#=========================================================================
# TestSimpleSink_test.py
#=========================================================================

from __future__ import print_function

from pymtl import *

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, nbits, msgs ):

    # Instantiate models

    s.src  = TestSimpleSource ( nbits, msgs )
    s.sink = TestSimpleSink   ( nbits, msgs )

    # Connect chain

    s.connect( s.src.out.msg, s.sink.in_.msg )
    s.connect( s.src.out.val, s.sink.in_.val )
    s.connect( s.src.out.rdy, s.sink.in_.rdy )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " | " + s.sink.line_trace()

#-------------------------------------------------------------------------
# test_basics
#-------------------------------------------------------------------------
def test_basics( dump_vcd ):

  # Test messages

  test_msgs = [
    0x0000,
    0x0a0a,
    0x0b0b,
    0x0c0c,
    0x0d0d,
    0xf0f0,
    0xe0e0,
    0xd0d0,
  ]

  # Instantiate and elaborate the model

  model = TestHarness( 16, test_msgs )
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

