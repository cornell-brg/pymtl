from verilator_sim  import get_verilated
from new_pmlib.regs import Reg
from new_pymtl      import SimulationTool

def test_reg():
  model  = Reg(16)
  print "BEGIN"
  vmodel = get_verilated( model )
  print "END"

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
