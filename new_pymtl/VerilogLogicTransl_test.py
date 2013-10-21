#=========================================================================
# VerilogLogicTransl_test.py
#=========================================================================

import SimulationTool_seq_test as sequential

from VerilogLogicTransl import VerilogLogicTransl
from subprocess         import check_output, STDOUT, CalledProcessError

import tempfile

compiler = 'iverilog -g2005 -Wall -Wno-sensitivity-entire-vector'

#-------------------------------------------------------------------------
# Translation Test
#-------------------------------------------------------------------------
def setup_sim( model ):
  model.elaborate()

  with tempfile.NamedTemporaryFile() as output:
    VerilogLogicTransl( model, output )
    #output.flush()
    #cmd  = '{} {}'.format( compiler, output.name )

    #try:

    #  result = check_output( cmd.split() , stderr=STDOUT )
    #  output.seek(0)
    #  verilog = output.read()
    #  print
    #  print verilog

    #except CalledProcessError as e:

    #  output.seek(0)
    #  verilog = output.read()

    #  raise Exception( 'Module did not compile!\n\n'
    #                   'Command:\n' + ' '.join(e.cmd) + '\n\n'
    #                   'Error:\n' + e.output + '\n'
    #                   'Source:\n' + verilog
    #                 )


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
