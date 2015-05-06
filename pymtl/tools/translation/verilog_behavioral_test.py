#=======================================================================
# verilog_behavioral_test.py
#=======================================================================

import pytest
import functools

from verilator_sim import TranslationTool
from exceptions    import VerilogTranslationError

#-----------------------------------------------------------------------
# Test Config
#-----------------------------------------------------------------------

# This imports all the SimulationTool tests. Below we will hack the
# setup_sim() function call in each module to use a special verilog
# version of the setup.

from ..simulation.SimulationTool_seq_test    import *
from ..simulation.SimulationTool_comb_test   import *
from ..simulation.SimulationTool_mix_test    import *
from ..simulation.SimulationTool_transl_test import *

# Skip all tests in module if verilator is not installed

pytestmark = requires_verilator

# These tests are specifically marked to fail

[ pytest.mark.xfail(reason=y)(x) for x,y in [


  (test_SubscriptTemp,
   'FIXME: Verilator/PyMTL simulation mismatch! Verilator bug?'),

  (test_ListOfMixedUseWires,
   'This works fine in Python Simulation, but does not translate into '
   'Verilog correctly because we assume all elements of a list of wires '
   'will have the same assignment structure!'),

  (test_ListOfSubmodPortBundles,
    'FIXME: Incorrect Verilog translation'),
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

  (test_SliceTempWriteCheck,
   'FIXME: TranslationError: cannot infer temporary from subscript'),

  (test_translation_slices03,
   'FIXME: my_signal[0:x-1] does not work, inferred as part select!'),
  (test_translation_slices04,
   'FIXME: my_signal[0:x+1] does not work, inferred as part select!'),

  #'FIXME: my_signal[-2]   issue #31'),
  #'FIXME: my_signal[0:-2] issue #31'),

  (test_translation_slices11,
   'FIXME: my_signal[A:B+4] does not work, if A = x*4 and B = 4*x!'),
  (test_translation_slices13,
   'FIXME: my_signal[x*4:x*4+2+2] does not work!'),

  (test_translation_bad_decorator,
   'FIXME: @tick_cl does not throw any notice of no translation!'),
  (test_translation_loopvar_port_name_conflict,
   'FIXME: loop variables and ports have conflicting names post-translation!'),

  (test_translation_list_slice_temp,
   'Assigning sliced list in behavior block does not work.'),

   #'FIXME: for loop reverse iteration'
]]

# These tests are specifically marked to skip

[ pytest.mark.skipif(True, reason=y)(x) for x,y in [
    (test_RaiseException,
     'Exception raises appear as print statements in Verilator'),
    (test_ValueInSequentialBlock,
     'PyMTLErrors are raised only in the simulator'),
    (test_MissingNextInSequentialBlock,
     'PyMTLErrors are raised only in the simulator'),
    (test_MissingListNextInSequentialBlock,
     'PyMTLErrors are raised only in the simulator'),
    (test_NextInCombinationalBlock,
     'PyMTLErrors are raised only in the simulator'),
    (test_MissingValueInCombinationalBlock,
     'PyMTLErrors are raised only in the simulator'),
    (test_MissingListValueInCombinationalBlock,
     'PyMTLErrors are raised only in the simulator'),
]]

# These tests are specifically meant to check for VerilogTranslationErrors
[ pytest.mark.xfail(raises=VerilogTranslationError, reason=y)(x) for x,y in [

  (test_translation_multiple_lhs_tuple,      ''),
  (test_translation_multiple_lhs_targets,    ''),
  (test_translation_multiple_decorators,     ''),
  (test_translation_for_loop_enumerate,      ''),
  #(test_translation_for_loop_enumerate_comb, '' ),
  (test_translation_bad_comparison,
   'Chained comparisons are currently not translatable.'),
  (test_translation_list_slice_step,
    'Cannot slice a range() operator and iterate over it.'),
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
