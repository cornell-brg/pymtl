#=======================================================================
# verilog_behavioral_test.py
#=======================================================================

import pytest

from verilator_sim import TranslationTool

#-----------------------------------------------------------------------
# Test Config
#-----------------------------------------------------------------------

# This imports all the SimulationTool tests. Below we will hack the
# setup_sim() function call in each module to use a special verilog
# version of the setup.

from ..simulation.SimulationTool_seq_test  import *
from ..simulation.SimulationTool_comb_test import *
from ..simulation.SimulationTool_mix_test  import *

# Skip all tests in module if verilator is not installed

pytestmark = requires_verilator

# These tests are specifically marked skip

[ pytest.mark.xfail( x ) for x in [


  # FIXME: Verilator/PyMTL simulation mismatch! Verilator bug?
  test_SubscriptTemp,

  # This works fine in Python Simulation, but does not translate into
  # Verilog correctly because we assume all elements of a list of wires
  # will have the same assignment structure!
  test_ListOfMixedUseWires,

  # FIXME: Incorrect Verilog translation:
  # PYMTL:
  #   @s.combinational
  #   def logic1():
  #     for i in range(2):
  #       s.submod[i].in_.a.value = s.in_[i].a
  #       s.submod[i].in_.b.value = s.in_[i].b
  #
  # VERILOG:
  #   always @ (*) begin
  #     for (i=0; i < 2; i=i+1)
  #     begin
  #       in__a = in__a[i];
  #       in__b = in__b[i];
  #     end
  #   end
  test_ListOfSubmodPortBundles,

  # FIXME: TranslationError: cannot infer temporary from subscript
  test_SliceTempWriteCheck,

]]

# Exception raises appear as print statements in Verilator
pytest.mark.skipif( True )( test_RaiseException )

# PyMTLErrors are raised only in the simulator
[ pytest.mark.skipif( True )( x ) for x in [
  test_ValueInSequentialBlock,
  test_MissingNextInSequentialBlock,
  test_MissingListNextInSequentialBlock,
  test_NextInCombinationalBlock,
  test_MissingValueInCombinationalBlock,
  test_MissingListValueInCombinationalBlock,
]]

#-----------------------------------------------------------------------
# local_setup_sim
#-----------------------------------------------------------------------
# - (?) create a vcd dump of the simulation
# - elaborate the module
# - translate to verilog with the Translation Tool
# - create a simulator with the SimulationTool
#
def local_setup_sim( model ):

  #model.vcd_file = \
  #  'pymtl.tools.simulation.vcd_test.{}.vcd'.format( model.class_name )

  model = TranslationTool( model )
  model.elaborate()
  sim = SimulationTool( model )
  return model, sim

