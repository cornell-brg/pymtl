from verilator_sim  import get_verilated
from new_pmlib.regs import Reg
from new_pymtl      import SimulationTool

def reg_test( model ):

  vmodel = get_verilated( model )
  vmodel.elaborate()

  sim = SimulationTool( vmodel )

  sim.reset()
  assert vmodel.out ==  0

  vmodel.in_.value   = 10
  sim.cycle()
  assert vmodel.out == 10

  vmodel.in_.value   = 12
  assert vmodel.out == 10
  sim.cycle()
  assert vmodel.out == 12

def test_reg8():
  reg_test( Reg(8) )

def test_reg16():
  reg_test( Reg(16) )
