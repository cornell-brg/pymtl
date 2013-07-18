#=========================================================================
# SimulationTool_comb_test.py
#=========================================================================
# Combinational logic tests for the SimulationTool class.

from Model          import *
from SimulationTool import *
from helpers        import *
from Bits           import Bits

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# PassThrough Tester
#-------------------------------------------------------------------------

def passthrough_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  sim.eval_combinational()
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  sim.eval_combinational()
  assert model.out == 10

#-------------------------------------------------------------------------
# PassThrough Old
#-------------------------------------------------------------------------

class PassThroughOld( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = s.in_.value

def test_PassThroughOld():
  passthrough_tester( PassThroughOld )

#-------------------------------------------------------------------------
# PassThroughBits
#-------------------------------------------------------------------------

class PassThroughBits( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( Bits( nbits ) )
    s.out = OutPort( Bits( nbits ) )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = s.in_

def test_PassThroughBits():
  passthrough_tester( PassThroughBits )

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.v = s.in_

def test_PassThrough():
  passthrough_tester( PassThrough )

#-------------------------------------------------------------------------
# FullAdder
#-------------------------------------------------------------------------

class FullAdder( Model ):
  def __init__( s ):
    s.in0  = InPort ( 1 )
    s.in1  = InPort ( 1 )
    s.cin  = InPort ( 1 )
    s.sum  = OutPort( 1 )
    s.cout = OutPort( 1 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      a = s.in0.value
      b = s.in1.value
      c = s.cin.value
      s.sum.value  = (a ^ b) ^ c
      s.cout.value = (a & b) | (a & c) | (b & c)

def test_FullAdder():
  model = FullAdder( )
  sim = setup_sim( model )
  import itertools
  for x,y,z in itertools.product([ 0,1], [0,1], [0,1] ):
    model.in0.v = x
    model.in1.v = y
    model.cin.v = z
    sim.eval_combinational()
    assert model.sum  == x^y^z
    assert model.cout == ( (x&y)|(x&z)|(y&z) )


#-------------------------------------------------------------------------
# Ripple Carry Adder Tester
#-------------------------------------------------------------------------

def ripplecarryadder_tester( model_type, set, check ):
  model = model_type( 4 )
  sim = setup_sim( model )
  #sim.reset()
  set( model.in0, 2 )
  set( model.in1, 2 )
  sim.eval_combinational()
  check( model.sum, 4 )

  set( model.in0, 11 )
  set( model.in1,  4 )
  sim.eval_combinational()
  check( model.sum, 15 )

  set( model.in0, 9 )
  check( model.sum, 15 )

  sim.eval_combinational()
  check( model.sum, 13 )

  set( model.in0,  5 )
  set( model.in1, 12 )
  check( model.sum, 13 )

  sim.eval_combinational()
  check( model.sum, 1 )

#-------------------------------------------------------------------------
# RippleCarryAdderNoSlice
#-------------------------------------------------------------------------

class RippleCarryAdderNoSlice( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    # Ports
    s.in0 = [ InPort ( 1 ) for x in xrange( nbits ) ]
    s.in1 = [ InPort ( 1 ) for x in xrange( nbits ) ]
    s.sum = [ OutPort( 1 ) for x in xrange( nbits ) ]

  def elaborate_logic( s ):
    # Submodules
    s.adders = [ FullAdder() for i in xrange( s.nbits ) ]
    # s.connections
    for i in xrange( s.nbits ):
      s.connect( s.adders[i].in0, s.in0[i] )
      s.connect( s.adders[i].in1, s.in1[i] )
      s.connect( s.adders[i].sum, s.sum[i] )
    for i in xrange( s.nbits - 1 ):
      s.connect( s.adders[ i + 1 ].cin, s.adders[ i ].cout )
    s.connect( s.adders[0].cin, 0 )

def test_RippleCarryAdderNoSlice():

  def set( signal, value ):
    for i in range( len( signal ) ):
      signal[i].v = value & 1
      value >>= 1

  def check( signal, value ):
    mask = 1
    for i in range( len( signal ) ):
      assert signal[i] == value & mask
      value >>= 1

  ripplecarryadder_tester( RippleCarryAdderNoSlice, set, check )

#-------------------------------------------------------------------------
# RippleCarryAdder
#-------------------------------------------------------------------------

class RippleCarryAdder( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in0 = InPort ( nbits )
    s.in1 = InPort ( nbits )
    s.sum = OutPort( nbits )

  def elaborate_logic( s ):
    s.adders = [ FullAdder() for i in xrange( s.nbits ) ]

    for i in xrange( s.nbits ):
      s.connect( s.adders[i].in0, s.in0[i] )
      s.connect( s.adders[i].in1, s.in1[i] )
      s.connect( s.adders[i].sum, s.sum[i] )
    for i in xrange( s.nbits - 1 ):
      s.connect( s.adders[i+1].cin, s.adders[i].cout )
    s.connect( s.adders[0].cin, 0 )

def test_RippleCarryAdder():
  def set( signal, value ):
    signal.v = value
  def check( signal, value ):
    assert signal.v == value
  ripplecarryadder_tester( RippleCarryAdder, set, check )

#-------------------------------------------------------------------------
# BitBlast Utility Functions
#-------------------------------------------------------------------------

def setup_bit_blast( nbits, groups=None ):
  if not groups:
    model = SimpleBitBlast( nbits )
  else:
    model = ComplexBitBlast( nbits, groups )
  sim = setup_sim( model )
  return model, sim

def verify_bit_blast( port_array, expected ):
  actual = 0
  for i, port in enumerate(port_array):
    shift = i * port.nbits
    actual |= (port.value.uint() << shift)
  assert bin(actual) == bin(expected)

#-------------------------------------------------------------------------
# SimpleBitBlast
#-------------------------------------------------------------------------

class SimpleBitBlast( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = InPort( nbits )
    s.out   = [ OutPort(1) for x in xrange( nbits ) ]

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        s.out[i].value = s.in_.value[i]

def test_SimpleBitBlast_8_to_8x1():
  model, sim = setup_bit_blast( 8 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_SimpleBitBlast_16_to_16x1():
  model, sim = setup_bit_blast( 16 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.v = 0b1111000011001010
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b1111000011001010 )

#-------------------------------------------------------------------------
# ComplexBitBlast
#-------------------------------------------------------------------------

class ComplexBitBlast(Model):
  def __init__( s, nbits, groupings ):
    s.nbits     = nbits
    s.groupings = groupings
    s.in_       = InPort( nbits )
    s.out       = [ OutPort( groupings ) for x in
                    xrange( 0, nbits, groupings ) ]

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      outport_num = 0
      for i in range( 0, s.nbits, s.groupings ):
        s.out[outport_num].value = s.in_.value[i:i+s.groupings]
        outport_num += 1

def test_ComplexBitBlast_8_to_8x1():
  model, sim = setup_bit_blast( 8, 1 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_4x2():
  model, sim = setup_bit_blast( 8, 2 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_2x4():
  model, sim = setup_bit_blast( 8, 4 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_1x8():
  model, sim = setup_bit_blast( 8, 8 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

#-------------------------------------------------------------------------
# BitMerge Utility Functions
#-------------------------------------------------------------------------

def setup_bit_merge( nbits, groups=None ):
  if not groups:
    model = SimpleBitMerge( nbits )
  else:
    model = ComplexBitMerge( nbits, groups )
  sim = setup_sim( model )
  return model, sim

def set_ports( port_array, value ):
  for i, port in enumerate( port_array ):
    shift = i * port.nbits
    # Truncate to ensure no width mismatches -cbatten
    port.value = (value >> shift) & ((1 << port.nbits) - 1)

#-------------------------------------------------------------------------
# SimpleBitMerge
#-------------------------------------------------------------------------

class SimpleBitMerge( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = [ InPort( 1 ) for x in xrange( nbits ) ]
    s.out   = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        s.out.value[i] = s.in_[i].value

def test_SimpleBitMerge_8x1_to_8():
  model, sim = setup_bit_merge( 8 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.value == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101
  model.in_[0].value = 0
  sim.eval_combinational()
  assert model.out.value == 0b01010100
  model.in_[7].value = 1
  sim.eval_combinational()
  assert model.out.value == 0b11010100

def test_SimpleBitMerge_16x1_to_16():
  model, sim = setup_bit_merge( 16 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.value == 0b11110000
  set_ports( model.in_, 0b1111000011001010 )
  sim.eval_combinational()
  assert model.out.value == 0b1111000011001010
  model.in_[0].value = 1
  sim.eval_combinational()
  assert model.out.value == 0b1111000011001011
  model.in_[15].value = 0
  sim.eval_combinational()
  assert model.out.value == 0b0111000011001011

#-------------------------------------------------------------------------
# ComplexBitMerge
#-------------------------------------------------------------------------

class ComplexBitMerge( Model ):
  def __init__( s, nbits, groupings ):
    s.nbits     = nbits
    s.groupings = groupings
    s.in_       = [ InPort( groupings) for x in
                    xrange( 0, nbits, groupings ) ]
    s.out       = OutPort(nbits)

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      inport_num = 0
      for i in range( 0, s.nbits, s.groupings ):
        s.out.value[i:i+s.groupings] = s.in_[inport_num].value
        inport_num += 1

def test_ComplexBitMerge_8x1_to_8():
  model, sim = setup_bit_merge( 8, 1 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_4x2_to_8():
  model, sim = setup_bit_merge( 8, 2 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_2x4_to_8():
  model, sim = setup_bit_merge( 8, 4 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_1x8_to_8():
  model, sim = setup_bit_merge( 8, 8 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

#-------------------------------------------------------------------------
# Self PassThrough
#-------------------------------------------------------------------------
# Test of using 'self' instead of 's'

class SelfPassThrough( Model ):
  def __init__( self, nbits ):
    self.in_   = InPort ( nbits )
    self.out   = OutPort( nbits )

  def elaborate_logic( self ):
    @self.combinational
    def logic():
      self.out.v = self.in_

import pytest
def test_SelfPassThrough():
  passthrough_tester( SelfPassThrough )

#-------------------------------------------------------------------------
# Mux Tester
#-------------------------------------------------------------------------
def mux_tester( model_type ):
  model = model_type( 8, 3 )
  sim = setup_sim( model )
  sim.reset()
  model.in_[0].v = 1
  model.in_[1].v = 2
  model.in_[2].v = 0
  model.sel.v    = 0
  sim.eval_combinational()
  assert model.out == 1
  model.sel.v = 1
  sim.eval_combinational()
  assert model.out == 2
  sim.eval_combinational()
  assert model.out == 2
  model.sel.v = 2
  sim.eval_combinational()
  assert model.out == 0

#-------------------------------------------------------------------------
# Mux
#-------------------------------------------------------------------------

class Mux( Model ):
  def __init__( s, nbits, nports ):
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( get_sel_nbits( nbits ) )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      assert s.sel < len( s.in_ )
      s.out.v = s.in_[ s.sel.uint() ]

def test_Mux():
  mux_tester( Mux )

#-------------------------------------------------------------------------
# IfMux
#-------------------------------------------------------------------------

class IfMux( Model ):
  def __init__( s, nbits, nports=3 ):
    assert nports == 3
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( get_sel_nbits( nbits ) )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      if   s.sel == 0:
        s.out.v = s.in_[ 0 ]
      elif s.sel == 1:
        s.out.v = s.in_[ 1 ]
      elif s.sel == 2:
        s.out.v = s.in_[ 2 ]
      else:
        assert False

def test_IfMux():
  mux_tester( IfMux )

#-------------------------------------------------------------------------
# splitslice_tester
#-------------------------------------------------------------------------
# Test slicing followed by combinational logic

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
# CombSlicePassThrough
#-------------------------------------------------------------------------
class CombSlicePassThrough( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = OutPort ( 2 )

  def elaborate_logic( s ):
    s.pass0  = PassThrough( 2 )
    s.pass1  = PassThrough( 2 )

    @s.combinational
    def comb_logic():
      s.pass0.in_.v = s.in_[0:2]
      s.pass1.in_.v = s.in_[2:4]

    s.connect( s.pass0.out, s.out0 )
    s.connect( s.pass1.out, s.out1 )

def test_CombSlicePassThrough():
  splitslice_tester( CombSlicePassThrough )

#-------------------------------------------------------------------------
# CombSlicePassThroughWire
#-------------------------------------------------------------------------
class CombSlicePassThroughWire( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = OutPort ( 2 )

  def elaborate_logic( s ):
    s.wire0 = Wire( 2 )
    s.wire1 = Wire( 2 )

    @s.combinational
    def comb_logic():
      s.wire0.v    = s.in_[0:2]
      s.wire1.v[:] = s.in_[2:4]

    @s.combinational
    def wire0_logic():
      s.out0.v = s.wire0

    @s.combinational
    def wire1_logic():
      s.out1.v = s.wire1

def test_CombSlicePassThroughWire():
  splitslice_tester( CombSlicePassThroughWire )


#-------------------------------------------------------------------------
# CombSlicePassThroughStruct
#-------------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
class CombSlicePassThroughStruct( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = InPort  ( 2 )

  def elaborate_logic( s ):
    s.pass0  = PassThrough( 2 )
    s.pass1  = PassThrough( 2 )

    s.connect( s.in_[0:2], s.pass0.in_ )
    s.connect( s.in_[2:4], s.pass1.in_ )

    s.connect( s.pass0.out, s.out0 )
    s.connect( s.pass1.out, s.out1 )

def test_CombSlicePassThroughStruct():
  splitslice_tester( CombSlicePassThroughStruct )

#-------------------------------------------------------------------------
# BitMergePassThrough
#-------------------------------------------------------------------------
class BitMergePassThrough( Model ):
  def __init__( s ):
    s.in_ = [ InPort( 1 ) for x in xrange( 8 ) ]
    s.out = OutPort( 8 )

  def elaborate_logic( s ):
    s.merge = SimpleBitMerge( 8 )
    s.pt    = PassThrough( 8 )

    for i in range( 8 ):
      s.connect( s.in_[ i ], s.merge.in_[ i ] )

    s.connect( s.merge.out, s.pt.in_ )
    s.connect( s.pt.out,    s.out    )

def test_BitMergePassThrough():
  model = BitMergePassThrough()
  sim = setup_sim( model )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.value == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101
  model.in_[0].value = 0
  sim.eval_combinational()
  assert model.out.value == 0b01010100
  model.in_[7].value = 1
  sim.eval_combinational()
  assert model.out.value == 0b11010100

#-------------------------------------------------------------------------
# ValueWriteCheck
#-------------------------------------------------------------------------
# Test to verify the value write check logic in SignalValue is correctly
# preventing infinite loops.
class ValueWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_   = InPort  ( 16 )
    s.out   = OutPort ( 16 )

  def elaborate_logic( s ):

    s.temp = [ Wire( 16 ) for x in xrange( 2 ) ]

    @s.combinational
    def comb_logic():
      s.temp[0].value = s.in_     & 0xFFFF
      s.temp[1].value = s.temp[0] & 0xFFFF

    s.connect( s.out, s.temp[1] )

def test_ValueWriteCheck():
  passthrough_tester( ValueWriteCheck )

#-------------------------------------------------------------------------
# SliceWriteCheck
#-------------------------------------------------------------------------
class SliceWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):
    s.m0 = PassThrough( 16 )
    s.connect( s.in_, s.m0.in_ )
    s.connect( s.out, s.m0.out )

def test_SliceWriteCheck():
  model = SliceWriteCheck( 16 )
  model.elaborate()
  sim = setup_sim( model )
  assert model.out == 0

  # Test regular write
  model.in_.v = 8
  sim.eval_combinational()
  assert model.out == 0b1000

  # Write slice directly, passes due to the way impl done
  model.in_[0] = 1
  sim.eval_combinational()
  assert model.out == 0b1001
  model.in_[4:8] = 0b1001
  sim.eval_combinational()
  assert model.out == 0b10011001

  # Write sliced bits, should pass
  model.in_.v[1] = 1
  sim.eval_combinational()
  assert model.out == 0b10011011
  model.in_.v[4:8] = 0b1010
  sim.eval_combinational()
  assert model.out == 0b10101011

  # Slice then write, should fail
  model.in_[0].v = 0
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b10101010
  model.in_[4:8].v = 0b0000
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b00001010

#-------------------------------------------------------------------------
# SliceLogicWriteCheck
#-------------------------------------------------------------------------
# Test storing a Bits slice to a temporary, then writing it
class SliceTempWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):

    @s.combinational
    def logic():
      s.out.v[0:8] = s.in_[0:8]
      x = s.out[8:16]
      x.v          = s.in_[8:16]

import pytest
@pytest.mark.xfail
def test_SliceTempWriteCheck():
  model = SliceTempWriteCheck( 16 )
  model.elaborate()
  sim = setup_sim( model )
  assert model.out == 0

  model.in_.value = 0x00AA
  sim.eval_combinational()
  assert model.out == 0x00AA

  model.in_.value = 0xAA00
  sim.eval_combinational()
  assert model.out == 0xAA00
