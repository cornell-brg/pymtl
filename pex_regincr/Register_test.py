#=========================================================================
# Register Unit Tests
#=========================================================================

from pymtl import *

from Register import Register

#-------------------------------------------------------------------------
# Basic Test Suite
#-------------------------------------------------------------------------

def test_basics():

  model = Register(16)
  model.elaborate()

  sim = SimulationTool( model )
  sim.reset()

  def cycle( in_, out ):
    model.in_.value = in_
    sim.eval_combinational()
    assert model.out.value == out
    sim.cycle()

  #      in  out
  cycle(  0,   0 )
  cycle(  1,   0 )
  cycle( 13,   1 )
  cycle( 42,  13 )
  cycle( 42,  42 )
  cycle( 42,  42 )
  cycle( 42,  42 )
  cycle( 51,  42 )
  cycle( 51,  51 )

