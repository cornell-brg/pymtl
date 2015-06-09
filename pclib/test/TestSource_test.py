#=========================================================================
# TestSource_test.py
#=========================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.test import TestSource, TestRandomDelay

from TestSimpleSink import TestSimpleSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):
  """Connect source directly to sink."""

  def __init__( s, dtype, msgs, delay ):

    s.src  = TestSource     ( dtype, msgs, delay )
    s.sink = TestSimpleSink ( dtype, msgs )

    s.connect( s.src.out, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# TestHarnessExtraDelay
#-------------------------------------------------------------------------
class TestHarnessExtraDelay( Model ):
  """Connect source to sink through extra delay."""

  def __init__( s, dtype, msgs, delay ):

    s.src   = TestSource      ( dtype, msgs, delay )
    s.delay = TestRandomDelay ( dtype, 5 )
    s.sink  = TestSimpleSink  ( dtype, msgs )

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + \
           s.delay.line_trace() + " > " + \
           s.sink.line_trace()


#-------------------------------------------------------------------------
# do_test
#-------------------------------------------------------------------------
def do_test( dump_vcd, delay, ModelType ):

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

  model = ModelType( 16, test_msgs, delay )
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

@pytest.mark.parametrize( 'delay,model_type', [
  ( 0, TestHarness),
  ( 1, TestHarness),
  ( 5, TestHarness),
  (20, TestHarness),
  ( 0, TestHarnessExtraDelay),
  ( 1, TestHarnessExtraDelay),
  ( 5, TestHarnessExtraDelay),
  (20, TestHarnessExtraDelay),
])
def test_TestSource( dump_vcd, delay, model_type ):
  do_test( dump_vcd, delay, model_type )

