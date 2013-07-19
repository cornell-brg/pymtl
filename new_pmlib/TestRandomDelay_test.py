#=========================================================================
# TestRandomDelay Test Suite
#=========================================================================

from new_pymtl import *

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink
from TestRandomDelay  import TestRandomDelay

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, nbits, msgs, delay ):

    # Instantiate models

    s.src   = TestSimpleSource ( nbits, msgs  )
    s.delay = TestRandomDelay  ( nbits, delay )
    s.sink  = TestSimpleSink   ( nbits, msgs  )

    # Connect chain

    #connect_chain([ s.src, s.delay, s.sink ])
    s.connect( s.src.out_msg,   s.delay.in_msg )
    s.connect( s.src.out_val,   s.delay.in_val )
    s.connect( s.src.out_rdy,   s.delay.in_rdy )
    s.connect( s.delay.out_msg, s.sink.in_msg  )
    s.connect( s.delay.out_val, s.sink.in_val  )
    s.connect( s.delay.out_rdy, s.sink.in_rdy  )

  def elaborate_logic( s ):
    pass

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " | " + \
           s.delay.line_trace() + " | " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_delay( dump_vcd, delay ):

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

  model = TestHarness( 16, test_msgs, delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestRandomDelay_test_delay" + str(delay) + ".vcd" )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()
  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 0
#-------------------------------------------------------------------------

def test_delay0( dump_vcd ):
  run_test_random_delay( dump_vcd, 0 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 1
#-------------------------------------------------------------------------

def test_delay1( dump_vcd ):
  run_test_random_delay( dump_vcd, 1 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 5
#-------------------------------------------------------------------------

def test_delay5( dump_vcd ):
  run_test_random_delay( dump_vcd, 5 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 20
#-------------------------------------------------------------------------

def test_delay20( dump_vcd ):
  run_test_random_delay( dump_vcd, 20 )

