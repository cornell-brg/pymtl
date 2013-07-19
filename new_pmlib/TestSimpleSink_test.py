#=========================================================================
# TestSimpleSink Test Suite
#=========================================================================

from new_pymtl import *

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, nbits, msgs ):

    # Instantiate models

    s.src  = TestSimpleSource ( nbits, msgs  )
    s.sink = TestSimpleSink   ( nbits, msgs )

    # Connect chain

    #connect_chain([ s.src, s.sink ])
    s.connect( s.src.out_msg, s.sink.in_msg )
    s.connect( s.src.out_val, s.sink.in_val )
    s.connect( s.src.out_rdy, s.sink.in_rdy )

  def elaborate_logic( s ):
    pass

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " | " + s.sink.line_trace()

#-------------------------------------------------------------------------
# TestSimpleSink unit test
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
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSimpleSink_test_basics.vcd" )

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

