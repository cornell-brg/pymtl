#=======================================================================
# TestRandomDelay_test.py
#=======================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.test import TestRandomDelay

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, dtype, msgs, delay ):

    s.src   = TestSimpleSource ( dtype, msgs  )
    s.delay = TestRandomDelay  ( dtype, delay )
    s.sink  = TestSimpleSink   ( dtype, msgs  )

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " | " + \
           s.delay.line_trace() + " | " + \
           s.sink.line_trace()

#-----------------------------------------------------------------------
# test_delay
#-----------------------------------------------------------------------
@pytest.mark.parametrize('random_delay', [
   0,
   1,
   5,
  20,
])
def test_delay( dump_vcd, random_delay ):

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

  model = TestHarness( 16, test_msgs, random_delay )
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
