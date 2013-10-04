#=========================================================================
# TranslationTool_test.py
#=========================================================================

import SimulationTool_struct_test as t1
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
  setup_sim( t1.PassThrough( 8 ) )
  setup_sim( t1.PassThrough( 32 ) )

def test_PassThroughBits():
  setup_sim( t1.PassThroughBits( 8 ) )

def test_PassThroughList():
  setup_sim( t1.PassThroughList( 8, 4 ) )
  setup_sim( t1.PassThroughList( 8, 1 ) )

#def test_PassThroughListWire():
#  setup_sim( PassThroughListWire )
