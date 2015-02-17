#=======================================================================
# verilog_structural_test.py
#=======================================================================

import pytest

from verilator_sim import TranslationTool

#-----------------------------------------------------------------------
# Test Config
#-----------------------------------------------------------------------

# This imports all the SimulationTool tests. Below we will hack the
# setup_sim() function call in each module to use a special verilog
# version of the setup.

from ..simulation.SimulationTool_struct_test import *
from ..simulation.SimulationTool_wire_test   import *

# Skip all tests in module if verilator is not installed

pytestmark = requires_verilator

# These tests are specifically marked xfail

[ pytest.mark.xfail( x ) for x in [
     test_PassThrough,
     test_PassThroughBits,
     test_PassThroughList,
     test_PassThroughListWire,
     test_PassThroughWrapped,
     test_PassThroughWrappedChain,
     test_Splitter,
     test_SplitterWires,
     test_SplitterWrapped,
     test_SplitterPT_1,
     test_SplitterPT_2,
     test_SplitterPT_3,
     test_SplitterPT_4,
     test_SplitterPT_5,
     test_ConstantPort,
     test_ConstantSlice,
     test_ListOfPortBundles,
     test_ThreeStageTick,
     test_NStageTick,
     test_NStagePosedge,
     test_NStageComb,
]]

#-----------------------------------------------------------------------
# local_setup_sim
#-----------------------------------------------------------------------
# - (?) create a vcd dump of the simulation
# - elaborate the module
# - translate to verilog with the Translation Tool
# - create a simulator with the SimulationTool

from verilog_behavioral_test import local_setup_sim


