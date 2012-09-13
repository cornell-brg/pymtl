#=========================================================================
# SimpleMemory Test Suite
#=========================================================================

from pymtl import *
from MemMsg import *
import pmlib

from TestSimpleMemory import TestSimpleMemory

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    self.src  = pmlib.TestSource ( 67, src_msgs,  src_delay  )
    self.m    = ModelType        ( 1 )
    self.sink = pmlib.TestSink   ( 35, sink_msgs, sink_delay )

    # connect
    connect( self.src.out_msg, self.m.memreq[0] )
    connect( self.src.out_val, self.m.memreq_val[0] )
    connect( self.src.out_rdy, self.m.memreq_rdy[0] )

    connect( self.sink.in_msg, self.m.memresp[0] )
    connect( self.sink.in_val, self.m.memresp_val[0] )
    connect( self.sink.in_rdy, self.m.memresp_rdy[0] )

  def done( self ):
    return self.src.done.value and self.sink.done.value

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_mem_test( dump_vcd, vcd_file_name,
                  ModelType, src_delay, sink_delay ):

  # Test messages

  m = [
    mk_req( 0, 0x00000001, 2, 0x00000000 ), mk_resp( 0, 2, 0x00000000 ),
    mk_req( 1, 0x00000001, 2, 0x00000000 ), mk_resp( 1, 2, 0x00000000 ),
    mk_req( 0, 0x00000001, 2, 0x00000000 ), mk_resp( 0, 2, 0x00000000 ),
    mk_req( 1, 0x00000001, 0, 0xdeadbeef ), mk_resp( 1, 0, 0x00000000 ),
    mk_req( 0, 0x00000001, 0, 0x00000000 ), mk_resp( 0, 0, 0xdeadbeef ),
    mk_req( 1, 0x00000001, 1, 0x00000000 ), mk_resp( 1, 1, 0x00000000 ),
    mk_req( 0, 0x00000001, 0, 0x00000000 ), mk_resp( 0, 0, 0xdeadbe00 ),
    mk_req( 1, 0x00000800, 0, 0xfeedbaac ), mk_resp( 1, 0, 0x00000000 ),
    mk_req( 0, 0x00000800, 0, 0x00000000 ), mk_resp( 0, 0, 0xfeedbaac ),
    mk_req( 1, 0x0000001e, 0, 0xddccbbaa ), mk_resp( 1, 0, 0x00000000 ),
    mk_req( 0, 0x0000001e, 0, 0x00000000 ), mk_resp( 0, 0, 0xddccbbaa ),
  ]

  src_msgs  = m[::2]
  sink_msgs = m[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  #print model.m.mem

  sim.reset()
  while not model.done():
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test Memory unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_mem_test( dump_vcd, "SimpleMemory_test_delay0x0.vcd",
                TestSimpleMemory, 0, 0 )
