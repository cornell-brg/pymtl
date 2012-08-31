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
    sim.cycle()
    assert model.out.value == out

  #      in  out
  cycle(  0,   0 )
  cycle(  1,   1 )
  cycle( 13,  13 )
  cycle( 42,  42 )
  cycle( 42,  42 )
  cycle( 42,  42 )
  cycle( 42,  42 )
  cycle( 51,  51 )
  cycle( 51,  51 )

