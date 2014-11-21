#=========================================================================
# TestSink_test.py
#=========================================================================

from pymtl      import *
from pclib.test import TestSource, TestSink, TestRandomDelay

#-------------------------------------------------------------------------
# TestHarness (directly connect source to sink)
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.nbits      = nbits
    s.msgs       = msgs
    s.src_delay  = src_delay
    s.sink_delay = src_delay

  def elaborate_logic( s ):

    # Instantiate models

    s.src  = TestSource ( s.nbits, s.msgs, s.src_delay  )
    s.sink = TestSink   ( s.nbits, s.msgs, s.sink_delay )

    # Connect

    s.connect( s.src.out, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.sink.line_trace()

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
    sim.dump_vcd( dump_vcd )

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
# TestSink unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else False, 0, 0 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 1 x 1
#-------------------------------------------------------------------------

def test_delay1x1( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else False, 1, 1 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else False, 5, 10 )

#-------------------------------------------------------------------------
# TestSink unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else False, 10, 5 )

#-------------------------------------------------------------------------
# TestHarnessExtraDelay (connect source to sink through extra delay)
#-------------------------------------------------------------------------

class TestHarnessExtraDelay( Model ):

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.nbits      = nbits
    s.msgs       = msgs
    s.src_delay  = src_delay
    s.sink_delay = src_delay

  def elaborate_logic( s ):

    # Instantiate models

    s.src   = TestSource      ( s.nbits, s.msgs, s.src_delay )
    s.delay = TestRandomDelay ( s.nbits, 5 )
    s.sink  = TestSink        ( s.nbits, s.msgs, s.sink_delay )

    # Connect

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + \
           s.delay.line_trace() + " > " + \
           s.sink.line_trace()

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
    sim.dump_vcd( dump_vcd )

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
# TestSource unit test with delay = 0 x 0 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay0x0( dump_vcd ):
  run_test_random_xdelay( get_vcd_filename() if dump_vcd else False, 0, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1 x 1 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay1x1( dump_vcd ):
  run_test_random_xdelay( get_vcd_filename() if dump_vcd else False, 1, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5 x 10 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay5x10( dump_vcd ):
  run_test_random_xdelay( get_vcd_filename() if dump_vcd else False, 5, 10 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 10 x 5 and extra delay of 5
#-------------------------------------------------------------------------

def test_xdelay10x5( dump_vcd ):
  run_test_random_xdelay( get_vcd_filename() if dump_vcd else False, 10, 5 )


#-------------------------------------------------------------------------
# TestTwoSinks (connect source to sink through extra delay)
#-------------------------------------------------------------------------

class TestHarnessTwoDelay( Model ):

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.nbits      = nbits
    s.msgs       = msgs
    s.src_delay  = src_delay
    s.sink_delay = src_delay

  def elaborate_logic( s ):

    # Instantiate models

    s.src1   = TestSource      ( s.nbits, s.msgs[:-2], s.src_delay )
    s.sink1  = TestSink        ( s.nbits, s.msgs[:-2], s.sink_delay )
    s.src2   = TestSource      ( s.nbits, s.msgs,      s.src_delay )
    s.sink2  = TestSink        ( s.nbits, s.msgs,      s.sink_delay )

    # Connect

    s.connect( s.src1.out, s.sink1.in_ )
    s.connect( s.src2.out, s.sink2.in_ )

  def done( s ):
    return (s.src1.done and s.sink1.done and
            s.src2.done and s.sink2.done)

  def line_trace( s ):
    return s.src1.line_trace()  + " > " + \
           s.sink1.line_trace() + "  "  + \
           s.src2.line_trace()  + " > " + \
           s.sink2.line_trace()

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
    sim.dump_vcd( dump_vcd )

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
# TestSource unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_twodelay0x0( dump_vcd ):
  run_test_random_twodelay( get_vcd_filename() if dump_vcd else False, 0, 0 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 1 x 1 and extra delay of 5
#-------------------------------------------------------------------------

def test_twodelay1x1( dump_vcd ):
  run_test_random_twodelay( get_vcd_filename() if dump_vcd else False, 1, 1 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 5 x 10 and extra delay of 5
#-------------------------------------------------------------------------

def test_twodelay5x10( dump_vcd ):
  run_test_random_twodelay( get_vcd_filename() if dump_vcd else False, 5, 10 )

#-------------------------------------------------------------------------
# TestSource unit test with delay = 10 x 5 and extra delay of 5
#-------------------------------------------------------------------------

def test_twodelay10x5( dump_vcd ):
  run_test_random_twodelay( get_vcd_filename() if dump_vcd else False, 10, 5 )
