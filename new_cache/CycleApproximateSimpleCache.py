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
  
class CycleApproximateSimpleCache( Model ):
  
  def __init__( s , byte_size = 256, cacheline_size = 16, ways = 8
  ,address_size = 32, data_size = 32, hit_time = 0, miss_time = 10):
    s.byte_size = byte_size
    s.address_size = 32
    s.data_size = data_size / 8
    s.cacheline_size = cacheline_size
    s.ways = ways
    s.sets = byte_size/(ways*cacheline_size)
    s.cachelines = [[Bits(cacheline_size*8) for j in xrange(ways)] for i in xrange(s.sets)]
    
    s.offset_start = 0
    s.offset_end = int(log(cacheline_size,2))
    s.sets_start = s.offset_end
    s.sets_end = int(s.sets_start + log(s.sets,2))
    s.tag_starts = s.sets_end
    s.tag_ends = address_size
    
    s.taglines = [[0 for i in range(ways)] for j in range(s.sets)]
    s.creq_params = MemReqParams(address_size, data_size)
    s.memreq_params = MemReqParams(address_size, cacheline_size*8)
    s.cresp_params = MemRespParams(data_size)
    s.memresp_params = MemRespParams(cacheline_size*8)
    
    s.dirty_bits = [[False for i in range(ways)] for j in range(s.sets)]
    s.valid_bits = [[False for i in range(ways)] for j in range(s.sets)]
    s.arbitration = [0] * s.sets
    
    s.miss_time = miss_time
    s.hit_time = hit_time
    
    s.in_src = InValRdyBundle(s.creq_params.nbits)
    s.out_sink = OutValRdyBundle(s.cresp_params.nbits)
    
    s.in_mem = InValRdyBundle(s.memresp_params.nbits)
    s.out_mem = OutValRdyBundle(s.memreq_params.nbits)
  
  def line_trace( s ):
    return str(s.state) + " " + str(s.buffer) + " " + str(s.out_sink.msg)
    
  def elaborate_logic( s ):
    
    s.req_src = MemReqFromBits(s.creq_params)
    s.resp_sink = MemRespToBits(s.cresp_params)
    s.req_mem = MemReqToBits(s.memreq_params)
    s.resp_mem = MemRespFromBits(s.memresp_params)
    
    rd = s.memreq_params.type_read
    wr = s.memreq_params.type_write
    
    s.count = 0
    s.state = STATE_READY
    s.buffer = 0
    s.buffer_full = False
    
    s.connect(s.req_src.bits,s.buffer)
    
    @s.tick
    def logic():
      in_go = s.in_src.val and s.in_src.rdy
      out_go = s.out_sink.val and s.out_sink.rdy
      
      s.in_src.rdy.next = 0
      s.out_sink.val.next = 0
      s.in_mem.rdy.next = 0
      s.out_mem.val.next = 0
      if out_go:
        s.buffer_full = False
        
      if in_go:
        s.buffer = s.in_src.msg.uint()
        s.buffer_full = True
      
      (type,addr,length,data) = s.creq_params.unpck_req(s.buffer)
      tag = addr[s.tag_starts:s.tag_ends].uint()
      set = addr[s.sets_start:s.sets_end].uint()
      offset = addr[s.offset_start:s.offset_end].uint()*8
      data = data.uint()
      length = length.uint()
      l = length
      if(length == 0):
        length = s.data_size
      length = length * 8
      type = type.uint()
      dset = s.dirty_bits[set]
      tset = s.taglines[set]
      vset = s.valid_bits[set]
      
      if(s.state == STATE_READY): 
        s.in_src.rdy.next = 1
        if(s.buffer_full):
          s.ct = 0
          s.in_src.rdy.next = 0
          cacheline = None
          
          while(s.ct < len(tset)):
            if(tag == tset[s.ct] and vset[s.ct]):
              cacheline = s.cachelines[set][s.ct]
              break
            s.ct = s.ct + 1
          
          if(cacheline == None):
            s.sent_mem = False

            if(s.dirty_bits[set][s.arbitration[set]]):
              s.state = STATE_EVICT
            else:
              s.state = STATE_READ
              
          else:
            if(s.count < s.hit_time):
              s.count = s.count + 1
            else:  
              if(type == rd):
                s.state = STATE_COMPLETE
              elif(type == wr):
                cacheline[offset:offset+length] = Bits(length,value=data,trunc = True)
                s.state = STATE_COMPLETE
                
      if(s.state == STATE_EVICT):
        if(not s.sent_mem):
          s.ct = s.arbitration[set]
          eaddr = Bits(s.address_size)
          eaddr[s.offset_start:s.offset_end].value = 0
          eaddr[s.sets_start:s.sets_end].value = set
          eaddr[s.tag_starts:s.tag_ends].value = s.taglines[set][s.ct]
          s.out_mem.val.next = 1
          s.out_mem.msg.value = s.memreq_params.mk_req(wr,eaddr,0,s.cachelines[set][s.ct])
          if(s.miss_time == 0):
            s.in_mem.rdy.next = 1
          if(s.out_mem.rdy and s.out_mem.val):
            s.out_mem.val.next = 0
            s.sent_mem = True
            
            
        if(s.sent_mem):
          if(s.count < s.miss_time):
            s.count = s.count + 1
            if(s.count == s.miss_time):
              s.in_mem.rdy.next = 1
          else:
            s.in_mem.rdy.next = 1
            if(s.in_mem.val and s.in_mem.rdy):
              s.in_mem.rdy.next = 0
              s.state = STATE_READ
              s.sent_mem = False
              s.count = 0
      
      if(s.state == STATE_READ):
        
        if(not s.sent_mem):
          s.ct = s.arbitration[set]
          eaddr = (addr >> s.offset_end) << (s.offset_end)
          s.out_mem.val.next = 1
          
          if(s.miss_time == 0):
            s.in_mem.rdy.next = 1
          s.out_mem.msg.value = s.memreq_params.mk_req(rd,eaddr,0,0)
          
          if(s.out_mem.rdy and s.out_mem.val):
            s.sent_mem = True
            s.out_mem.val.next = 0
        
        if(s.sent_mem):
          if(s.count < s.miss_time):
            s.count = s.count + 1
            if(s.count == s.miss_time):
              s.in_mem.rdy.next = 1
          else:
            s.in_mem.rdy.next = 1
            if(s.in_mem.val and s.in_mem.rdy):
              s.in_mem.rdy.next = 0
              (rtype, rlen, rdata) = s.memresp_params.unpck_resp(s.in_mem.msg.value)
              
              s.cachelines[set][s.ct].value = rdata.uint()
              s.taglines[set][s.ct] = (addr >> s.tag_starts)
              
              s.valid_bits[set][s.ct] = True
              if(type == wr):
                s.cachelines[set][s.ct][offset:offset+length] = data
                s.dirty_bits[set][s.ct] = True
              elif(type == rd):
                s.dirty_bits[set][s.ct] = False
              s.state = STATE_COMPLETE
              s.sent_mem = False
              s.count = 0
              
      if(s.state == STATE_COMPLETE):
        s.count = 0
        s.out_sink.msg.value = s.cresp_params.mk_resp(type,l,
        s.cachelines[set][s.ct][offset:offset+length])
        s.out_sink.val.value = 1
        if(s.out_sink.rdy and s.out_sink.val):
          s.in_src.rdy.next = 1
          s.state = STATE_READY
          s.out_sink.val.next = 0
          s.arbitration[set] = (s.ct + 1) % s.ways
        