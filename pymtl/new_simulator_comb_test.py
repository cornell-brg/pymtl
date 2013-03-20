from new_model import *
from new_simulator import *

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# PassThrough Tester
#-------------------------------------------------------------------------

def passthrough_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  sim.eval_combinational()
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  sim.eval_combinational()
  assert model.out == 10

#-------------------------------------------------------------------------
# PassThrough Old
#-------------------------------------------------------------------------

class PassThroughOld( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )

  @ combinational
  def logic( self ):
    self.out.value = self.in_.value

def test_PassThroughOld():
  passthrough_tester( PassThroughOld )

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )

  @ combinational
  def logic( self ):
    self.out.v = self.in_

import pytest
@pytest.mark.xfail
def test_PassThrough():
  passthrough_tester( PassThrough )
