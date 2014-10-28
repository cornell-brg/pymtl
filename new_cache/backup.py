from pymtl          import *
from new_pmlib          import InValRdyBundle, OutValRdyBundle
from new_pmlib          import mem_msgs

from new_pmlib.mem_msgs import MemReqParams, MemRespParams
from new_pmlib.mem_msgs import MemReqFromBits, MemRespFromBits
from new_pmlib.mem_msgs import MemReqToBits, MemRespToBits

from math               import log

STATE_READY    = 0
STATE_HIT      = 1
STATE_READ     = 2
STATE_EVICT    = 3
STATE_COMPLETE = 4 
  
class CL_Cache( Model ):
  
  def __init__( s , line_nbytes = 16, cache_nlines = 16, n_ways = 1,  \
               address_nbits = 32, data_nbits = 32, hit_penalty = 10, \
               miss_penalty = 10):
  
    s.creq_params    = MemReqParams(address_nbits, data_nbits)
    s.memreq_params  = MemReqParams(address_nbits, line_nbytes*8)
    s.cresp_params   = MemRespParams(data_nbits)
    s.memresp_params = MemRespParams(line_nbytes*8)
    
    #Val Ready Cache
    s.cachereq  = InValRdyBundle(s.creq_params.nbits)
    s.cacheresp = OutValRdyBundle(s.cresp_params.nbits)
      
    #Val Ready Mem
    s.memresp   = InValRdyBundle(s.memresp_params.nbits)
    s.memreq    = OutValRdyBundle(s.memreq_params.nbits)
    
    
    
    s.address_nbits = address_nbits
    s.data_nbits    = data_nbits
    s.line_nbytes   = line_nbytes
    s.n_ways        = n_ways
    s.n_sets        = (cache_nlines)/(n_ways)
      
    #Set index accesses for pieces of address
    s.offset_start = 0
    s.offset_end   = int(log(line_nbytes,2))
    s.sets_start   = s.offset_end
    s.sets_end     = int(s.sets_start + log(s.n_sets,2))
    s.tag_start    = s.sets_end
    s.tag_end      = address_nbits
      
    s.cachelines  = [[Bits(line_nbytes*8) for j in xrange(n_ways)] \
                      for i in xrange(s.n_sets)]
    s.taglines    = [[Bits(s.tag_end-s.tag_start) for i in range(n_ways)] \
                      for j in range(s.n_sets)]
    s.dirty_bits  = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.valid_bits  = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.arbitration = [0] * s.n_sets
    
    s.miss_penalty = miss_penalty
    s.hit_penalty  = hit_penalty

  
  def line_trace( s ):
    #TODO clean up and provide more useful info
    return str(s.state) + " " + str(s.buffer) + " " + str(s.cacheresp.msg) + " In Rdy " + str(s.cachereq.rdy) + " In Val " + str(s.cachereq.val) + " Out Rdy " + str(s.cacheresp.rdy) + " Out Val " + str(s.cacheresp.val)

  def fake_stall ( s , penalty):
    if(s.stall_count < penalty):
      s.stall_count        = s.stall_count + 1
      s.cachereq.rdy.next  = 0
      s.cacheresp.val.next = 0
      s.memresp.rdy.next   = 0
      s.memreq.val.next    = 0
      return True
    else:
      return False
    
  def elaborate_logic( s ):
    
    #Shorter Names
    rd = s.memreq_params.type_read
    wr = s.memreq_params.type_write
    
    s.stall_count = 0
    s.state       = STATE_READY
    s.buffer      = Bits(s.creq_params.nbits,value = 0)
    s.buffer_full = False
    s.addr        = Bits(s.creq_params.addr_nbits)
    s.ilength     = Bits(s.creq_params.len_nbits)
    s.length      = Bits(s.creq_params.data_nbits)
    s.type        = Bits(s.creq_params.type_nbits)
    s.data        = Bits(s.creq_params.data_nbits)
    s.rdata       = Bits(s.memresp_params.data_nbits) #data read from memory
    s.curr_way    = Bits(s.n_ways)
    s.sent_mem    = False
    s.eaddr       = Bits(s.address_nbits) #address to memory
    s.set         = Bits(s.n_sets,value = 0)
    s.offset      = Bits((s.offset_end-s.offset_start)*8, value = 0)
    s.tag         = Bits(s.tag_end-s.tag_start,value = 0)
    @s.tick
    def logic():
    
      in_go  = s.cachereq.val  and s.cachereq.rdy
      out_go = s.cacheresp.val and s.cacheresp.rdy  
      
      if out_go:
        s.buffer_full = False
        s.state       = STATE_READY
        
      if in_go and s.state == STATE_READY:
        s.buffer.value = s.cachereq.msg
        s.buffer_full  = True
        
      #Set default values to be changed based on state
      s.cachereq.rdy.next  = 0
      s.cacheresp.val.next = 0
      s.memresp.rdy.next   = 0
      s.memreq.val.next    = 0
      
      s.type.value    = s.buffer[s.creq_params.type_slice]
      s.ilength.value = s.buffer[s.creq_params.len_slice]
      s.addr.value    = s.buffer[s.creq_params.addr_slice]
      s.data.value    = s.buffer[s.creq_params.data_slice]      
      
      s.tag.value    = s.addr[s.tag_start:s.tag_end]
      s.set.value    = s.addr[s.sets_start:s.sets_end]
      s.offset.value = s.addr[s.offset_start:s.offset_end]*8
      s.length.value = s.ilength
      
      if s.length == 0:
        s.length.value = s.data_nbits / 8
        
      s.length.value = s.length * 8
      
      if s.state == STATE_READY: 
        s.cachereq.rdy.next = 1
        
        if s.buffer_full:
          s.curr_way.value    = 0
          s.cachereq.rdy.next = 0
          
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
                s.cachelines[s.set][s.curr_way] \
                  [s.offset:s.offset+s.length].value = s.data[0:s.length]
                  
                s.state = STATE_COMPLETE
                
              s.stall_count = 0
                
      if(s.state == STATE_EVICT):
      
        if(not s.sent_mem):
          s.curr_way.value                           = s.arbitration[s.set]
          s.eaddr[s.offset_start:s.offset_end].value = 0
          s.eaddr[s.sets_start:s.sets_end].value     = s.set
          s.eaddr[s.tag_start:s.tag_end].value       = s.taglines[s.set][s.curr_way]
          
          s.memreq.val.next                                = 1
          s.memreq.msg[ s.memreq_params.type_slice ].value = wr
          s.memreq.msg[ s.memreq_params.addr_slice ].value = s.eaddr
          s.memreq.msg[ s.memreq_params.len_slice  ].value = 0
          s.memreq.msg[ s.memreq_params.data_slice ].value = s.cachelines[s.set][s.curr_way]
          
          if s.miss_penalty == 0:
            s.memresp.rdy.next = 1
            
          if s.memreq.rdy and s.memreq.val:
            s.memreq.val.next = 0
            s.sent_mem        = True
            
            
        if s.sent_mem:
        
          if s.fake_stall(s.miss_penalty):
          
            if s.stall_count == s.miss_penalty:
              s.memresp.rdy.next = 1
              
          else:
            s.memresp.rdy.next = 1
            
            if s.memresp.val and s.memresp.rdy:
              s.memresp.rdy.next = 0
              s.state            = STATE_READ
              s.sent_mem         = False
              s.stall_count      = 0
      
      if s.state == STATE_READ:      
        if not s.sent_mem:
          s.curr_way.value = s.arbitration[s.set]
          s.eaddr = (s.addr >> s.offset_end) << (s.offset_end)
          s.memreq.val.next = 1
          
          if s.miss_penalty == 0:
            s.memresp.rdy.next = 1
            
          s.memreq.msg[ s.memreq_params.type_slice ].value = rd
          s.memreq.msg[ s.memreq_params.addr_slice ].value = s.eaddr
          s.memreq.msg[ s.memreq_params.len_slice  ].value = 0
          s.memreq.msg[ s.memreq_params.data_slice ].value = 0
          
          if s.memreq.rdy and s.memreq.val:
            s.sent_mem        = True
            s.memreq.val.next = 0
        
        if s.sent_mem:        
          if s.stall_count < s.miss_penalty:
            s.stall_count = s.stall_count + 1
            
            if s.stall_count == s.miss_penalty:
              s.memresp.rdy.next = 1
              
          else:
            s.memresp.rdy.next = 1
            
            if s.memresp.val and s.memresp.rdy:
              s.memresp.rdy.next = 0
              s.rdata.value = s.memresp.msg[s.memresp_params.data_slice]
              
              s.cachelines[s.set][s.curr_way].value = s.rdata
              s.taglines[s.set][s.curr_way].value = (s.addr >> s.tag_start)
              
              s.valid_bits[s.set][s.curr_way] = True
              
              if s.type == wr:
                s.cachelines[s.set][s.curr_way] \
                  [s.offset:s.offset+s.length].value = s.data[0:s.length]
                s.dirty_bits[s.set][s.curr_way] = True
                
              elif s.type == rd:
                s.dirty_bits[s.set][s.curr_way] = False
                
              s.state = STATE_COMPLETE
              s.sent_mem = False
              s.stall_count = 0
              
      if s.state == STATE_COMPLETE:
        s.stall_count = 0
        
        s.cacheresp.msg[ s.cresp_params.type_slice ].next = s.type
        s.cacheresp.msg[ s.cresp_params.len_slice  ].next = s.ilength
        s.cacheresp.msg[ s.cresp_params.data_slice ].next = \
          s.cachelines[s.set][s.curr_way][s.offset:s.offset+s.length]
        s.cacheresp.val.next = 1
        
        if s.cacheresp.rdy:
          s.cachereq.rdy.next = 1
          s.arbitration[s.set] = (s.curr_way + 1) % s.n_ways
          s.buffer_full = False
        
