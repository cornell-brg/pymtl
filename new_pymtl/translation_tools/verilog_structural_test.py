#=========================================================================
# verilog_structural_test.py
#=========================================================================

from ..      import SimulationTool_struct_test as structural
from ..      import requires_iverilog
from verilog import check_compile as setup_sim

#-------------------------------------------------------------------------
# Test Config
#-------------------------------------------------------------------------
# Skip all tests in module if iverilog is not installed

pytestmark = requires_iverilog

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

def test_PassThrough():
  setup_sim( structural.PassThrough( 8 ) )
  setup_sim( structural.PassThrough( 32 ) )

def test_PassThroughBits():
  setup_sim( structural.PassThroughBits( 8 ) )

def test_PassThroughList():
  setup_sim( structural.PassThroughList( 8, 4 ) )
  setup_sim( structural.PassThroughList( 8, 1 ) )

def test_PassThroughListWire():
  setup_sim( structural.PassThroughListWire( 8, 4 ) )
  setup_sim( structural.PassThroughListWire( 8, 1 ) )

def test_PassThroughWrapped():
  setup_sim( structural.PassThroughWrapped( 8 ) )

def test_PassThroughWrappedChain():
  setup_sim( structural.PassThroughWrappedChain( 8 ) )

def test_Splitter():
  setup_sim( structural.Splitter( 16 ) )

def test_SplitterWires():
  setup_sim( structural.SplitterWires( 16 ) )

def test_SplitterWrapped():
  setup_sim( structural.SplitterWrapped( 16 ) )

def test_SplitterPT_1():
  setup_sim( structural.SplitterPT_1( 16 ) )

def test_SplitterPT_2():
  setup_sim( structural.SplitterPT_2( 16 ) )

def test_SplitterPT_3():
  setup_sim( structural.SplitterPT_3( 16 ) )

def test_SplitterPT_4():
  setup_sim( structural.SplitterPT_4( 16 ) )

def test_SplitterPT_5():
  setup_sim( structural.SplitterPT_5( 16 ) )

def test_SimpleBitBlast():
  setup_sim( structural.SimpleBitBlast( 8 ) )

def test_ComplexBitBlast():
  setup_sim( structural.ComplexBitBlast( 8, 2 ) )

def test_SimpleBitMerge():
  setup_sim( structural.SimpleBitMerge( 8 ) )

def test_ComplexBitMerge():
  setup_sim( structural.ComplexBitMerge( 8, 2 ) )

def test_ConstantPort():
  setup_sim( structural.ConstantPort() )

def test_ConstantSlice():
  setup_sim( structural.ConstantSlice() )

def test_ConstantModule():
  setup_sim( structural.ConstantModule() )

def test_ListOfPortBundles():
  setup_sim( structural.ListOfPortBundles() )


