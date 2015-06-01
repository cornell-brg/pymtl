#=========================================================================
# TestSink_test.py
#=========================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.test import TestSource, TestSink, TestRandomDelay

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):
  """Directly connect source to sink."""

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.src  = TestSource ( nbits, msgs, src_delay  )
    s.sink = TestSink   ( nbits, msgs, sink_delay )

    s.connect( s.src.out, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# TestHarnessExtraDelay
#-------------------------------------------------------------------------
class TestHarnessExtraDelay( Model ):
  """Connect source to delay to sink."""

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.src   = TestSource      ( nbits, msgs, src_delay )
    s.delay = TestRandomDelay ( nbits, 5 )
    s.sink  = TestSink        ( nbits, msgs, sink_delay )

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + \
           s.delay.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# TestHarnessTwoDelay
#-------------------------------------------------------------------------
class TestHarnessTwoDelay( Model ):
  """Two independent source->delay->sink pipelines."""

  def __init__( s, nbits, msgs, src_delay, sink_delay ):

    s.src1   = TestSource      ( nbits, msgs[:-2], src_delay )
    s.sink1  = TestSink        ( nbits, msgs[:-2], sink_delay )
    s.src2   = TestSource      ( nbits, msgs,      src_delay )
    s.sink2  = TestSink        ( nbits, msgs,      sink_delay )

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
# do_test
#-------------------------------------------------------------------------
def do_test( dump_vcd, src_delay, sink_delay, ModelType ):

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

  model = ModelType( 16, test_msgs, src_delay, sink_delay )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

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
# test_TestSink
#-------------------------------------------------------------------------
@pytest.mark.parametrize('src_delay,sink_delay,model_type',[
  ( 0,  0, TestHarness),
  ( 1,  1, TestHarness),
  ( 5, 10, TestHarness),
  (10,  5, TestHarness),
  ( 0,  0, TestHarnessExtraDelay),
  ( 1,  1, TestHarnessExtraDelay),
  ( 5, 10, TestHarnessExtraDelay),
  (10,  5, TestHarnessExtraDelay),
  ( 0,  0, TestHarnessTwoDelay),
  ( 1,  1, TestHarnessTwoDelay),
  ( 5, 10, TestHarnessTwoDelay),
  (10,  5, TestHarnessTwoDelay),
])
def test_TestSink( dump_vcd, src_delay, sink_delay, model_type ):
  do_test( dump_vcd, src_delay, sink_delay, model_type )
