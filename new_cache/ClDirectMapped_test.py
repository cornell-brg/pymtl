#=======================================================================
# DirectMapped_test.py for CL
#=======================================================================

from pymtl import *
from new_pmlib import TestSource, TestSink

from CycleApproximateSimpleCache import CL_Cache
from TestCacheResp32Sink         import TestCacheResp32Sink
from new_pmlib.TestMemory        import TestMemory

import new_pmlib.mem_msgs as mem_msgs

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay, mem_delay,
                mem_nbytes, addr_nbits, data_nbits, line_nbits ):

    s.creq_params  = mem_msgs.MemReqParams ( addr_nbits, data_nbits )
    s.cresp_params = mem_msgs.MemRespParams( data_nbits )

    s.mreq_params  = mem_msgs.MemReqParams ( addr_nbits, line_nbits )
    s.mresp_params = mem_msgs.MemRespParams( line_nbits )

    # Instantiate models

    s.src   = TestSource( s.creq_params.nbits, src_msgs,  0 )
    s.cache = CL_Cache()
    s.mem   = TestMemory( s.mreq_params, s.mresp_params, 1, 0 )
    s.sink  = TestCacheResp32Sink(  s.cresp_params, sink_msgs, 0 )

    s.out_data  = InPort(s.mreq_params.data_nbits)
    s.in_data  = InPort(s.mreq_params.data_nbits)
    
  def elaborate_logic( s ):
    s.connect( s.src.out.msg[s.creq_params.type_slice], s.cache.cachereq_msg_type)
    s.connect( s.src.out.msg[s.creq_params.addr_slice], s.cache.cachereq_msg_addr)
    s.connect( s.src.out.msg[s.creq_params.data_slice], s.cache.cachereq_msg_data)
    s.connect( s.src.out.msg[s.creq_params.len_slice], s.cache.cachereq_msg_len)
    s.connect( s.src.out.val, s.cache.cachereq_val)
    s.connect( s.src.out.rdy, s.cache.cachereq_rdy)
    
    
    for x in range(len(s.cache.memreq_msg_data)):
      s.connect( s.cache.memreq_msg_data[x],  s.out_data[x*32:(x+1)*32])
      
    s.connect( s.cache.memreq_msg_addr,  s.mem.reqs[0].msg[s.mreq_params.addr_slice])
    s.connect( s.cache.memreq_msg_len,   s.mem.reqs[0].msg[s.mreq_params.len_slice])
    s.connect( s.cache.memreq_msg_type,  s.mem.reqs[0].msg[s.mreq_params.type_slice])
    s.connect( s.cache.memreq_rdy, s.mem.reqs[0].rdy)
    s.connect( s.cache.memreq_val, s.mem.reqs[0].val)
    
    
    
    for x in range(len(s.cache.memreq_msg_data)):
      s.connect(s.cache.memresp_msg_data[x], s.in_data[x*32:(x+1)*32])
    
    s.connect( s.cache.memresp_msg_len,   s.mem.resps[0].msg[s.mresp_params.len_slice])
    s.connect( s.cache.memresp_msg_type,  s.mem.resps[0].msg[s.mresp_params.type_slice])
    s.connect( s.cache.memresp_rdy, s.mem.resps[0].rdy)
    s.connect( s.cache.memresp_val, s.mem.resps[0].val)
    
    s.connect( s.sink.in_.msg[s.cresp_params.type_slice], s.cache.cacheresp_msg_type)
    s.connect( s.sink.in_.msg[s.cresp_params.data_slice], s.cache.cacheresp_msg_data)
    s.connect( s.sink.in_.msg[s.cresp_params.len_slice], s.cache.cacheresp_msg_len)
    s.connect( s.sink.in_.val, s.cache.cacheresp_val)
    s.connect( s.sink.in_.rdy, s.cache.cacheresp_rdy)
    
    
    #TODO moving these assignments above using s.connect instead caused problems
    @s.combinational
    def logic():
      s.mem.reqs[0].msg[s.mreq_params.data_slice].value = s.out_data
      s.in_data.value = s.mem.resps[0].msg[s.mresp_params.data_slice]

  def done( s ):

    done = s.src.done.value and s.sink.done.value
    return done

  def line_trace( s ):
    return s.cache.line_trace() + " " + s.sink.line_trace()

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache Unit Test
#-------------------------------------------------------------------------

