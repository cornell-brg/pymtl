#=========================================================================
# TestSource Test Suite
#=========================================================================

from pymtl import *

from TestSource      import TestSource
from TestSimpleSink  import TestSimpleSink
from TestRandomDelay import TestRandomDelay

#-------------------------------------------------------------------------
# TestHarness (directly connect source to sink)
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, nbits, msgs, delay ):

    self.src  = TestSource     ( nbits, msgs, delay )
    self.sink = TestSimpleSink ( nbits, msgs )

    connect( self.src.out_msg, self.sink.in_msg )
    connect( self.src.out_val, self.sink.in_val )
    connect( self.src.out_rdy, self.sink.in_rdy )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + self.sink.line_trace()

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
    sim.dump_vcd( "pmlib-TestSource_test_delay" + str(delay) + ".vcd" )

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
# TestSource unit test with delay = 0
#-------------------------------------------------------------------------

def test_delay0( dump_vcd ):
  run_test_random_delay( dump_vcd, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1
#-------------------------------------------------------------------------

def test_delay1( dump_vcd ):
  run_test_random_delay( dump_vcd, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5
#-------------------------------------------------------------------------

def test_delay5( dump_vcd ):
  run_test_random_delay( dump_vcd, 5 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 20
#-------------------------------------------------------------------------

def test_delay20( dump_vcd ):
  run_test_random_delay( dump_vcd, 20 )

#-------------------------------------------------------------------------
# TestHarnessExtraDelay (connect source to sink through extra delay)
#-------------------------------------------------------------------------

class TestHarnessExtraDelay (Model):

  def __init__( self, nbits, msgs, delay ):

    self.src   = TestSource      ( nbits, msgs, delay )
    self.delay = TestRandomDelay ( nbits, 5 )
    self.sink  = TestSimpleSink  ( nbits, msgs )

    # Connect source to random delay

    connect( self.src.out_msg, self.delay.in_msg )
    connect( self.src.out_val, self.delay.in_val )
    connect( self.src.out_rdy, self.delay.in_rdy )

    # Connect random delay to sink

    connect( self.delay.out_msg, self.sink.in_msg )
    connect( self.delay.out_val, self.sink.in_val )
    connect( self.delay.out_rdy, self.sink.in_rdy )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + \
           self.delay.line_trace() + " > " + \
           self.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_xdelay( dump_vcd, delay ):

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

  model = TestHarnessExtraDelay( 16, test_msgs, delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSource_test" + \
                  "_xdelay" + str(delay) + ".vcd" )

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
# TestSource unit test with delay = 0 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay0( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1 and extra delay of 5
#-------------------------------------------------------------------------

def test_delay1( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay5( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 5 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 20 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay20( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 20 )

