#=========================================================================
# Register Unit Tests
#=========================================================================

from pymtl import *

from Register import Register

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def harness( inouts ):

  model = Register(16)
  model.elaborate()

  sim = SimulationTool( model )
  sim.dump_vcd( "Register_test.vcd" )
  sim.reset()

  for inout in inouts:
    model.in_.value = inout[0]
    sim.cycle()
    assert model.out.value == inout[1]

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics():
  harness([
    # in   out
    [  0,   0 ],
    [  1,   1 ],
    [ 13,  13 ],
    [ 42,  42 ],
    [ 42,  42 ],
    [ 42,  42 ],
    [ 42,  42 ],
    [ 51,  51 ],
    [ 51,  51 ],
  ])

