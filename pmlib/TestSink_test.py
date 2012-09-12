#=========================================================================
# TestSink Test Suite
#=========================================================================

from pymtl import *

from TestSource      import TestSource
from TestSink        import TestSink
from TestRandomDelay import TestRandomDelay

#-------------------------------------------------------------------------
# TestHarness (directly connect source to sink)
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, nbits, msgs, src_delay, sink_delay ):

    # Instantiate models

    self.src  = TestSource ( nbits, msgs, src_delay  )
    self.sink = TestSink   ( nbits, msgs, sink_delay )

    # Connect chain

    connect_chain([ self.src, self.sink ])

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + self.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_delay( dump_vcd, src_delay, sink_delay ):

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

  model = TestHarness( 16, test_msgs, src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSink_test_delay" + \
                  str(src_delay) + "x" + str(sink_delay) + ".vcd" )

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
# TestSink unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_test_random_delay( dump_vcd, 0, 0 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 1 x 1
#-------------------------------------------------------------------------

def test_delay1x1( dump_vcd ):
  run_test_random_delay( dump_vcd, 1, 1 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_test_random_delay( dump_vcd, 5, 10 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_test_random_delay( dump_vcd, 10, 5 )

#-------------------------------------------------------------------------
# TestHarnessExtraDelay (connect source to sink through extra delay)
#-------------------------------------------------------------------------

class TestHarnessExtraDelay (Model):

  def __init__( self, nbits, msgs, src_delay, sink_delay ):

    # Instantiate models

    self.src   = TestSource      ( nbits, msgs, src_delay )
    self.delay = TestRandomDelay ( nbits, 5 )
    self.sink  = TestSink        ( nbits, msgs, sink_delay )

    # Connect chain

    connect_chain([ self.src, self.delay, self.sink ])

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + \
           self.delay.line_trace() + " > " + \
           self.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_xdelay( dump_vcd, src_delay, sink_delay ):

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

  model = TestHarnessExtraDelay( 16, test_msgs, src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSink_test" + \
                  str(src_delay) + "x" + str(sink_delay) + ".vcd" )

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
# TestSource unit test with delay = 0 x 0 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay0x0( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 0, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1 x 1 and extra delay of 5
#-------------------------------------------------------------------------

def test_delay1x1( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 1, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5 x 10 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay5x10( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 5, 10 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 10 x 5 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay10x5( dump_vcd ):
  run_test_random_xdelay( dump_vcd, 10, 5 )


#-------------------------------------------------------------------------
# TestTwoSinks (connect source to sink through extra delay)
#-------------------------------------------------------------------------

class TestHarnessTwoDelay (Model):

  def __init__( self, nbits, msgs, src_delay, sink_delay ):

    # Instantiate models

    self.src1   = TestSource      ( nbits, msgs[:-2], src_delay )
    self.sink1  = TestSink        ( nbits, msgs[:-2], sink_delay )
    self.src2   = TestSource      ( nbits, msgs,      src_delay )
    self.sink2  = TestSink        ( nbits, msgs,      sink_delay )

    # Connect chain

    connect_chain([ self.src1, self.sink1 ])
    connect_chain([ self.src2, self.sink2 ])

  def done( self ):
    return (self.src1.done.value and self.sink1.done.value and
            self.src2.done.value and self.sink2.done.value)

  def line_trace( self ):
    return self.src1.line_trace()  + " > " + \
           self.sink1.line_trace() + "  "  + \
           self.src2.line_trace()  + " > " + \
           self.sink2.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_twodelay( dump_vcd, src_delay, sink_delay ):

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

  model = TestHarnessTwoDelay( 16, test_msgs, src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSink_testtwo" + \
                  str(src_delay) + "x" + str(sink_delay) + ".vcd" )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.num_cycles < 80:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestSource unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_twodelay0x0( dump_vcd ):
  run_test_random_twodelay( dump_vcd, 0, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1 x 1 and extra delay of 5
#-------------------------------------------------------------------------

def test_twodelay1x1( dump_vcd ):
  run_test_random_twodelay( dump_vcd, 1, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5 x 10 and extra delay of 5
#-------------------------------------------------------------------------

def test_twodelay5x10( dump_vcd ):
  run_test_random_twodelay( dump_vcd, 5, 10 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 10 x 5 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay10x5( dump_vcd ):
  run_test_random_twodelay( dump_vcd, 10, 5 )
