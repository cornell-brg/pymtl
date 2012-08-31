#=========================================================================
# RegIncrStruct Unit Tests
#=========================================================================

from pymtl import *

from RegIncrStruct import RegIncrStruct

#-------------------------------------------------------------------------
# Basic Test Suite
#-------------------------------------------------------------------------

def test_basics():

  model = RegIncrStruct()
  model.elaborate()

  sim = SimulationTool( model )
  sim.reset()

  def cycle( in_, out ):
    model.in_.value = in_
    sim.cycle()
    assert model.out.value == out

  #      in  out
  cycle(  1,   2 )
  cycle(  2,   3 )
  cycle( 13,  14 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 51,  52 )
  cycle( 51,  52 )

