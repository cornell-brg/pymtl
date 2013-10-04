#=========================================================================
# TranslationTool_test.py
#=========================================================================

import SimulationTool_struct_test as structural
from VerilogTranslationTool     import VerilogTranslationTool

import tempfile
import os

compiler = 'iverilog -g2005 -Wall -Wno-sensitivity-entire-vector'

def setup_sim( model ):
  model.elaborate()

  with tempfile.NamedTemporaryFile() as output:
    VerilogTranslationTool( model, output )
    output.flush()
    cmd  = '{} {}'.format( compiler, output.name )
    exit = os.system( cmd )

    output.seek(0)
    verilog = output.read()
    print
    print verilog

    if exit != 0:
      raise Exception( "Module did not compile!\n Source:\n" + verilog )


#-------------------------------------------------------------------------
# PassThrough
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

#def test_PassThroughWrapped():
#def test_PassThroughWrappedChain():
#def test_Splitter():
#def test_SplitterWires():
#def test_SplitterWrapped():
#def test_SplitterPT_1():
#def test_SplitterPT_2():
#def test_SplitterPT_3():
#def test_SplitterPT_4():
#def test_SplitterPT_5():
#def test_SplitterPT_5():
#def test_SimpleBitBlast():
#  setup_sim( structural.SimpleBitBlast( 8 ) )
#def test_SimpleBitBlast():
#  setup_sim( structural.SimpleBitBlast( 16 ) )
#def test_ComplexBitBlast():
#def test_SimlbeBitMerge():
#def test_ConstantPort():
#def test_ConstantSlice():
#def test_ConstantModule():
#def test_ListOfPortBundles():
