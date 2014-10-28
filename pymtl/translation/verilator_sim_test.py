#=======================================================================
# verilator_sim_test.py
#=======================================================================

from pymtl          import SimulationTool
from verilator_sim  import get_verilated
from pymtl          import requires_verilator
from pclib.regs import Reg

#-----------------------------------------------------------------------
# Test Config
#-----------------------------------------------------------------------
# Skip all tests in module if verilator is not installed

pytestmark = requires_verilator

#-----------------------------------------------------------------------
# Test Function
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Run Tests
#-----------------------------------------------------------------------

def test_reg8():
  reg_test( Reg(8) )

def test_reg16():
  reg_test( Reg(16) )
