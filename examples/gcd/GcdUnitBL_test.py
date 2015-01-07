#=========================================================================
# GcdUnitBL Test Suite
#=========================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.test import TestSource, TestSink
from GcdUnitBL  import GcdUnitBL

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

def run_gcd_test( dump_vcd, test_verilog, ModelType, src_delay, sink_delay ):

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
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  (  0,  0),
  ( 10,  5),
  (  5, 10),
])
def test( dump_vcd, src_delay, sink_delay ):
  run_gcd_test( dump_vcd, False, GcdUnitBL, src_delay, sink_delay )
