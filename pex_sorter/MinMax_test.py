#=========================================================================
# MinMax Unit Tests
#=========================================================================

from pymtl import *

from MinMax import MinMax

import random

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def harness( inouts ):

  model = MinMax()
  model.elaborate()

  sim = SimulationTool( model )
  sim.dump_vcd( "MinMax_test.vcd" )
  sim.reset()

  for inout in inouts:
    print inout

    model.in0.value = inout[0]
    model.in1.value = inout[1]

    sim.cycle()

    assert model.min.value == inout[2]
    assert model.max.value == inout[3]

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics():
  harness([
  #  -- in -- -- out --
    [  4,  3,   3,  4 ],
    [  9,  6,   6,  9 ],
    [ 12, 16,  12, 16 ],
    [ 12, 16,  12, 16 ],
  ])

