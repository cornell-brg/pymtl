from new_pymtl          import *
from new_pmlib          import InValRdyBundle, OutValRdyBundle
from new_pmlib          import mem_msgs

from new_pmlib.mem_msgs import MemReqParams, MemRespParams
from new_pmlib.mem_msgs import MemReqFromBits, MemRespFromBits
from new_pmlib.mem_msgs import MemReqToBits, MemRespToBits

from math               import log
from math               import ceil

STATE_READY    = 0
STATE_HIT      = 1
STATE_READ     = 2
STATE_EVICT    = 3
STATE_COMPLETE = 4 
  
## (In a few places) HARD CODED FOR THE DEFAULT ARGUMENTS
#TODO rename and add headers
class CL_Cache( Model ):
  
  def __init__( s , line_nbytes = 16, cache_nlines = 16, n_ways = 1,  \
               address_nbits = 32, data_nbits = 32, hit_penalty = 0, \
               miss_penalty = 0):
    
    #Val Ready Cache
    s.creq_len = int(ceil(log(data_nbits/8, 2)))
    
    s.cachereq_msg_data = InPort(data_nbits)
    s.cachereq_msg_addr = InPort(address_nbits)
    s.cachereq_msg_len  = InPort(s.creq_len)
    s.cachereq_msg_type = InPort(1)
    s.cachereq_val      = InPort(1)
    s.cachereq_rdy      = OutPort(1)
    
    s.cacheresp_msg_data = OutPort(data_nbits)
    s.cacheresp_msg_len  = OutPort(s.creq_len)
    s.cacheresp_msg_type = OutPort(1)
    s.cacheresp_val      = OutPort(1)
    s.cacheresp_rdy      = InPort(1)
    
    #Val Ready Mem
    mdata_nbits = line_nbytes * 8
    s.mreq_len = int(ceil(log(line_nbytes, 2)))
    
    s.memreq_msg_data = [OutPort(32) for x in range(mdata_nbits/32)]
    s.memreq_msg_addr = OutPort(address_nbits)
    s.memreq_msg_len  = OutPort(s.mreq_len)
    s.memreq_msg_type = OutPort(1)
    s.memreq_val      = OutPort(1)
    s.memreq_rdy      = InPort(1)
    
    s.memresp_msg_data = [InPort(32) for x in range(mdata_nbits/32)]
    s.memresp_msg_len  = InPort(s.mreq_len)
    s.memresp_msg_type = InPort(1)
    s.memresp_val      = InPort(1)
    s.memresp_rdy      = OutPort(1)
    
    s.address_nbits = address_nbits
    s.data_nbits    = data_nbits
    s.line_nbytes   = line_nbytes
    s.n_ways        = n_ways
    s.n_sets        = (cache_nlines)/(n_ways)
      
    #Set index accesses for pieces of address
    s.offset_start = 0
    s.offset_end   = int(log(line_nbytes,2))
    s.set_start    = s.offset_end
    s.set_end      = int(s.set_start + log(s.n_sets,2))
    s.tag_start    = s.set_end
    s.tag_end      = address_nbits
      
    s.cachelines  = [[[Bits(32) for k in range(line_nbytes/4)] \
                      for j in range(n_ways)] \
                      for i in xrange(s.n_sets)]
    s.taglines    = [[Bits(32) for i in range(n_ways)] \
                      for j in range(s.n_sets)]
    s.dirty_bits  = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.valid_bits  = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.arbitration = [0] * s.n_sets
    
    s.miss_penalty = miss_penalty
    s.hit_penalty  = hit_penalty

  
  def line_trace( s ):
    #TODO clean up and provide more useful info
    #return str(s.state) + " " + str(s.buffer) + " " + str(s.cacheresp.msg) + " In Rdy " + str(s.cachereq.rdy) + " In Val " + str(s.cachereq.val) + " Out Rdy " + str(s.cacheresp.rdy) + " Out Val " + str(s.cacheresp.val)
    return "TODO"
  def fake_stall ( s , penalty):
    if(s.stall_count < penalty):
      s.stall_count        = s.stall_count + 1
      s.cachereq_rdy.next  = 0
      s.cacheresp_val.next = 0
      s.memresp_rdy.next   = 0
      s.memreq_val.next    = 0
      return True
    else:
      return False
  def rshift(s,val,n):
      return (val % 0x100000000) >> n
      
  def elaborate_logic( s ):
    
    #Shorter Names
    rd = 0
    wr = 1
    
    s.stall_count = 0
    s.state       = STATE_READY
    
    s.buffer_msg_data = Bits(s.data_nbits)
    s.buffer_msg_addr = Bits(s.address_nbits)
    s.buffer_msg_len  = Bits(s.creq_len)
    s.buffer_msg_type = Bits(1)
    s.buffer_full     = False
    
    s.addr        = Bits(s.address_nbits)
    s.ilength     = Bits(s.creq_len)
    s.length      = Bits(s.data_nbits)
    s.type        = Bits(1)
    s.data        = Bits(s.data_nbits)
    
    s.curr_way    = Bits(s.n_ways)
    s.sent_mem    = False
    s.eaddr       = Bits(s.address_nbits) #address to memory
    s.set         = Bits(s.n_sets,value = 0)
    s.word_offset = Bits(32, value = 0)
    s.byte_offset = Bits(32, value = 0)
    s.tag         = Bits(32,value = 0)
    
    
      
    @s.tick
    def logic():
    
      in_go  = s.cachereq_val  and s.cachereq_rdy
      out_go = s.cacheresp_val and s.cacheresp_rdy  
      
      if out_go:
        s.buffer_full = False
        s.state       = STATE_READY
        
      if in_go and s.state == STATE_READY:
        s.buffer_msg_data.value = s.cachereq_msg_data
        s.buffer_msg_addr.value = s.cachereq_msg_addr
        s.buffer_msg_len.value  = s.cachereq_msg_len
        s.buffer_msg_type.value = s.cachereq_msg_type
        s.buffer_full  = True
        
      #Set default values to be changed based on state
      s.cachereq_rdy.next  = 0
      s.cacheresp_val.next = 0
      s.memresp_rdy.next   = 0
      s.memreq_val.next    = 0
      
      s.type.value    = s.buffer_msg_type
      s.ilength.value = s.buffer_msg_len
      s.addr.value    = s.buffer_msg_addr
      s.data.value    = s.buffer_msg_data     
      
      s.tag.value    = s.rshift(s.addr,s.tag_start)
      s.set.value    = s.rshift(s.addr & ((1<<s.set_end)-1),s.set_start)
      s.word_offset.value = (s.addr & ((1<<s.offset_end)-1)) / 4
      s.byte_offset.value = (s.addr & ((1<<s.offset_end)-1)) % 4
      s.length.value = s.ilength
      
      if s.length == 0:
        s.length.value = s.data_nbits / 8
        
      s.length.value = s.length * 8
      
      if s.state == STATE_READY: 
        s.cachereq_rdy.next = 1
        
        if s.buffer_full:
          s.curr_way.value    = 0
          s.cachereq_rdy.next = 0
          
      #Search Tag Array First
          while s.curr_way.value < len(s.taglines[s.set]):
            if s.tag == s.taglines[s.set][s.curr_way] \
               and s.valid_bits[s.set][s.curr_way]:
              break
              
            s.curr_way.value = s.curr_way + 1
          
          #Tag not found
          if s.curr_way >= s.n_ways:
            s.sent_mem = False

            if(s.dirty_bits[s.set][s.arbitration[s.set]]):
              s.state = STATE_EVICT
              
            else:
              s.state = STATE_READ
              
          else:
            if(not s.fake_stall(s.hit_penalty)): 
            
              if(s.type == rd):              
                s.state = STATE_COMPLETE
                
              elif(s.type == wr):
                #TODO Support Bits Constructor in @s.tick
                #s.cachelines[s.set][s.curr_way.value][offset:offset+length].value = Bits(length,value=s.data.value,trunc = True).value
                assert not s.length == 0
                #TODO :( bits translatable
                s.cachelines[s.set][s.curr_way]                            \
                  [s.word_offset].value = (s.cachelines[s.set][s.curr_way] \
                    [s.word_offset] & (0xFFFFFFFF ^                        \
                    (((1 << s.length.uint()) - 1) <<                       \
                    (s.byte_offset.uint()*8)))) |                          \
                    ((s.data.uint() & ((1 << s.length.uint()) - 1)) <<     \
                    s.byte_offset.uint()*8)
                s.state = STATE_COMPLETE
                
              s.stall_count = 0
                
      if(s.state == STATE_EVICT):
      
        if(not s.sent_mem):
          s.curr_way.value = s.arbitration[s.set]
          s.eaddr.value = 0
          s.eaddr.value = (s.taglines[s.set][s.curr_way] << s.tag_start) | (s.set << s.set_start)
          
          s.memreq_val.next = 1
          s.memreq_msg_type.value = wr
          s.memreq_msg_addr.value = s.eaddr
          s.memreq_msg_len.value = 0
          s.memreq_msg_data[0].value = s.cachelines[s.set][s.curr_way][0]
          s.memreq_msg_data[1].value = s.cachelines[s.set][s.curr_way][1]
          s.memreq_msg_data[2].value = s.cachelines[s.set][s.curr_way][2]
          s.memreq_msg_data[3].value = s.cachelines[s.set][s.curr_way][3]
          
          
          if s.miss_penalty == 0:
            s.memresp_rdy.next = 1
            
          if s.memreq_rdy and s.memreq_val:
            s.memreq_val.next = 0
            s.sent_mem        = True
            
            
        if s.sent_mem:
        
          if s.fake_stall(s.miss_penalty):
          
            if s.stall_count == s.miss_penalty:
              s.memresp_rdy.next = 1
              
          else:
            s.memresp_rdy.next = 1
            
            if s.memresp_val and s.memresp_rdy:
              s.memresp_rdy.next = 0
              s.state            = STATE_READ
              s.sent_mem         = False
              s.stall_count      = 0
      
      if s.state == STATE_READ:      
        if not s.sent_mem:
          s.curr_way.value = s.arbitration[s.set]
          s.eaddr = (s.addr >> s.offset_end) << (s.offset_end)
          s.memreq_val.next = 1
          
          if s.miss_penalty == 0:
            s.memresp_rdy.next = 1
            
          s.memreq_msg_type.value = rd

          s.memreq_msg_addr.value = s.eaddr
          s.memreq_msg_len.value = 0
          s.memreq_msg_data[0].value = 0
          s.memreq_msg_data[1].value = 0
          s.memreq_msg_data[2].value = 0
          s.memreq_msg_data[3].value = 0
          if s.memreq_rdy and s.memreq_val:
            s.sent_mem        = True
            s.memreq_val.next = 0
        
        if s.sent_mem:   
          if s.stall_count < s.miss_penalty:
            s.stall_count = s.stall_count + 1
            
            if s.stall_count == s.miss_penalty:
              s.memresp_rdy.next = 1
              
          else:
            s.memresp_rdy.next = 1
            
            if s.memresp_val and s.memresp_rdy:
              s.memresp_rdy.next = 0
              s.cachelines[s.set][s.curr_way][0].value = s.memresp_msg_data[0]
              s.cachelines[s.set][s.curr_way][1].value = s.memresp_msg_data[1]
              s.cachelines[s.set][s.curr_way][2].value = s.memresp_msg_data[2]
              s.cachelines[s.set][s.curr_way][3].value = s.memresp_msg_data[3]
              
              s.taglines[s.set][s.curr_way].value = (s.addr >> s.tag_start)
              
              s.valid_bits[s.set][s.curr_way] = True
              
              if s.type == wr:
                s.cachelines[s.set][s.curr_way]                            \
                  [s.word_offset].value = (s.cachelines[s.set][s.curr_way] \
                    [s.word_offset] & (0xFFFFFFFF ^                        \
                    (((1 << s.length.uint()) - 1) <<                       \
                    (s.byte_offset.uint()*8)))) |                          \
                    ((s.data.uint() & ((1 << s.length.uint()) - 1)) <<     \
                    s.byte_offset.uint()*8)
                s.dirty_bits[s.set][s.curr_way] = True
                
              elif s.type == rd:
                s.dirty_bits[s.set][s.curr_way] = False
                
              s.state = STATE_COMPLETE
              s.sent_mem = False
              s.stall_count = 0
              
      if s.state == STATE_COMPLETE:
        s.stall_count = 0
        
        s.cacheresp_msg_type.next = s.type
        s.cacheresp_msg_len.next  = s.ilength
        s.cacheresp_msg_data.next =                                   \
          s.rshift(s.cachelines[s.set][s.curr_way][s.word_offset] &   \
          (((1 << s.length.uint()) - 1) << (s.byte_offset.uint()*8)), \
          (s.byte_offset.uint()*8))
        s.cacheresp_val.next = 1

        if s.cacheresp_rdy:
          s.cachereq_rdy.next = 1
          s.arbitration[s.set] = (s.curr_way + 1) % s.n_ways
          s.buffer_full = False
        