#=========================================================================
# VerilogLogicTransl_test.py
#=========================================================================

import SimulationTool_seq_test  as sequential
import SimulationTool_comb_test as combinational

from CLogicTransl import CLogicTransl
from subprocess   import check_output, STDOUT, CalledProcessError
from SignalValue  import CreateWrappedClass
from Model        import *

from CLogicHelpers import gen_cppsim

import tempfile

compiler = "g++ -O3 -fPIC -shared -o {libname} {csource}"

#-------------------------------------------------------------------------
# translate
#-------------------------------------------------------------------------
def translate( model ):
  model.elaborate()

  with tempfile.NamedTemporaryFile(suffix='.cpp') as output:

    cdef, CSimWrapper = CLogicTransl( model, output )
    output.flush()

    # NOTE: if we don't create a unique name for each .so, things get
    #       inconsisten (stale data?)
    clib = model.class_name+'.so'
    cmd  = compiler.format( libname = clib,
                            csource = output.name )

    try:

      result = check_output( cmd.split() , stderr=STDOUT )
      output.seek(0)
      source = output.read()

      csim = gen_cppsim( clib, cdef )
      sim  = CSimWrapper( csim )

      print
      print source
      print

      return sim

    except CalledProcessError as e:

      output.seek(0)
      source = output.read()

      raise Exception( 'Module did not compile!\n\n'
                       'Command:\n' + ' '.join(e.cmd) + '\n\n'
                       'Error:\n' + e.output + '\n'
                       'Source:\n' + source
                     )


#-------------------------------------------------------------------------
# NetObject
#-------------------------------------------------------------------------
class _NetObject( object ):
  def __init__( self, dest=0, src=0, seqnum=0, payload=0 ):
    self.dest    = dest
    self.src     = src
    self.seqnum  = seqnum
    self.payload = payload

NO = CreateWrappedClass( _NetObject )

#-------------------------------------------------------------------------
# Sequential Logic
#-------------------------------------------------------------------------

def test_Register():
  sim = translate( sequential.Register( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 8
  sim.in_ = 9; assert sim.out == 8
  sim.in_ = 10
  sim.cycle(); assert sim.out == 10
  sim.in_ = 2
  sim.cycle(); assert sim.out == 2

def test_RegisterWrapped():
  sim = translate( sequential.RegisterWrapped( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 8
  sim.in_ = 9; assert sim.out == 8
  sim.in_ = 10
  sim.cycle(); assert sim.out == 10
  sim.in_ = 2
  sim.cycle(); assert sim.out == 2

def test_RegisterWrappedChain():
  sim = translate( sequential.RegisterWrappedChain( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 0
  sim.cycle(); assert sim.out == 0
  sim.in_ = 9;
  sim.in_ = 10
  sim.cycle(); assert sim.out == 8
  sim.in_ = 2
  sim.cycle(); assert sim.out == 8
  sim.cycle(); assert sim.out == 10
  sim.cycle(); assert sim.out == 2

#def test_RegisterReset():
#  sim = translate( sequential.RegisterReset( 16 ) )
#  model.in_ = 8
#  assert model.out == 0
#  sim.reset()
#  assert model.out == 0
#  sim.cycle()
#  assert model.out == 8
#  model.in_ = 9
#  assert model.out == 8
#  model.in_ = 10
#  sim.cycle()
#  assert model.out == 10
#  sim.reset()
#  assert model.out == 0


# TODO: slices not supported
# TODO: bit math doesn't work properly

#def test_SliceWriteCheck():
#  translate( sequential.SliceWriteCheck( 16 ) )
#
#def test_SliceTempWriteCheck():
#  translate( sequential.SliceTempWriteCheck( 16 ) )


#def test_MultipleWrites():
#  translate( sequential.MultipleWrites() )
#

#-------------------------------------------------------------------------
# Complex Objects
#-------------------------------------------------------------------------
#def test_Register_Obj():
#  translate( sequential.Register( NO ) )

##-------------------------------------------------------------------------
## Combinational Logic
##-------------------------------------------------------------------------
#def test_PassThroughOld():
#  translate( combinational.PassThroughOld(8) )
#def test_PassThroughBits():
#  translate( combinational.PassThroughBits(8) )
#def test_PassThrough():
#  translate( combinational.PassThrough(8) )
#def test_FullAdder():
#  translate( combinational.FullAdder() )
#def test_RippleCarryAdderNoSlice():
#  translate( combinational.RippleCarryAdderNoSlice( 4 ) )
#def test_RippleCarryAdder():
#  translate( combinational.RippleCarryAdder( 4 ) )
#def test_SimpleBitBlast_8_to_8x1():
#  translate( combinational.SimpleBitBlast( 8 ) )
#def test_SimpleBitBlast_16_to_16x1():
#  translate( combinational.SimpleBitBlast( 16 ) )
#def test_ComplexBitBlast_8_to_8x1():
#  translate( combinational.ComplexBitBlast( 8, 1 ) )
#def test_ComplexBitBlast_8_to_4x2():
#  translate( combinational.ComplexBitBlast( 8, 2 ) )
#def test_ComplexBitBlast_8_to_2x4():
#  translate( combinational.ComplexBitBlast( 8, 4 ) )
#def test_ComplexBitBlast_8_to_1x8():
#  translate( combinational.ComplexBitBlast( 8, 8 ) )
#def test_SimpleBitMerge_8x1_to_8():
#  translate( combinational.SimpleBitMerge( 16 ) )
#def test_SimpleBitMerge_16x1_to_16():
#  translate( combinational.SimpleBitMerge( 16 ) )
#def test_ComplexBitMerge_8x1_to_8():
#  translate( combinational.ComplexBitMerge( 8, 1 ) )
#def test_ComplexBitMerge_4x2_to_8():
#  translate( combinational.ComplexBitMerge( 8, 2 ) )
#def test_ComplexBitMerge_2x4_to_8():
#  translate( combinational.ComplexBitMerge( 8, 4 ) )
#def test_ComplexBitMerge_1x8_to_8():
#  translate( combinational.ComplexBitMerge( 8, 8 ) )
#def test_SelfPassThrough():
#  translate( combinational.SelfPassThrough( 2 ) )
#def test_Mux():
#  translate( combinational.Mux( 8, 4 ) )
#def test_IfMux():
#  translate( combinational.IfMux( 8 ) )
#def test_CombSlicePassThrough():
#  translate( combinational.CombSlicePassThrough() )
#def test_CombSlicePassThroughWire():
#  translate( combinational.CombSlicePassThroughWire() )
#def test_CombSlicePassThroughStruct():
#  translate( combinational.CombSlicePassThroughStruct() )
#def test_BitMergePassThrough():
#  translate( combinational.BitMergePassThrough() )
#def test_ValueWriteCheck():
#  translate( combinational.ValueWriteCheck( 16 ) )
#def test_SliceWriteCheck():
#  translate( combinational.SliceWriteCheck( 16 ) )
#def test_SliceTempWriteCheck():
#  translate( combinational.SliceTempWriteCheck( 16 ) )
#def test_MultipleWrites():
#  translate( combinational.MultipleWrites( 4 ) )
