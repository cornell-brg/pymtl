#=========================================================================
# DirectedMappedWriteBackCache Unit Test
#=========================================================================

from   new_pymtl import *
import new_pmlib

import new_pmlib.mem_msgs   as     mem_msgs
import new_pmlib.valrdy     as     valrdy
from   new_pmlib.TestMemory import TestMemory

from TestCacheResp32Sink        import TestCacheResp32Sink
from DirectMappedWriteBackCache import DirectMappedWriteBackCache

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay, mem_delay,
                mem_nbytes, addr_nbits, data_nbits, line_nbits, test_verilog ):

    creq_params  = mem_msgs.MemReqParams ( addr_nbits, data_nbits )
    cresp_params = mem_msgs.MemRespParams( data_nbits )

    mreq_params  = mem_msgs.MemReqParams ( addr_nbits, line_nbits )
    mresp_params = mem_msgs.MemRespParams( line_nbits )

    # Instantiate models

    s.src   = new_pmlib.TestSource( creq_params.nbits, src_msgs,  src_delay )
    s.cache = DirectMappedWriteBackCache( mem_nbytes, addr_nbits,
                                             data_nbits, line_nbits )
    s.mem   = TestMemory( mreq_params, mresp_params, 1, mem_delay )
    s.sink  = TestCacheResp32Sink(  cresp_params, sink_msgs, sink_delay )

    if test_verilog:
      s.cache = get_verilated( s.cache )

  def elaborate_logic( s ):

    # connect

    s.connect( s.src.out,       s.cache.cachereq  )
    s.connect( s.cache.memreq,  s.mem.reqs[0]     )
    s.connect( s.cache.memresp, s.mem.resps[0]    )
    s.connect( s.sink.in_,      s.cache.cacheresp )

  def done( s ):

    done = s.src.done.value and s.sink.done.value
    return done

  def line_trace( s ):
    return s.cache.line_trace()

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache Unit Test
#-------------------------------------------------------------------------

def run_DirectMappedWriteBackCache_test( dump_vcd, test_verilog, vcd_file_name,
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

    #mk_req( rd,   0x000fff00, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeec ),
    #mk_req( wr,   0x000fff00, 0,  0xaaaa0000 ), mk_resp( wr,   0,   0x00000000 ),
    #mk_req( rd,   0x000fff00, 0,  0x00000000 ), mk_resp( rd,   0,   0xaaaa0000 ),

    # Simple Test, write word and read word back

    mk_req( wr,   0x00000000, 0,  0x0a0a0a0a ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x00000000, 0,  0x00000000 ), mk_resp( rd,   0,   0x0a0a0a0a ),

    # Write to valid cache line, make sure all words are hits

    mk_req( wr,   0x00000004, 0,  0x0b0b0b0b ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x00000008, 0,  0x0c0c0c0c ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( wr,   0x0000000c, 0,  0x0d0d0d0d ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x00000004, 0,  0x00000000 ), mk_resp( rd,   0,   0x0b0b0b0b ),
    mk_req( rd,   0x00000008, 0,  0x00000000 ), mk_resp( rd,   0,   0x0c0c0c0c ),
    mk_req( rd,   0x0000000c, 0,  0x00000000 ), mk_resp( rd,   0,   0x0d0d0d0d ),

    # Evict cache line, write to refill line, read word back

    mk_req( wr,   0x0000ff08, 0,  0xdeadbeef ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ff08, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeef ),
    mk_req( wr,   0x0000ff04, 0,  0xff00ff00 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ff04, 0,  0x00000000 ), mk_resp( rd,   0,   0xff00ff00 ),

    # Refill a new cache line

    mk_req( wr,   0x0000ab20, 0,  0xabcdefff ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ab20, 0,  0x00000000 ), mk_resp( rd,   0,   0xabcdefff ),
    mk_req( wr,   0x0000ab2c, 0,  0x01234567 ), mk_resp( wr,   0,   0x00000000 ),
    mk_req( rd,   0x0000ab2c, 0,  0x00000000 ), mk_resp( rd,   0,   0x01234567 ),

    # Make sure old line is still hitting

    mk_req( rd,   0x0000ff08, 0,  0x00000000 ), mk_resp( rd,   0,   0xdeadbeef ),
    mk_req( rd,   0x0000ff04, 0,  0x00000000 ), mk_resp( rd,   0,   0xff00ff00 ),

    # Read the evicted line, make sure data was written back

    mk_req( rd,   0x00000000, 0,  0x00000000 ), mk_resp( rd,   0,   0x0a0a0a0a ),
    mk_req( rd,   0x00000004, 0,  0x00000000 ), mk_resp( rd,   0,   0x0b0b0b0b ),
    mk_req( rd,   0x00000008, 0,  0x00000000 ), mk_resp( rd,   0,   0x0c0c0c0c ),
    mk_req( rd,   0x0000000c, 0,  0x00000000 ), mk_resp( rd,   0,   0x0d0d0d0d ),

    # Test byte accesses

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
                       line_nbits, test_verilog )
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

  #model.cache.ctrl.valid_bits.mem[ 0 ].value = 1
  #model.cache.ctrl.dirty_bits.mem[ 0 ].value = 0

  #model.cache.dpath.tag_array.SRAM.mem[ 0 ].value = \
  #  0x000fff

  #model.cache.dpath.data_array.SRAM.mem[ 0 ].value = \
  #  0xdeadbeefdeadbeeedeadbeeddeadbeec

  # Begin Simulation

  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache src_delay = 0, sink_delay = 0, mem_delay = 0
#-------------------------------------------------------------------------

def test_cache_delay_0x0_0( dump_vcd, test_verilog ):
  run_DirectMappedWriteBackCache_test( dump_vcd, test_verilog,
    "DirectMappedWriteBackCache_test_delay_0x0_0.vcd", 0, 0, 0 )

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache src_delay = 4, sink_delay = 0, mem_delay = 10
#-------------------------------------------------------------------------

def test_cache_delay_4x0_10( dump_vcd, test_verilog ):
  run_DirectMappedWriteBackCache_test( dump_vcd, test_verilog,
    "DirectMappedWriteBackCache_test_delay_4x0_10.vcd", 4, 0, 10 )

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache src_delay = 0, sink_delay = 6, mem_delay = 10
#-------------------------------------------------------------------------

def test_cache_delay_0x6_10( dump_vcd, test_verilog ):
  run_DirectMappedWriteBackCache_test( dump_vcd, test_verilog,
    "DirectMappedWriteBackCache_test_delay_0x6_10.vcd", 0, 6, 10 )

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache src_delay = 8, sink_delay = 6, mem_delay = 12
#-------------------------------------------------------------------------

def test_cache_delay_8x6_12( dump_vcd, test_verilog ):
  run_DirectMappedWriteBackCache_test( dump_vcd, test_verilog,
    "DirectMappedWriteBackCache_test_delay_8x6_12.vcd", 8, 6, 12 )



