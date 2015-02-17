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

  # FIXME: loops with variable capture currently aren't translated
  # correctly.
  #
  # For PyMTL code:
  #   for i in range( s.nstages - 1 ):
  #     @s.tick_rtl
  #     def func( i = i ):  # Need to capture i for this to work
  #       s.wire[ i + 1 ].n = s.wire[ i ]
  #
  # We get the following Verilog code:
  #
  #   // logic for func()
  #   always @ (posedge clk) begin
  #     wire[(i+1)] <= wire[i];
  #   end
  #
  #   // logic for func()
  #   always @ (posedge clk) begin
  #     wire[(i+1)] <= wire[i];
  #   end
  #
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


