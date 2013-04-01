from Model          import *
from SimulationTool import *

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# Register Tester
#-------------------------------------------------------------------------

def register_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  assert model.out == 0
  sim.cycle()
  assert model.out == 8
  model.in_.v = 9
  assert model.out == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out == 10
  model.in_.v = 2
  sim.cycle()
  assert model.out == 2

#-------------------------------------------------------------------------
# RegisterOld
#-------------------------------------------------------------------------

class RegisterOld( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_.value

def test_RegisterOld():
  register_tester( RegisterOld )

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Register( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.n = s.in_

def test_Register():
  register_tester( Register )

#-------------------------------------------------------------------------
# RegisterWrapped
#-------------------------------------------------------------------------

class RegisterWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    # TODO: cannot use keyword "reg" for variable names when converting
    #       To! Check for this?
    s.reg0 = Register( s.nbits )
    # Connections
    connect( s.in_, s.reg0.in_ )
    connect( s.out, s.reg0.out )

def test_RegisterWrapped():
  register_tester( RegisterWrapped )

#-------------------------------------------------------------------------
# RegisterWrappedChain
#-------------------------------------------------------------------------

class RegisterWrappedChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.reg0 = Register( s.nbits )
    s.reg1 = Register( s.nbits )
    s.reg2 = Register( s.nbits )
    # Connections
    connect( s.in_     , s.reg0.in_ )
    connect( s.reg0.out, s.reg1.in_ )
    connect( s.reg1.out, s.reg2.in_ )
    connect( s.reg2.out, s.out      )

def test_RegisterWrappedChain():
  model = RegisterWrappedChain( 16 )
  sim = setup_sim( model )
  sim.reset()
  model.in_.value = 8
  assert model.reg0.out.v ==  0
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 9
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 10
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v ==  8
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v ==  8
  assert model.out.v      ==  8
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v == 10
  assert model.out.v      == 10

#-------------------------------------------------------------------------
# RegisterReset
#-------------------------------------------------------------------------

class RegisterReset(Model):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      if s.reset:
        s.out.n = 0
      else:
        s.out.n = s.in_

def test_RegisterReset():
  model = RegisterReset( 16)
  sim   = setup_sim( model )
  model.in_.v = 8
  assert model.out.v == 0
  sim.reset()
  assert model.out.v == 0
  sim.cycle()
  assert model.out.v == 8
  model.in_.v = 9
  assert model.out.v == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out.v == 10
  sim.reset()
  assert model.out.v == 0
