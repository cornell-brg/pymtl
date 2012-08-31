#=========================================================================
# RegIncrFlat Unit Tests
#=========================================================================

from pymtl import *

from RegIncrFlat import RegIncrFlat

#-------------------------------------------------------------------------
# Basic Test Suite
#-------------------------------------------------------------------------

def test_basics():

  model = RegIncrFlat()
  model.elaborate()

  sim = SimulationTool( model )
  sim.reset()

  def cycle( in_, out ):
    model.in_.value = in_
    sim.eval_combinational()
    assert model.out.value == out
    sim.cycle()

  #      in  out
  cycle(  1,   1 )
  cycle(  2,   2 )
  cycle( 13,   3 )
  cycle( 42,  14 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 51,  43 )
  cycle( 51,  52 )

