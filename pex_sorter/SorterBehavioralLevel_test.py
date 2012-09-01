#=========================================================================
# SorterBehavioralLevel Unit Tests
#=========================================================================

from pymtl import *

from SorterBehavioralLevel import SorterBehavioralLevel

import random

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def harness( inouts ):

  model = SorterBehavioralLevel()
  model.elaborate()

  sim = SimulationTool( model )
  sim.dump_vcd( "SorterBehavioralLevel_test.vcd" )
  sim.reset()

  for inout in inouts:

    model.in_[0].value = inout[0]
    model.in_[1].value = inout[1]
    model.in_[2].value = inout[2]
    model.in_[3].value = inout[3]

    sim.cycle()

    assert model.out[0].value == inout[4]
    assert model.out[1].value == inout[5]
    assert model.out[2].value == inout[6]
    assert model.out[3].value == inout[7]

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics():
  harness([
  #  ---- in ---- ---- out ----
    [ 4, 3, 2, 1,  1, 2, 3, 4 ],
    [ 9, 6, 7, 1,  1, 6, 7, 9 ],
    [12,16, 3,42,  3,12,16,42 ],
  ])

#-------------------------------------------------------------------------
# Test duplicates
#-------------------------------------------------------------------------

def test_duplicates():
  harness([
  #  ---- in ---- ---- out ----
    [ 2, 8, 9, 9,  2, 8, 9, 9 ],
    [ 2, 8, 2, 8,  2, 2, 8, 8 ],
    [ 1, 1, 1, 1,  1, 1, 1, 1 ],
  ])

#-------------------------------------------------------------------------
# Test random
#-------------------------------------------------------------------------

def test_random():

  # Create random inputs with reference outputs

  inouts = []
  for i in xrange(100):

    # Create random list of four integers

    in_list  = [ random.randint(0,99) for x in xrange(4) ]

    # Create output list which is sorted version of input

    out_list = in_list[:]
    out_list.sort()

    # Add these lists to our inouts

    inouts.append( in_list + out_list )

  harness( inouts )

