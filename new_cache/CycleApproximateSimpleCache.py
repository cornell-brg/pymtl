from new_pymtl  import *
from new_pmlib  import InValRdyBundle, OutValRdyBundle
from new_pmlib  import mem_msgs
from new_pmlib.mem_msgs import MemReqParams, MemRespParams
from new_pmlib.mem_msgs import MemReqFromBits, MemRespFromBits
from new_pmlib.mem_msgs import MemReqToBits, MemRespToBits
from math import log

STATE_READY = 0
STATE_HIT = 1
STATE_READ = 2
STATE_EVICT = 3
STATE_COMPLETE = 4 
  
class CL_Cache( Model ):
  
  def __init__( s , line_nbytes = 16, cache_nlines = 16, n_ways = 1
  ,address_nbits = 32, data_nbits = 32, hit_penalty = 0, miss_penalty = 0):
  
    s.creq_params = MemReqParams(address_nbits, data_nbits)
    s.memreq_params = MemReqParams(address_nbits, line_nbytes*8)
    s.cresp_params = MemRespParams(data_nbits)
    s.memresp_params = MemRespParams(line_nbytes*8)
    
    #Val Ready Cache
    s.cachereq = InValRdyBundle(s.creq_params.nbits)
    s.cacheresp = OutValRdyBundle(s.cresp_params.nbits)
      
    #Val Ready Mem
    s.memresp = InValRdyBundle(s.memresp_params.nbits)
    s.memreq = OutValRdyBundle(s.memreq_params.nbits)
    
    
    
    s.address_nbits = address_nbits
    s.data_nbits = data_nbits
    s.line_nbytes = line_nbytes
    s.n_ways = n_ways
    s.n_sets = (cache_nlines)/(n_ways)
      
    #Set index accesses for pieces of address
    s.offset_start = 0
    s.offset_end = int(log(line_nbytes,2))
    s.n_sets_start = s.offset_end
    s.n_sets_end = int(s.n_sets_start + log(s.n_sets,2))
    s.tag_start = s.n_sets_end
    s.tag_end = address_nbits
      
    s.cachelines = [[Bits(line_nbytes*8) for j in xrange(n_ways)] for i in xrange(s.n_sets)]
    s.taglines = [[Bits(s.tag_end-s.tag_start) for i in range(n_ways)] for j in range(s.n_sets)]
    s.dirty_bits = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.valid_bits = [[False for i in range(n_ways)] for j in range(s.n_sets)]
    s.arbitration = [0] * s.n_sets
    
    s.miss_penalty = miss_penalty
    s.hit_penalty = hit_penalty

  
  def line_trace( s ):
    return str(s.state) + " " + str(s.buffer) + " " + str(s.cacheresp.msg) + " In Rdy " + str(s.cachereq.rdy) + " In Val " + str(s.cachereq.val) + " Out Rdy " + str(s.cacheresp.rdy) + " Out Val " + str(s.cacheresp.val)

  def fake_stall ( s , penalty):
    if(s.stall_count < penalty):
      s.cachereq.rdy.next = 0
      s.cacheresp.val.next = 0
      s.memresp.rdy.next = 0
      s.memreq.val.next = 0
      return True
    else:
      return False
    
  def elaborate_logic( s ):
    
  #Shorter Names
    rd = s.memreq_params.type_read
    wr = s.memreq_params.type_write
    
    s.stall_count = 0
    s.state = STATE_READY
    s.buffer = Bits(s.creq_params.nbits,value = 0)
    s.buffer_full = False
    
    @s.tick
    def logic():
      in_go = s.cachereq.val and s.cachereq.rdy
      out_go = s.cacheresp.val and s.cacheresp.rdy
      
      
      
      if out_go:
        s.buffer_full = False
        s.state = STATE_READY
        
      if in_go and s.state == STATE_READY:
        s.buffer.value = s.cachereq.msg
        s.buffer_full = True
        
        
      s.cachereq.rdy.next = 0
      s.cacheresp.val.next = 0
      s.memresp.rdy.next = 0
      s.memreq.val.next = 0
    
      (type,addr,length,data) = s.creq_params.unpck_req(s.buffer)
      tag = addr[s.tag_start:s.tag_end].uint()
      set = addr[s.n_sets_start:s.n_sets_end].uint()
      offset = addr[s.offset_start:s.offset_end].uint()*8
      length = length.uint()
      
      l = length
      if(length == 0):
        length = s.data_nbits / 8
      length = length * 8
    
      dset = s.dirty_bits[set]
      curr_set_tags = s.taglines[set]
      curr_set_valid_bits = s.valid_bits[set]
      
      
      if(s.state == STATE_READY): 
        s.cachereq.rdy.next = 1
        if(s.buffer_full):
          s.curr_way = 0
          s.cachereq.rdy.next = 0
          cacheline = None
          
      #Search Tag Array First
          while(s.curr_way < len(curr_set_tags)):
            if(tag == curr_set_tags[s.curr_way] and curr_set_valid_bits[s.curr_way]):
              cacheline = s.cachelines[set][s.curr_way]
              break
            s.curr_way = s.curr_way + 1
          
          if(cacheline == None):
            s.sent_mem = False

            if(s.dirty_bits[set][s.arbitration[set]]):
              s.state = STATE_EVICT
            else:
              s.state = STATE_READ
              
          else:
            if(not s.fake_stall(s.hit_penalty)): 
              if(type == rd):
                s.state = STATE_COMPLETE
              elif(type == wr):
                cacheline[offset:offset+length].value = Bits(length,value=data,trunc = True).value
                s.state = STATE_COMPLETE
              s.stall_count = 0
                
      if(s.state == STATE_EVICT):
        if(not s.sent_mem):
          s.curr_way = s.arbitration[set]
          eaddr = Bits(s.address_nbits)
          eaddr[s.offset_start:s.offset_end].value = 0
          eaddr[s.n_sets_start:s.n_sets_end].value = set
          eaddr[s.tag_start:s.tag_end].value = s.taglines[set][s.curr_way]
          s.memreq.val.next = 1
          s.memreq.msg.value = s.memreq_params.mk_req(wr,eaddr,0,s.cachelines[set][s.curr_way])
          if(s.miss_penalty == 0):
            s.memresp.rdy.next = 1
          if(s.memreq.rdy and s.memreq.val):
            s.memreq.val.next = 0
            s.sent_mem = True
            
            
        if(s.sent_mem):
          if(s.fake_stall(s.miss_penalty)):
            if(s.stall_count == s.miss_penalty):
              s.memresp.rdy.next = 1
          else:
            s.memresp.rdy.next = 1
            if(s.memresp.val and s.memresp.rdy):
              s.memresp.rdy.next = 0
              s.state = STATE_READ
              s.sent_mem = False
              s.stall_count = 0
      
      if(s.state == STATE_READ):
        if(not s.sent_mem):
          s.curr_way = s.arbitration[set]
          eaddr = (addr >> s.offset_end) << (s.offset_end)
          s.memreq.val.next = 1
          
          if(s.miss_penalty == 0):
            s.memresp.rdy.next = 1
          s.memreq.msg.value = s.memreq_params.mk_req(rd,eaddr,0,0)
          
          if(s.memreq.rdy and s.memreq.val):
            s.sent_mem = True
            s.memreq.val.next = 0
        
        if(s.sent_mem):
          if(s.stall_count < s.miss_penalty):
            s.stall_count = s.stall_count + 1
            if(s.stall_count == s.miss_penalty):
              s.memresp.rdy.next = 1
          else:
            s.memresp.rdy.next = 1
            if(s.memresp.val and s.memresp.rdy):
              s.memresp.rdy.next = 0
              (rtype, rlen, rdata) = s.memresp_params.unpck_resp(s.memresp.msg.value)
              
              s.cachelines[set][s.curr_way].value = rdata.uint()
              s.taglines[set][s.curr_way] = (addr >> s.tag_start)
              
              s.valid_bits[set][s.curr_way] = True
              if(type == wr):
                s.cachelines[set][s.curr_way][offset:offset+length].value = data[0:length].value
                s.dirty_bits[set][s.curr_way] = True
              elif(type == rd):
                s.dirty_bits[set][s.curr_way] = False
              s.state = STATE_COMPLETE
              s.sent_mem = False
              s.stall_count = 0
              
      if(s.state == STATE_COMPLETE):
        s.stall_count = 0
        s.cacheresp.msg.next = s.cresp_params.mk_resp(type,l,
        s.cachelines[set][s.curr_way][offset:offset+length])
        s.cacheresp.val.next = 1
        print s.cacheresp.rdy, s.cacheresp.rdy.next
        if(s.cacheresp.rdy):
          print "hello"
          s.cachereq.rdy.next = 1
          s.arbitration[set] = (s.curr_way + 1) % s.n_ways
          s.buffer_full = False
        