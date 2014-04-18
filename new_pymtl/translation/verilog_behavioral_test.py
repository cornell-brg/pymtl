#=======================================================================
# verilog_behavioral_test.py
#=======================================================================

from ..simulation import SimulationTool_seq_test  as sequential
from ..simulation import SimulationTool_comb_test as combinational
from ..           import requires_iverilog
from verilog      import check_compile as setup_sim

import pytest

#-----------------------------------------------------------------------
# Test Config
#-----------------------------------------------------------------------
# Skip all tests in module if iverilog is not installed

pytestmark = requires_iverilog

#-----------------------------------------------------------------------
# Sequential Logic
#-----------------------------------------------------------------------

def test_RegisterOld():
  setup_sim( sequential.RegisterOld(  8 ) )
  setup_sim( sequential.RegisterOld( 16 ) )

def test_RegisterBits():
  setup_sim( sequential.RegisterBits( 8 ) )

def test_Register():
  setup_sim( sequential.Register( 8 ) )

def test_RegisterWrapped():
  setup_sim( sequential.RegisterWrapped( 8 ) )

def test_RegisterWrappedChain():
  setup_sim( sequential.RegisterWrappedChain( 16 ) )

def test_RegisterReset():
  setup_sim( sequential.RegisterReset( 16 ) )

def test_SliceWriteCheck():
  setup_sim( sequential.SliceWriteCheck( 16 ) )

def test_SliceTempWriteCheck():
  setup_sim( sequential.SliceTempWriteCheck( 16 ) )

def test_MultipleWrites():
  setup_sim( sequential.MultipleWrites() )

def test_BuiltinFuncs():
  setup_sim( sequential.BuiltinFuncs() )

def test_GetMSB():
  setup_sim( sequential.GetMSB( 5 ) )

#-----------------------------------------------------------------------
# Combinational Logic
#-----------------------------------------------------------------------

def test_PassThroughOld():
  setup_sim( combinational.PassThroughOld(8) )
def test_PassThroughBits():
  setup_sim( combinational.PassThroughBits(8) )
def test_PassThrough():
  setup_sim( combinational.PassThrough(8) )
def test_FullAdder():
  setup_sim( combinational.FullAdder() )
def test_RippleCarryAdderNoSlice():
  setup_sim( combinational.RippleCarryAdderNoSlice( 4 ) )
def test_RippleCarryAdder():
  setup_sim( combinational.RippleCarryAdder( 4 ) )
def test_SimpleBitBlast_8_to_8x1():
  setup_sim( combinational.SimpleBitBlast( 8 ) )
def test_SimpleBitBlast_16_to_16x1():
  setup_sim( combinational.SimpleBitBlast( 16 ) )
def test_ComplexBitBlast_8_to_8x1():
  setup_sim( combinational.ComplexBitBlast( 8, 1 ) )
def test_ComplexBitBlast_8_to_4x2():
  setup_sim( combinational.ComplexBitBlast( 8, 2 ) )
def test_ComplexBitBlast_8_to_2x4():
  setup_sim( combinational.ComplexBitBlast( 8, 4 ) )
def test_ComplexBitBlast_8_to_1x8():
  setup_sim( combinational.ComplexBitBlast( 8, 8 ) )
def test_SimpleBitMerge_8x1_to_8():
  setup_sim( combinational.SimpleBitMerge( 16 ) )
def test_SimpleBitMerge_16x1_to_16():
  setup_sim( combinational.SimpleBitMerge( 16 ) )
def test_ComplexBitMerge_8x1_to_8():
  setup_sim( combinational.ComplexBitMerge( 8, 1 ) )
def test_ComplexBitMerge_4x2_to_8():
  setup_sim( combinational.ComplexBitMerge( 8, 2 ) )
def test_ComplexBitMerge_2x4_to_8():
  setup_sim( combinational.ComplexBitMerge( 8, 4 ) )
def test_ComplexBitMerge_1x8_to_8():
  setup_sim( combinational.ComplexBitMerge( 8, 8 ) )
def test_SelfPassThrough():
  setup_sim( combinational.SelfPassThrough( 2 ) )
def test_Mux():
  setup_sim( combinational.Mux( 8, 4 ) )
def test_IfMux():
  setup_sim( combinational.IfMux( 8 ) )
def test_SubscriptTemp():
  setup_sim( combinational.SubscriptTemp( 8 ) )
def test_CombSlicePassThrough():
  setup_sim( combinational.CombSlicePassThrough() )
def test_CombSlicePassThroughWire():
  setup_sim( combinational.CombSlicePassThroughWire() )
def test_CombSlicePassThroughStruct():
  setup_sim( combinational.CombSlicePassThroughStruct() )
def test_BitMergePassThrough():
  setup_sim( combinational.BitMergePassThrough() )
def test_ValueWriteCheck():
  setup_sim( combinational.ValueWriteCheck( 16 ) )
def test_SliceWriteCheck():
  setup_sim( combinational.SliceWriteCheck( 16 ) )
@pytest.mark.xfail
def test_SliceTempWriteCheck():
  setup_sim( combinational.SliceTempWriteCheck( 16 ) )
def test_MultipleWrites():
  setup_sim( combinational.MultipleWrites( 4 ) )
def test_BundleComb():
  setup_sim( combinational.BundleChild( 16 ) )
def test_BundleChain():
  setup_sim( combinational.BundleChain( 16 ) )
def test_GlobalConstants():
  setup_sim( combinational.GlobalConstants() )
def test_IntTemporaries():
  setup_sim( combinational.IntTemporaries() )
def test_IntSubTemporaries():
  setup_sim( combinational.IntSubTemporaries() )

def test_Concat():
  setup_sim( combinational.Concat() )
def test_MultipleTempAssign():
  setup_sim( combinational.MultipleTempAssign() )
def test_ReduceAND():
  setup_sim( combinational.ReduceAND( 4 ) )
def test_ReduceOR():
  setup_sim( combinational.ReduceOR( 4 ) )
def test_ReduceXOR():
  setup_sim( combinational.ReduceXOR( 4 ) )
@pytest.mark.xfail
def test_NestedLoops():
  setup_sim( combinational.NestedLoops( 3 ) )
def test_NestedLoopsStruct():
  setup_sim( combinational.NestedLoopsStruct( 3 ) )
