#=========================================================================
# GcdUnitBL Test Suite
#=========================================================================

from new_pymtl import *
from new_pmlib import TestSource, TestSink

from GcdUnitBL import GcdUnitBL

from new_pymtl.translation_tools.verilator_sim import get_verilated

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, gcd_model, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    s.src  = TestSource ( 64, src_msgs,  src_delay  )
    s.gcd  = gcd_model
    s.sink = TestSink   ( 32, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src.out, s.gcd.in_  )
    s.connect( s.gcd.out, s.sink.in_ )

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

def run_gcd_test( dump_vcd, vcd_file_name, test_verilog,
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

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = get_verilated( model_under_test )

  model = TestHarness( model_under_test, src_msgs, sink_msgs,
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
                False, GcdUnitBL, 0, 0 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay10x5.vcd",
                False, GcdUnitBL, 10, 5 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay5x10.vcd",
                False, GcdUnitBL, 5, 10 )

