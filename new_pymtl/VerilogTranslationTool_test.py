#=========================================================================
# TranslationTool_test.py
#=========================================================================

from SimulationTool_struct_test import PassThrough, PassThroughBits
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

    if exit != 0:

      output.seek(0)
      verilog = output.read()
      raise Exception( "Module did not compile!\n Source:\n" + verilog )

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------
def test_PassThrough():
  setup_sim( PassThrough( 8 ) )
  setup_sim( PassThrough( 32 ) )


def test_PassThroughBits():
  setup_sim( PassThroughBits( 8 ) )
#
#def test_PassThroughList():
#  setup_sim( PassThroughList )
#
#def test_PassThroughListWire():
#  setup_sim( PassThroughListWire )
