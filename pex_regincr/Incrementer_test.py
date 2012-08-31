#=========================================================================
# Incrementer Unit Tests
#=========================================================================

from pymtl import *

from Incrementer import Incrementer

#-------------------------------------------------------------------------
# Basic Test Suite
#-------------------------------------------------------------------------

def test_basics():

  model = Incrementer(16)
  model.elaborate()

  sim = SimulationTool( model )
  sim.reset()

  def cycle( in_, out ):
    model.in_.value = in_
    sim.eval_combinational()
    assert model.out.value == out
    sim.cycle()

  #      in  out
  cycle(  0,   1 )
  cycle(  1,   2 )
  cycle( 13,  14 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 42,  43 )
  cycle( 51,  52 )
  cycle( 51,  52 )

