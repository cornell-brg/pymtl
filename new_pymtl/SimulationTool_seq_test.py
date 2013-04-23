#=========================================================================
# SimulationTool_seq_test.py
#=========================================================================
# Sequential logic tests for the SimulationTool class.

from Model          import *
from SimulationTool import *
from Bits           import Bits

import pytest

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# Register Tester
#-------------------------------------------------------------------------

def register_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  assert model.out == 0
  sim.cycle()
  assert model.out == 8
  model.in_.v = 9
  assert model.out == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out == 10
  model.in_.v = 2
  sim.cycle()
  assert model.out == 2

#-------------------------------------------------------------------------
# RegisterOld
#-------------------------------------------------------------------------

class RegisterOld( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_.value

def test_RegisterOld():
  register_tester( RegisterOld )

#-------------------------------------------------------------------------
# RegisterBits
#-------------------------------------------------------------------------

class RegisterBits( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( Bits( nbits ) )
    s.out = OutPort ( Bits( nbits ) )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_

def test_RegisterBits():
  register_tester( RegisterBits )

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Register( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.n = s.in_

def test_Register():
  register_tester( Register )

#-------------------------------------------------------------------------
# RegisterWrapped
#-------------------------------------------------------------------------

class RegisterWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    # TODO: cannot use keyword "reg" for variable names when converting
    #       To! Check for this?
    s.reg0 = Register( s.nbits )
    # s.connections
    s.connect( s.in_, s.reg0.in_ )
    s.connect( s.out, s.reg0.out )

def test_RegisterWrapped():
  register_tester( RegisterWrapped )

#-------------------------------------------------------------------------
# RegisterWrappedChain
#-------------------------------------------------------------------------

class RegisterWrappedChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.reg0 = Register( s.nbits )
    s.reg1 = Register( s.nbits )
    s.reg2 = Register( s.nbits )
    # s.connections
    s.connect( s.in_     , s.reg0.in_ )
    s.connect( s.reg0.out, s.reg1.in_ )
    s.connect( s.reg1.out, s.reg2.in_ )
    s.connect( s.reg2.out, s.out      )

def test_RegisterWrappedChain():
  model = RegisterWrappedChain( 16 )
  sim = setup_sim( model )
  sim.reset()
  model.in_.value = 8
  assert model.reg0.out.v ==  0
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 9
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 10
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v ==  8
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v ==  8
  assert model.out.v      ==  8
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v == 10
  assert model.out.v      == 10

#-------------------------------------------------------------------------
# RegisterReset
#-------------------------------------------------------------------------

class RegisterReset( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      if s.reset:
        s.out.n = 0
      else:
        s.out.n = s.in_

def test_RegisterReset():
  model = RegisterReset( 16 )
  sim   = setup_sim( model )
  model.in_.v = 8
  assert model.out.v == 0
  sim.reset()
  assert model.out.v == 0
  sim.cycle()
  assert model.out.v == 8
  model.in_.v = 9
  assert model.out.v == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out.v == 10
  sim.reset()
  assert model.out.v == 0

#-------------------------------------------------------------------------
# RegisterBitBlast
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py

from SimulationTool_comb_test   import verify_bit_blast
from SimulationTool_comb_test   import ComplexBitBlast as CombBitBlast
from SimulationTool_struct_test import ComplexBitBlast as StructBitBlast

class RegisterBitBlast( Model ):
  def __init__( s, nbits, subclass ):
    s.nbits     = nbits
    s.subclass  = subclass
    s.groupings = 2
    s.in_ = InPort( nbits )
    s.out = [ OutPort( s.groupings ) for x in
              xrange( 0, nbits, s.groupings ) ]

  def elaborate_logic( s ):
    # Submodules
    s.reg0  = Register( s.nbits )
    s.split = s.subclass( s.nbits, s.groupings )
    # Connections
    s.connect( s.in_     , s.reg0.in_  )
    s.connect( s.reg0.out, s.split.in_ )
    for i, x in enumerate( s.out ):
      s.connect( s.split.out[i], x )

def register_bit_blast_tester( model ):
  sim = setup_sim( model )
  sim.reset()
  model.in_.v = 0b11110000
  verify_bit_blast( model.out, 0b0 )
  assert model.reg0.out.v  == 0b0
  sim.cycle()
  assert model.reg0.out.v  == 0b11110000
  assert model.split.in_.v == 0b11110000
  verify_bit_blast( model.split.out, 0b11110000 )
  verify_bit_blast( model.out,       0b11110000 )
  model.in_.v = 0b1111000011001010
  assert model.reg0.out.v  == 0b11110000
  assert model.split.in_.v == 0b11110000
  verify_bit_blast( model.split.out, 0b11110000 )
  verify_bit_blast( model.out,       0b11110000 )
  sim.cycle()
  assert model.reg0.out.v  == 0b1111000011001010
  verify_bit_blast( model.out, 0b1111000011001010 )

def test_RegisterCombBitBlast():
  model = RegisterBitBlast( 16, CombBitBlast )
  register_bit_blast_tester( model )

def test_RegisterStructBitBlast():
  model = RegisterBitBlast( 16, StructBitBlast )
  register_bit_blast_tester( model )

#-------------------------------------------------------------------------
# splitslice_tester
#-------------------------------------------------------------------------
# Test slicing followed by sequential logic
# TODO: move to SimulationTool_mix_test.py

def splitslice_tester( model_type ):
  model = model_type()
  sim   = setup_sim( model )
  #import pprint
  #pprint.pprint( model.get_connections() )
  sim.eval_combinational()
  model.in_.v = 0b1001
  assert model.out0 == 0b00
  assert model.out1 == 0b00
  sim.eval_combinational()
  assert model.out0 == 0b01
  assert model.out1 == 0b10
  model.in_.v = 0b1111
  sim.eval_combinational()
  assert model.out0 == 0b11
  assert model.out1 == 0b11

#-------------------------------------------------------------------------
# RegisterPassThrough
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
from SimulationTool_comb_test   import PassThrough

class RegisterPassThrough( Model ):
  def __init__( s, nbits ):
    s.nbits  = nbits
    s.in_    = InPort  ( nbits )
    s.out    = OutPort ( nbits )

  def elaborate_logic( s ):
    s.reg0 = Register    ( s.nbits )
    s.pt   = PassThrough ( s.nbits )

    s.connect( s.in_,      s.reg0.in_ )
    s.connect( s.reg0.out, s.pt.in_   )
    s.connect( s.pt.out,   s.out      )

def test_RegisterPassThrough():
  register_tester( RegisterPassThrough )

#-------------------------------------------------------------------------
# PassThroughRegister
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
from SimulationTool_comb_test   import PassThrough

class PassThroughRegister( Model ):
  def __init__( s, nbits ):
    s.nbits  = nbits
    s.in_    = InPort  ( nbits )
    s.out    = OutPort ( nbits )

  def elaborate_logic( s ):
    s.pt   = PassThrough ( s.nbits )
    s.reg0 = Register    ( s.nbits )

    s.connect( s.in_,      s.pt.in_   )
    s.connect( s.pt.out,   s.reg0.in_ )
    s.connect( s.reg0.out, s.out      )

def test_PassThroughRegister():
  register_tester( PassThroughRegister )

#-------------------------------------------------------------------------
# splitslice_tester
#-------------------------------------------------------------------------
# Test registered slicing followed by combinational logic
# TODO: move to SimulationTool_mix_test.py

def splitslice_tester( model_type ):
  model = model_type()
  sim   = setup_sim( model )
  sim.cycle()
  model.in_.v = 0b1001
  assert model.out0 == 0b00
  assert model.out1 == 0b00
  sim.cycle()
  assert model.out0 == 0b01
  assert model.out1 == 0b10
  model.in_.v = 0b1111
  sim.cycle()
  assert model.out0 == 0b11
  assert model.out1 == 0b11

#-------------------------------------------------------------------------
# RegSlicePassThrough
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
class RegSlicePassThrough( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = OutPort ( 2 )

  def elaborate_logic( s ):
    s.pass0  = PassThrough( 2 )
    s.pass1  = PassThrough( 2 )

    @s.posedge_clk
    def seq_logic():
      s.pass0.in_.n = s.in_[0:2]
      s.pass1.in_.n = s.in_[2:4]

    s.connect( s.pass0.out, s.out0 )
    s.connect( s.pass1.out, s.out1 )

def test_RegSlicePassThrough():
  splitslice_tester( RegSlicePassThrough )

#-------------------------------------------------------------------------
# RegSlicePassThroughWire
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
class RegSlicePassThroughWire( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = OutPort ( 2 )

  def elaborate_logic( s ):
    s.wire0 = Wire( 2 )
    s.wire1 = Wire( 2 )

    @s.posedge_clk
    def seq_logic():
      s.wire0.n    = s.in_[0:2]
      s.wire1.n[:] = s.in_[2:4]

    @s.combinational
    def wire0_logic():
      s.out0.v = s.wire0

    @s.combinational
    def wire1_logic():
      s.out1.v = s.wire1

@pytest.mark.xfail
def test_RegSlicePassThroughWire():
  splitslice_tester( RegSlicePassThroughWire )
