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

# These tests are specifically marked xfail

[ pytest.mark.xfail( x ) for x in [

    test_ValueInSequentialBlock,
    test_MissingNextInSequentialBlock,
    test_MissingListNextInSequentialBlock,
    test_RegisterBits,
    test_RegisterWrappedChain,
    test_SliceTempWriteCheck,

    test_NextInCombinationalBlock,
    test_MissingValueInCombinationalBlock,
    test_MissingListValueInCombinationalBlock,
    test_SubscriptTemp,
    test_CombSlicePassThroughStruct,
    test_IntTemporaries,
    test_IntSubTemporaries,
    test_ListOfMixedUseWires,
    test_RaiseException,
    test_ListOfSubmodPortBundles,

    test_RegSlicePassThrough,
    test_RegSlicePassThroughWire,
    test_RegisterCombBitBlast,
    test_RegisterStructBitBlast,
    test_SliceWriteCheck,
    test_OutputToRegInput,
    test_OutputToRegInputSlice,
    test_OutputToRegInput_Comb,
    test_OutputToRegInputSlice_Comb,
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

