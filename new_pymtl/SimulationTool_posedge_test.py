#from Model import *
#from SimulationTool import *
#
##-------------------------------------------------------------------------
## Setup Sim
##-------------------------------------------------------------------------
#
#def setup_sim( model ):
#  model.elaborate()
#  sim = SimulationTool( model )
#  return sim
#
##-------------------------------------------------------------------------
## Register Tester
##-------------------------------------------------------------------------
#
#def register_tester( model_type ):
#  model = model_type( 16 )
#  sim = self.setup_sim( model )
#  model.in_.v = 8
#  assert model.out == 0
#  sim.cycle()
#  assert model.out == 8
#  model.in_.v = 9
#  assert model.out == 8
#  model.in_.v = 10
#  sim.cycle()
#  assert model.out == 10
#
##-------------------------------------------------------------------------
## RegisterOld
##-------------------------------------------------------------------------
#
#class RegisterOld(Model):
#  def __init__(self, bits):
#    self.in_ = InPort(bits)
#    self.out = OutPort(bits)
#
#  @posedge_clk
#  def tick(self):
#    self.out.next = self.in_.value
#
#def test_RegisterOld():
#  register_tester( RegisterOld )
#
##-------------------------------------------------------------------------
## Register
##-------------------------------------------------------------------------
#
#class Register(Model):
#  def __init__(self, bits):
#    self.in_ = InPort(bits)
#    self.out = OutPort(bits)
#
#  @posedge_clk
#  def tick(self):
#    self.out.n = self.in_
#
#def test_Register():
#  register_tester( Register )
