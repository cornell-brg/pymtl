#=======================================================================
# verilog_structural_test.py
#=======================================================================

import pytest
import collections

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


  # FIXME: wire-to-wire connections do not try to infer directionality
  test_WireToWire2,

]]

#-----------------------------------------------------------------------
# verify_pipeline
#-----------------------------------------------------------------------
def verify_pipeline( Model ):
  model = Model()
  model.elaborate()
  sim = SimulationTool( model )

  pipeline = collections.deque( maxlen=3 )
  pipeline.extend( [0]*3 )

  for i in range( 10 ):
    model.in_.value = i
    pipeline.appendleft( i )
    sim.cycle()
    assert model.out == pipeline[-1]

#-----------------------------------------------------------------------
# MultipleParamTranslations
#-----------------------------------------------------------------------
def test_MultipleParamTranslations( setup_sim ):
  class ParamClass( Model ):
    def __init__( s, id_ ):
      s.in_, s.out = InPort(4), OutPort(4)
      s.id_        = id_
      @s.posedge_clk
      def logic():
        s.out.next = s.in_
  class ParentClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(4), OutPort(4)
      s.m = [ TranslationTool(ParamClass( x )) for x in range( 3 ) ]
      s.connect( s.in_,      s.m[0].in_ )
      s.connect( s.m[0].out, s.m[1].in_ )
      s.connect( s.m[1].out, s.m[2].in_ )
      s.connect( s.m[2].out, s.out      )

  verify_pipeline( ParentClass )

#-----------------------------------------------------------------------
# MultipleNoParamTranslations
#-----------------------------------------------------------------------
@pytest.mark.xfail
def test_MultipleNoParamTranslations( setup_sim ):
  class NoParamClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(4), OutPort(4)
      @s.posedge_clk
      def logic():
        s.out.next = s.in_
  class ParentClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(4), OutPort(4)
      s.m = [ TranslationTool( NoParamClass() ) for x in range( 3 ) ]
      s.connect( s.in_,      s.m[0].in_ )
      s.connect( s.m[0].out, s.m[1].in_ )
      s.connect( s.m[1].out, s.m[2].in_ )
      s.connect( s.m[2].out, s.out      )

  verify_pipeline( ParentClass )

#-----------------------------------------------------------------------
# local_setup_sim
#-----------------------------------------------------------------------
# - (?) create a vcd dump of the simulation
# - elaborate the module
# - translate to verilog with the Translation Tool
# - create a simulator with the SimulationTool

from verilog_behavioral_test import local_setup_sim

