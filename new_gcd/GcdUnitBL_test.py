#=========================================================================
# GcdUnitBL Test Suite
#=========================================================================

from new_pymtl import *
from new_pmlib import TestSource, TestSink

from GcdUnitBL import GcdUnitBL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    s.src  = TestSource ( 64, src_msgs,  src_delay  )
    s.gcd  = ModelType        ()
    s.sink = TestSink   ( 32, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src.out_msg, s.gcd.in_.msg )
    s.connect( s.src.out_val, s.gcd.in_.val )
    s.connect( s.src.out_rdy, s.gcd.in_.rdy )

    s.connect( s.gcd.out.msg, s.sink.in_msg )
    s.connect( s.gcd.out.val, s.sink.in_val )
    s.connect( s.gcd.out.rdy, s.sink.in_rdy )

    #connect_chain([ s.src, s.gcd, s.sink ]) # TODO?

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + \
           s.gcd.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def concat( a, b ):
  return ( a << 32 | b )

def run_gcd_test( dump_vcd, vcd_file_name,
                  ModelType, src_delay, sink_delay ):

  # Test messages

  m = [
    concat( 15,  5 ),  5,
    concat(  5, 15 ),  5,
    concat(  7, 13 ),  1,
    concat( 75, 45 ), 15,
    concat( 36, 96 ), 12,
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

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay0x0.vcd",
                GcdUnitBL, 0, 0 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay10x5.vcd",
                GcdUnitBL, 10, 5 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay5x10.vcd",
                GcdUnitBL, 5, 10 )