def run_SimpleCache_test( dump_vcd, vcd_file_name,
                          src_delay, sink_delay, mem_delay ):

  # Parameters

  addr_nbits =  32
  data_nbits =  32
  line_nbits = 128
  mem_nbytes = 256

  # Syntax Helpers

  memreq_params  = mem_msgs.MemReqParams ( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  req  = memreq_params.mk_req
  resp = memresp_params.mk_resp

  rd = memreq_params.type_read
  wr = memreq_params.type_write

  def mk_req( type_, addr, len_, data ):
    return req( type_, addr, len_, data )

  def mk_resp( type_, len_, data ):
    return resp( type_, len_, data )

  # Test Msgs

  test_msgs = [

    # ----------------------------------------  --------------------------------
    #             Memory Request                        Memory Response
    # ----------------------------------------  --------------------------------
    #       type  addr        len data                   type  len  data

    #-----------------------------------------------------------------------
    # Throw Away tests
    #-----------------------------------------------------------------------
    #Tests 1-3
    mk_req( rd,   0x000fff00, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeef ),
    mk_req( wr,   0x000fff00, 0,  0xaaaa0000 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x000fff00, 0,  0x00000000 ), mk_resp( rd,   0,   0xaaaa0000 ),

    # Simple Test, write word and read word back
    #Tests 4-5
    mk_req( wr,   0x00000000, 0,  0x0a0a0a0a ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x00000000, 0,  0x00000000 ), mk_resp( rd,   0,   0x0a0a0a0a ),

    # Write to valid cache line, make sure all words are hits
    #Tests 6-11
    mk_req( wr,   0x00000004, 0,  0x0b0b0b0b ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x00000008, 0,  0x0c0c0c0c ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x0000000c, 0,  0x0d0d0d0d ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x00000004, 0,  0x00000000 ), mk_resp( rd,   0,   0x0b0b0b0b ),
    mk_req( rd,   0x00000008, 0,  0x00000000 ), mk_resp( rd,   0,   0x0c0c0c0c ),
    mk_req( rd,   0x0000000c, 0,  0x00000000 ), mk_resp( rd,   0,   0x0d0d0d0d ),

    # Evict cache line, write to refill line, read word back
    #Tests 12-15
    mk_req( wr,   0x0000ff08, 0,  0xdeadbeef ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ff08, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeef ),
    mk_req( wr,   0x0000ff04, 0,  0xff00ff00 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ff04, 0,  0x00000000 ), mk_resp( rd,   0,   0xff00ff00 ),

    # Refill a new cache line
    #Tests 16-19
    mk_req( wr,   0x0000ab20, 0,  0xabcdefff ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ab20, 0,  0x00000000 ), mk_resp( rd,   0,   0xabcdefff ),
    mk_req( wr,   0x0000ab2c, 0,  0x01234567 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ab2c, 0,  0x00000000 ), mk_resp( rd,   0,   0x01234567 ),

    # Make sure old line is still hitting
    #Tests 20-21
    mk_req( rd,   0x0000ff08, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeef ),
    mk_req( rd,   0x0000ff04, 0,  0x00000000 ), mk_resp( rd,   0,   0xff00ff00 ),

    # Read the evicted line, make sure data was written back
    #Tests 22-25
    mk_req( rd,   0x00000000, 0,  0x00000000 ), mk_resp( rd,   0,   0x0a0a0a0a ),
    mk_req( rd,   0x00000004, 0,  0x00000000 ), mk_resp( rd,   0,   0x0b0b0b0b ),
    mk_req( rd,   0x00000008, 0,  0x00000000 ), mk_resp( rd,   0,   0x0c0c0c0c ),
    mk_req( rd,   0x0000000c, 0,  0x00000000 ), mk_resp( rd,   0,   0x0d0d0d0d ),

    # Test byte accesses
    #Tests 26-33
    mk_req( wr,   0x00000008, 0,  0x0a0b0c0d ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x00000008, 1,  0xdeadbeef ), mk_resp( wr,   1,   0x00000000 ),
    mk_req( rd,   0x00000008, 1,  0x00000000 ), mk_resp( rd,   1,   0x000000ef ),
    mk_req( rd,   0x00000009, 1,  0x00000000 ), mk_resp( rd,   1,   0x0000000c ),
    mk_req( rd,   0x0000000a, 1,  0x00000000 ), mk_resp( rd,   1,   0x0000000b ),
    mk_req( rd,   0x0000000b, 1,  0x00000000 ), mk_resp( rd,   1,   0x0000000a ),
    mk_req( wr,   0x0000000a, 1,  0x000000ff ), mk_resp( wr,   1,   0x00000000 ),
    mk_req( rd,   0x00000008, 0,  0x00000000 ), mk_resp( rd,   0,   0x0aff0cef ),

    # Test halfword accesses

    mk_req( wr,   0x0000000c, 0,  0x01020304 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x0000000c, 2,  0xdeadbeef ), mk_resp( wr,   2,   0x00000000 ),
    mk_req( rd,   0x0000000c, 2,  0x00000000 ), mk_resp( rd,   2,   0x0000beef ),
    mk_req( rd,   0x0000000e, 2,  0x00000000 ), mk_resp( rd,   2,   0x00000102 ),
    mk_req( wr,   0x0000000e, 2,  0x0000d00d ), mk_resp( wr,   2,   0x00000000 ),
    mk_req( rd,   0x0000000c, 0,  0x00000000 ), mk_resp( rd,   0,   0xd00dbeef ),

  ]

  # src/sink msgs

  src_msgs  = test_msgs[::2]
  sink_msgs = test_msgs[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( src_msgs, sink_msgs, src_delay, sink_delay,
                       mem_delay, mem_nbytes, addr_nbits, data_nbits,
                       line_nbits )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  # Reset

  sim.reset()

  #-----------------------------------------------------------------------
  # Throw away test initializations
  #-----------------------------------------------------------------------
  # Intialize cache line 0
  # You can initialize more locations here

  model.cache.valid_bits[ 0 ][ 0 ] = True
  model.cache.dirty_bits[ 0 ][ 0 ] = False

  model.cache.taglines[ 0 ][ 0 ] = Bits(24,value=0xFFF)
  model.cache.cachelines[ 0 ][ 0 ][ 3 ] = \
    Bits(32,value=0xdeadbeec)
  model.cache.cachelines[ 0 ][ 0 ][ 2 ] = \
    Bits(32,value=0xdeadbeed)
  model.cache.cachelines[ 0 ][ 0 ][ 1 ] = \
    Bits(32,value=0xdeadbeee)
  model.cache.cachelines[ 0 ][ 0 ][ 0 ] = \
    Bits(32,value=0xdeadbeef)


  # Begin Simulation

  while not model.done():
    #print "OUT_DATA", model.out_data
    #print "IN_DATA", model.in_data
    #print "MEMORY REQ", model.mem.reqs[0]
    #print "MEMORY RESP", model.mem.resps[0]
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()
  sim.cycle()

import pytest
@pytest.mark.xfail
def test_cache( dump_vcd ):
  run_SimpleCache_test( dump_vcd, "DirectMapCache.vcd", 0, 0, 0 )
