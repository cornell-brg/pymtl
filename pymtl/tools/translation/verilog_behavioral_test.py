#=======================================================================
# verilog_behavioral_test.py
#=======================================================================

import pytest
import functools

from verilator_sim import TranslationTool
from exceptions    import VerilogTranslationError, VerilatorCompileError

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

#-----------------------------------------------------------------------
# tests specifically marked to fail
#-----------------------------------------------------------------------

[ pytest.mark.xfail(reason=x,raises=z)(y) for x,y,z in [

  #---------------------------------------------------------------------
  # documented bugs
  #---------------------------------------------------------------------

  ('This works fine in Python Simulation, but does not translate into '
   'Verilog correctly because we assume all elements of a list of wires '
   'will have the same assignment structure!',
    test_ListOfMixedUseWires, None ),

  ('FIXME: Incorrect Verilog translation',
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
    test_ListOfSubmodPortBundles, VerilatorCompileError ),

  ('FIXME: TranslationError: cannot infer temporary from subscript',
   test_SliceTempWriteCheck, VerilogTranslationError ),

  ('FIXME: my_signal[0:x-1] does not work, inferred as part select!',
   test_translation_slices03, VerilogTranslationError),
  ('FIXME: my_signal[0:x+1] does not work, inferred as part select!',
   test_translation_slices04, VerilogTranslationError),
  ('FIXME: my_signal[A:B+4] does not work, if A = x*4 and B = 4*x!' ,
   test_translation_slices11, VerilogTranslationError),
  ('FIXME: my_signal[x*4:x*4+2+2] does not work!' ,
   test_translation_slices13, VerilogTranslationError),
  ('Slicing of Bits with steps are not supported.',
   test_translation_slices14, None), #TODO: VerilogTranslationError),

  ('Type inferences of slices > 1-bit are not supported.',
   test_translation_slices15, VerilogTranslationError),

  ('FIXME: @tick_cl does not throw any notice of no translation!',
   test_translation_bad_decorator, None ),

  ('FIXME: loop variables and ports have conflicting names post-translation!',
   test_translation_loopvar_port_name_conflict, VerilatorCompileError ),
  ('FIXME: Inference from sext/zext/Bits cannot take Bits() obj as param.',
   test_translation_inf_func_not_int, VerilogTranslationError ),

  #---------------------------------------------------------------------
  # VerilogTranslationError tests
  #---------------------------------------------------------------------

  ('Assigning sliced list in behavior block does not work.',
   test_translation_list_slice_temp, Exception), # TODO: VerilogTranslationError),
  ('Assigning to a tuple on the LHS is not supported (x,y = ...).',
   test_translation_multiple_lhs_tuple, VerilogTranslationError ),
  ('Chained assignments are not supported (x = y = ...).',
   test_translation_multiple_lhs_targets, VerilogTranslationError ),
  ('Multiple decorators on concurrent blocks not supported.',
   test_translation_multiple_decorators, VerilogTranslationError ),
  ('Only range/xrange are supported for looping, not enumerate.',
   test_translation_for_loop_enumerate, VerilogTranslationError ),
  #('Signals read in for loops are not added to sensitivity list!'),
  # test_translation_for_loop_enumerate_comb, VerilogTranslationError ),
  ('Chained comparisons are currently not translatable.',
   test_translation_bad_comparison, VerilogTranslationError ),
  ('Cannot slice a range() operator and iterate over it.',
   test_translation_list_slice_step, VerilogTranslationError ),
  ('Cannot infer functions not explicitly supported.',
   test_translation_unsupported_func, VerilogTranslationError ),
  ('The sext/zext/Bits funcs cannot take a non-integer as a param',
   test_translation_func_not_int, VerilogTranslationError ),
  ('The step provided to range/xrange must be a constant, non-zero int.',
   test_translation_iter_unsupported_step, VerilogTranslationError ),
  ('Keyword args, arg list unpacking, and arg dict unpacking are not supported!',
   test_translation_keyword_args, VerilogTranslationError ),
  ('Non-literal Bits constructors not supported',
   test_translation_issue_123, VerilogTranslationError ),

]]

#-----------------------------------------------------------------------
# tests are specifically marked to skip
#-----------------------------------------------------------------------

[ pytest.mark.skipif(True, reason=x)(y) for x,y in [
    ('Exception raises appear as print statements in Verilator' ,
     test_RaiseException,),
    ('PyMTLErrors are raised only in the simulator',
     test_ValueInSequentialBlock,),
    ('PyMTLErrors are raised only in the simulator',
     test_MissingNextInSequentialBlock,),
    ('PyMTLErrors are raised only in the simulator',
     test_MissingListNextInSequentialBlock,),
    ('PyMTLErrors are raised only in the simulator',
     test_NextInCombinationalBlock,),
    ('PyMTLErrors are raised only in the simulator',
     test_MissingValueInCombinationalBlock,),
    ('PyMTLErrors are raised only in the simulator',
     test_MissingListValueInCombinationalBlock,),
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

  # debug
  #model.vcd_file = \
  #  'pymtl.tools.simulation.vcd_test.{}.vcd'.format( model.__class__.__name__ )

  model = TranslationTool( model )
  model.elaborate()
  sim = SimulationTool( model )
  return model, sim
