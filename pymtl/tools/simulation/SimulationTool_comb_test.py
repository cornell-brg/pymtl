#=======================================================================
# SimulationTool_comb_test.py
#=======================================================================
# Combinational logic tests for the SimulationTool class.

import pytest

from pymtl import *
from pymtl import PyMTLError

from SimulationTool_seq_test import setup_sim, local_setup_sim

#-----------------------------------------------------------------------
# .next in @combinational
#-----------------------------------------------------------------------
def test_NextInCombinationalBlock( setup_sim ):
  class BuggyClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(1), OutPort(1)
      @s.combinational
      def logic():
        s.out.next = s.in_
  with pytest.raises( PyMTLError ):
    model, sim = setup_sim( BuggyClass() )

#-----------------------------------------------------------------------
# missing .value in @combinational
#-----------------------------------------------------------------------
def test_MissingValueInCombinationalBlock( setup_sim ):

  class BuggyClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(1), OutPort(1)
      @s.combinational
      def logic():
        s.out = s.in_
  with pytest.raises( PyMTLError ):
    model, sim = setup_sim( BuggyClass() )

#-----------------------------------------------------------------------
# missing .value in @combinational list
#-----------------------------------------------------------------------
def test_MissingListValueInCombinationalBlock( setup_sim ):
  class BuggyClass( Model ):
    def __init__( s ):
      s.in_, s.out = InPort(1), OutPort[4](1)
      @s.combinational
      def logic():
        for i in range(4):
          s.out[i] = s.in_
  with pytest.raises( PyMTLError ):
    model, sim = setup_sim( BuggyClass() )

#-----------------------------------------------------------------------
# PassThrough Tester
#-----------------------------------------------------------------------

def passthrough_tester( model_type, setup_sim ):
  model      = model_type( 16 )
  model, sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  sim.eval_combinational()
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  sim.eval_combinational()
  assert model.out == 10

#-----------------------------------------------------------------------
# PassThrough Old
#-----------------------------------------------------------------------

class PassThroughOld( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = s.in_.value

def test_PassThroughOld( setup_sim ):
  passthrough_tester( PassThroughOld, setup_sim )

#-----------------------------------------------------------------------
# PassThroughBits
#-----------------------------------------------------------------------

class PassThroughBits( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( Bits( nbits ) )
    s.out = OutPort( Bits( nbits ) )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = s.in_

def test_PassThroughBits( setup_sim ):
  passthrough_tester( PassThroughBits, setup_sim )

#-----------------------------------------------------------------------
# PassThrough
#-----------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.v = s.in_

def test_PassThrough( setup_sim ):
  passthrough_tester( PassThrough, setup_sim )

#-----------------------------------------------------------------------
# FullAdder
#-----------------------------------------------------------------------

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

def test_FullAdder( setup_sim ):
  model      = FullAdder( )
  model, sim = setup_sim( model )
  import itertools
  for x,y,z in itertools.product([ 0,1], [0,1], [0,1] ):
    model.in0.v = x
    model.in1.v = y
    model.cin.v = z
    sim.eval_combinational()
    assert model.sum  == x^y^z
    assert model.cout == ( (x&y)|(x&z)|(y&z) )


#-----------------------------------------------------------------------
# Ripple Carry Adder Tester
#-----------------------------------------------------------------------

def ripplecarryadder_tester( setup_sim, model_type, set, check ):
  model      = model_type( 4 )
  model, sim = setup_sim( model )
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

#-----------------------------------------------------------------------
# RippleCarryAdderNoSlice
#-----------------------------------------------------------------------

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

def test_RippleCarryAdderNoSlice( setup_sim ):

  def set( signal, value ):
    for i in range( len( signal ) ):
      signal[i].v = value & 1
      value >>= 1

  def check( signal, value ):
    mask = 1
    for i in range( len( signal ) ):
      assert signal[i] == value & mask
      value >>= 1

  ripplecarryadder_tester( setup_sim, RippleCarryAdderNoSlice, set, check )

#-----------------------------------------------------------------------
# RippleCarryAdder
#-----------------------------------------------------------------------

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

def test_RippleCarryAdder( setup_sim ):
  def set( signal, value ):
    signal.v = value
  def check( signal, value ):
    assert signal.v == value
  ripplecarryadder_tester( setup_sim, RippleCarryAdder, set, check )

#-----------------------------------------------------------------------
# BitBlast Utility Functions
#-----------------------------------------------------------------------

def setup_bit_blast( setup_sim, nbits, groups=None ):
  if not groups:
    model      = SimpleBitBlast( nbits )
  else:
    model      = ComplexBitBlast( nbits, groups )
  model, sim = setup_sim( model )
  return model, sim

def verify_bit_blast( port_array, expected ):
  actual = 0
  for i, port in enumerate(port_array):
    shift = i * port.nbits
    actual |= (port.value.uint() << shift)
  assert bin(actual) == bin(expected)

#-----------------------------------------------------------------------
# SimpleBitBlast
#-----------------------------------------------------------------------

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

def test_SimpleBitBlast_8_to_8x1( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 8 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_SimpleBitBlast_16_to_16x1( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 16 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.v = 0b1111000011001010
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b1111000011001010 )

#-----------------------------------------------------------------------
# ComplexBitBlast
#-----------------------------------------------------------------------

class ComplexBitBlast( Model ):
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

def test_ComplexBitBlast_8_to_8x1( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 8, 1 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_4x2( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 8, 2 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_2x4( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 8, 4 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

def test_ComplexBitBlast_8_to_1x8( setup_sim ):
  model, sim = setup_bit_blast( setup_sim, 8, 8 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_bit_blast( model.out, 0b01010101 )

#-----------------------------------------------------------------------
# BitMerge Utility Functions
#-----------------------------------------------------------------------

def setup_bit_merge( setup_sim, nbits, groups=None ):
  if not groups:
    model      = SimpleBitMerge( nbits )
  else:
    model      = ComplexBitMerge( nbits, groups )
  model, sim = setup_sim( model )
  return model, sim

def set_ports( port_array, value ):
  for i, port in enumerate( port_array ):
    shift = i * port.nbits
    # Truncate to ensure no width mismatches -cbatten
    port.value = (value >> shift) & ((1 << port.nbits) - 1)

#-----------------------------------------------------------------------
# SimpleBitMerge
#-----------------------------------------------------------------------

class SimpleBitMerge( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = [ InPort( 1 ) for x in xrange( nbits ) ]
    s.out   = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        s.out[i].value = s.in_[i].value

def test_SimpleBitMerge_8x1_to_8( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 8 )
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

def test_SimpleBitMerge_16x1_to_16( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 16 )
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

#-----------------------------------------------------------------------
# ComplexBitMerge
#-----------------------------------------------------------------------

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
        s.out[i:i+s.groupings].value = s.in_[inport_num].value
        inport_num += 1

def test_ComplexBitMerge_8x1_to_8( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 8, 1 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_4x2_to_8( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 8, 2 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_2x4_to_8( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 8, 4 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexBitMerge_1x8_to_8( setup_sim ):
  model, sim = setup_bit_merge( setup_sim, 8, 8 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

#-----------------------------------------------------------------------
# Self PassThrough
#-----------------------------------------------------------------------
# Test of using 'self' instead of 's'

class SelfPassThrough( Model ):
  def __init__( self, nbits ):
    self.in_   = InPort ( nbits )
    self.out   = OutPort( nbits )

  def elaborate_logic( self ):
    @self.combinational
    def logic():
      self.out.v = self.in_

def test_SelfPassThrough( setup_sim ):
  passthrough_tester( SelfPassThrough, setup_sim )

#-----------------------------------------------------------------------
# Mux Tester
#-----------------------------------------------------------------------
def mux_tester( setup_sim, model_type ):
  model      = model_type( 8, 3 )
  model, sim = setup_sim( model )
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

#-----------------------------------------------------------------------
# Mux
#-----------------------------------------------------------------------

class Mux( Model ):
  def __init__( s, nbits, nports ):
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( clog2( nports ) )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      assert s.sel < len( s.in_ )
      s.out.v = s.in_[ s.sel ]

def test_Mux( setup_sim ):
  mux_tester( setup_sim, Mux )

#-----------------------------------------------------------------------
# IfMux
#-----------------------------------------------------------------------

class IfMux( Model ):
  def __init__( s, nbits, nports=3 ):
    assert nports == 3
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( clog2( nbits ) )
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

def test_IfMux( setup_sim ):
  mux_tester( setup_sim, IfMux )

#-----------------------------------------------------------------------
# SubscriptTemp
#-----------------------------------------------------------------------
class SubscriptTemp( Model ):
  def __init__( s, nbits, nports=3 ):
    assert nports == 3
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( clog2( nbits ) )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      if   s.sel == 0: temp = s.in_[ 0 ]
      elif s.sel == 1: temp = s.in_[ 1 ]
      elif s.sel == 2: temp = s.in_[ 2 ]
      else:            assert False
      s.out.v = temp

def test_SubscriptTemp( setup_sim ):
  mux_tester( setup_sim, SubscriptTemp )

#-----------------------------------------------------------------------
# splitslice_tester
#-----------------------------------------------------------------------
# Test slicing followed by combinational logic

def splitslice_tester( setup_sim, model_type ):
  model      = model_type()
  model, sim = setup_sim( model )
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

#-----------------------------------------------------------------------
# CombSlicePassThrough
#-----------------------------------------------------------------------
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

def test_CombSlicePassThrough( setup_sim ):
  splitslice_tester( setup_sim, CombSlicePassThrough )

#-----------------------------------------------------------------------
# CombSlicePassThroughWire
#-----------------------------------------------------------------------
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
      # This doesn't work, should it?
      #s.wire1[:].v = s.in_[2:4]
      s.wire1.v = s.in_[2:4]

    @s.combinational
    def wire0_logic():
      s.out0.v = s.wire0

    @s.combinational
    def wire1_logic():
      s.out1.v = s.wire1

def test_CombSlicePassThroughWire( setup_sim ):
  splitslice_tester( setup_sim, CombSlicePassThroughWire )


#-----------------------------------------------------------------------
# CombSlicePassThroughStruct
#-----------------------------------------------------------------------
# TODO: move to SimulationTool_mix_test.py
class CombSlicePassThroughStruct( Model ):
  def __init__( s ):
    s.in_  = InPort  ( 4 )
    s.out0 = OutPort ( 2 )
    s.out1 = OutPort ( 2 )

  def elaborate_logic( s ):
    s.pass0  = PassThrough( 2 )
    s.pass1  = PassThrough( 2 )

    s.connect( s.in_[0:2], s.pass0.in_ )
    s.connect( s.in_[2:4], s.pass1.in_ )

    s.connect( s.pass0.out, s.out0 )
    s.connect( s.pass1.out, s.out1 )

def test_CombSlicePassThroughStruct( setup_sim ):
  splitslice_tester( setup_sim, CombSlicePassThroughStruct )

#-----------------------------------------------------------------------
# BitMergePassThrough
#-----------------------------------------------------------------------
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

def test_BitMergePassThrough( setup_sim ):
  model      = BitMergePassThrough()
  model, sim = setup_sim( model )
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

#-----------------------------------------------------------------------
# ValueWriteCheck
#-----------------------------------------------------------------------
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

def test_ValueWriteCheck( setup_sim ):
  passthrough_tester( ValueWriteCheck, setup_sim )

#-----------------------------------------------------------------------
# SliceWriteCheck
#-----------------------------------------------------------------------
# Test updates to slices.
class SliceWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):
    s.m0 = PassThrough( 16 )
    s.connect( s.in_, s.m0.in_ )
    s.connect( s.out, s.m0.out )

def test_SliceWriteCheck( setup_sim ):

  model      = SliceWriteCheck( 16 )
  model, sim = setup_sim( model )
  assert model.out == 0

  # Test regular write
  model.in_.v = 8
  sim.eval_combinational()
  assert model.out == 0b1000

  # Slice then .v, should pass
  model.in_[0].v = 1
  sim.eval_combinational()
  assert model.out == 0b1001
  model.in_[4:8].v = 0b1001
  sim.eval_combinational()
  assert model.out == 0b10011001

  # Test regular write
  model.in_.v = 8
  sim.eval_combinational()
  assert model.out == 0b1000

  # Only slice, should fail
  model.in_[0] = 1
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b1001
  model.in_[4:8] = 0b1001
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b10011001

  # Test regular write
  model.in_.v = 8
  sim.eval_combinational()
  assert model.out == 0b1000

  # .v then slice, should fail
  model.in_.v[0] = 1
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b1001
  model.in_.v[4:8] = 0b1001
  sim.eval_combinational()
  with pytest.raises( AssertionError ):
    assert model.out == 0b10011001

#-----------------------------------------------------------------------
# SliceLogicWriteCheck
#-----------------------------------------------------------------------
# Test storing a Bits slice to a temporary, then writing it
class SliceTempWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):

    @s.combinational
    def logic():
      s.out[0:8].v = s.in_[0:8]
      x = s.out[8:16]
      x.v          = s.in_[8:16]

def test_SliceTempWriteCheck( setup_sim ):
  model      = SliceTempWriteCheck( 16 )
  model, sim = setup_sim( model )
  assert model.out == 0

  model.in_.value = 0x00AA
  sim.eval_combinational()
  assert model.out == 0x00AA

  model.in_.value = 0xAA00
  sim.eval_combinational()
  assert model.out == 0xAA00

#-----------------------------------------------------------------------
# MultipleWrites
#-----------------------------------------------------------------------
# Test to catch strange simulator behavior
class MultipleWrites( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = 4
      s.out.value = s.in_

def test_MultipleWrites( setup_sim ):
  passthrough_tester( MultipleWrites, setup_sim )

#-----------------------------------------------------------------------
# PortBundle
#-----------------------------------------------------------------------
# Test to catch strange simulator behavior
class TempBundle( PortBundle ):
  def __init__( s, nbits ):
    s.a = InPort( nbits )
    s.b = InPort( nbits )

InBundle, OutBundle = create_PortBundles( TempBundle )

class BundleChild( Model ):
  def __init__( s, nbits ):
    s.in_ = InBundle ( nbits )
    s.out = OutBundle( nbits )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.a.value = s.in_.b
      s.out.b.value = s.in_.a

def test_BundleComb( setup_sim ):
  model      = BundleChild( 16 )
  model, sim = setup_sim( model )
  model.in_.a.value = 2
  model.in_.b.value = 3
  sim.eval_combinational()
  assert model.out.a == 3
  assert model.out.b == 2
  model.in_.a.value = 10
  model.in_.b.value = 4
  sim.eval_combinational()
  assert model.out.a == 4
  assert model.out.b == 10

class BundleChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = InBundle ( nbits )
    s.out   = OutBundle( nbits )
  def elaborate_logic( s ):
    s.submod = [ BundleChild( s.nbits ) for x in range( 2 ) ]
    s.connect( s.in_,           s.submod[0].in_ )
    s.connect( s.submod[0].out, s.submod[1].in_ )
    s.connect( s.submod[1].out, s.out           )

def test_BundleChain( setup_sim ):
  model      = BundleChain( 16 )
  model, sim = setup_sim( model )
  model.in_.a.value = 2
  model.in_.b.value = 3
  sim.eval_combinational()
  assert model.out.a == 2
  assert model.out.b == 3
  model.in_.a.value = 10
  model.in_.b.value = 4
  sim.eval_combinational()
  assert model.out.a == 10
  assert model.out.b == 4

#-----------------------------------------------------------------------
# GlobalConstants
#-----------------------------------------------------------------------
CONSTANT_A = 4
CONSTANT_B = 7
class GlobalConstants( Model ):
  def __init__( s ):
    s.sel = InPort ( 1 )
    s.out = OutPort( 8 )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.value = CONSTANT_A if s.sel else CONSTANT_B

def test_GlobalConstants( setup_sim ):
  model      = GlobalConstants()
  model, sim = setup_sim( model )
  model.sel.value = 1
  sim.eval_combinational()
  assert model.out == 4
  model.sel.value = 0
  sim.eval_combinational()
  assert model.out == 7

#-----------------------------------------------------------------------
# GlobalConstantsBits
#-----------------------------------------------------------------------
CONSTANT_C = Bits(8, 4)
CONSTANT_D = Bits(8, 7)
def test_GlobalConstantsBits( setup_sim ):
  class GlobalConstantsBits( Model ):
    def __init__( s ):
      s.sel = InPort ( 1 )
      s.out = OutPort( 8 )
    def elaborate_logic( s ):
      @s.combinational
      def logic():
        s.out.value = CONSTANT_C if s.sel else CONSTANT_D

  model      = GlobalConstantsBits()
  model, sim = setup_sim( model )
  model.sel.value = 1
  sim.eval_combinational()
  assert model.out == 4
  model.sel.value = 0
  sim.eval_combinational()
  assert model.out == 7

#-----------------------------------------------------------------------
# IntTemporaries
#-----------------------------------------------------------------------
class IntTemporaries( Model ):
  def __init__( s ):

    s.STATE_A = 0
    s.STATE_B = 1
    s.STATE_C = 2

    s.go     = InPort ( 1 )
    s.state  = InPort ( 2 )
    s.update = OutPort( 2 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():

      next_state = s.state

      if   s.state == s.STATE_A and s.go:
        next_state = s.STATE_B
      elif s.state == s.STATE_B:
        next_state = s.STATE_C
      elif s.state == s.STATE_C and s.go:
        next_state = s.STATE_A

      s.update.value = next_state

def temp_tester( setup_sim, ModelType ):
  model      = ModelType()
  A, B, C    = model.STATE_A, model.STATE_B, model.STATE_C
  model, sim = setup_sim( model )

  # TODO: add constant params to Verilog translated harnesses?
  #model.state.value = model.STATE_A

  model.state.value = A
  model.go   .value = 0
  sim.eval_combinational()
  assert model.update == A

  model.state.value = A
  model.go   .value = 1
  sim.eval_combinational()
  assert model.update == B

  model.state.value = B
  model.go   .value = 1
  sim.eval_combinational()
  assert model.update == C

  model.state.value = B
  model.go   .value = 0
  sim.eval_combinational()
  assert model.update == C

  model.state.value = C
  model.go   .value = 1
  sim.eval_combinational()
  assert model.update == A

  model.state.value = C
  model.go   .value = 0
  sim.eval_combinational()
  assert model.update == C

def test_IntTemporaries( setup_sim ):
  temp_tester( setup_sim, IntTemporaries )

class IntSubTemporaries( IntTemporaries ):
  def elaborate_logic( s ):

    s.submod = PassThrough( 2 )
    s.connect( s.state, s.submod.in_ )

    @s.combinational
    def logic():

      next_state = s.submod.out

      if   s.state == s.STATE_A and s.go:
        next_state = s.STATE_B
      elif s.state == s.STATE_B:
        next_state = s.STATE_C
      elif s.state == s.STATE_C and s.go:
        next_state = s.STATE_A

      s.update.value = next_state

def test_IntSubTemporaries( setup_sim ):
  temp_tester( setup_sim, IntSubTemporaries )

#-----------------------------------------------------------------------
# Concat
#-----------------------------------------------------------------------
class Concat( Model ):
  def __init__( s ):
    s.in0  = InPort ( 1 )
    s.in1  = InPort ( 4 )
    s.in2  = InPort ( 2 )
    s.out0 = OutPort( 1+4+2 )
    s.out1 = OutPort( 1+4+2 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out0.value = concat( s.in0, s.in1, s.in2 )
      temp = concat( s.in0, s.in1, s.in2 )
      s.out1.value = temp

def test_Concat( setup_sim ):
  model      = Concat()
  model, sim = setup_sim( model )
  def test( i0, i1, i2, out ):
    model.in0.value = i0
    model.in1.value = i1
    model.in2.value = i2
    sim.eval_combinational()
    assert model.out0 == out
    assert model.out1 == out
  test( 1, 1,1, 0b1000101 )
  test( 0, 0,0, 0b0000000 )
  test( 1,15,3, 0b1111111 )
  test( 0, 8,2, 0b0100010 )
  test( 1, 5,1, 0b1010101 )

#-----------------------------------------------------------------------
# MultipleTempAssign
#-----------------------------------------------------------------------

class MultipleTempAssign( Concat ):
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out0.value = concat( s.in0, s.in1, s.in2 )
      if s.in0: cs = concat( s.in0, s.in1, s.in2 )
      else:     cs = concat( s.in0, s.in1, s.in2 )
      s.out1.value = cs

def test_MultipleTempAssign( setup_sim ):
  model      = MultipleTempAssign()
  model, sim = setup_sim( model )
  def test( i0, i1, i2, out ):
    model.in0.value = i0
    model.in1.value = i1
    model.in2.value = i2
    sim.eval_combinational()
    assert model.out0 == out
    assert model.out1 == out
  test( 1, 1,1, 0b1000101 )
  test( 0, 0,0, 0b0000000 )
  test( 1,15,3, 0b1111111 )
  test( 0, 8,2, 0b0100010 )
  test( 1, 5,1, 0b1010101 )

#-----------------------------------------------------------------------
# ReduceAND
#-----------------------------------------------------------------------
class ReduceAND( Model ):
  def __init__( s, nbits ):
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( 1 )
    s.out1 = OutPort( 1 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out0.value = reduce_and( s.in_ )
      temp = reduce_and( s.in_ )
      s.out1.value = temp

def test_ReduceAND( setup_sim ):
  model      = ReduceAND( 4 )
  model, sim = setup_sim( model )

  for i, o in zip([0b1111, 0b1010, 0b0101, 0b0000],[1,0,0,0]):
    model.in_.value = i
    sim.eval_combinational()
    assert model.out0 == o
    assert model.out1 == o

#-----------------------------------------------------------------------
# ReduceOR
#-----------------------------------------------------------------------
class ReduceOR( Model ):
  def __init__( s, nbits ):
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( 1 )
    s.out1 = OutPort( 1 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out0.value = reduce_or( s.in_ )
      temp = reduce_or( s.in_ )
      s.out1.value = temp

def test_ReduceOR( setup_sim ):
  model      = ReduceOR( 4 )
  model, sim = setup_sim( model )

  for i, o in zip([0b1111, 0b1010, 0b0101, 0b0000],[1,1,1,0]):
    model.in_.value = i
    sim.eval_combinational()
    assert model.out0 == o
    assert model.out1 == o

#-----------------------------------------------------------------------
# ReduceXOR
#-----------------------------------------------------------------------
class ReduceXOR( Model ):
  def __init__( s, nbits ):
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( 1 )
    s.out1 = OutPort( 1 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out0.value = reduce_xor( s.in_ )
      temp = reduce_xor( s.in_ )
      s.out1.value = temp

def test_ReduceXOR( setup_sim ):
  model      = ReduceXOR( 4 )
  model, sim = setup_sim( model )

  for i, o in zip([0b1111, 0b1010, 0b0101, 0b0000, 0b1001,
                   0b1110, 0b1101, 0b1011, 0b0111,
                   0b0001, 0b0010, 0b0100, 0b1000,],
                  [0,0,0,0,0,
                   1,1,1,1,
                   1,1,1,1,]
                  ):
    model.in_.value = i
    sim.eval_combinational()
    assert model.out0 == o
    assert model.out1 == o

#-----------------------------------------------------------------------
# NestedLoops
#-----------------------------------------------------------------------
class NestedLoops( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort [ nbits ]( nbits )
    s.out = OutPort[ nbits ]( nbits )
    s.nbits = nbits

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        for j in range( s.nbits ):
          s.out[i][j].value = s.in_[j][i]

class NestedLoopsStruct( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort [ nbits ]( nbits )
    s.out = OutPort[ nbits ]( nbits )
    s.nbits = nbits

  def elaborate_logic( s ):
    for i in range( s.nbits ):
      for j in range( s.nbits ):
        s.connect( s.out[i][j], s.in_[j][i] )

def verify_nested_loops( setup_sim, ModelType ):
  model      = ModelType( 3 )
  model, sim = setup_sim( model )

  model.in_[0].value = 0b111
  model.in_[1].value = 0b000
  model.in_[2].value = 0b010
  sim.eval_combinational()
  assert model.out[0] == 0b001
  assert model.out[1] == 0b101
  assert model.out[2] == 0b001
  model.in_[0].value = 0b011
  model.in_[1].value = 0b110
  model.in_[2].value = 0b101
  sim.eval_combinational()
  assert model.out[0] == 0b101
  assert model.out[1] == 0b011
  assert model.out[2] == 0b110

def test_NestedLoopsStruct( setup_sim ):
  verify_nested_loops( setup_sim, NestedLoopsStruct )

def test_NestedLoops( setup_sim ):
  verify_nested_loops( setup_sim, NestedLoops )

#-----------------------------------------------------------------------
# ListOfPortBundles
#-----------------------------------------------------------------------
class ListOfPortBundlesComb( Model ):
  def __init__( s ):
    s.in_ = [ InBundle ( 4 ) for x in range(2) ]
    s.out = [ OutBundle( 4 ) for x in range(2) ]

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( 2 ):
        s.out[i].a.value = s.in_[i].b
        s.out[i].b.value = s.in_[i].a

def test_ListOfPortBundles( setup_sim ):
  model      = ListOfPortBundlesComb()
  model, sim = setup_sim( model )

  model.in_[0].a.value = 2
  model.in_[0].b.value = 3
  model.in_[1].a.value = 4
  model.in_[1].b.value = 5
  sim.eval_combinational()
  assert model.out[0].a == 3
  assert model.out[0].b == 2
  assert model.out[1].a == 5
  assert model.out[1].b == 4

#-----------------------------------------------------------------------
# ListOfModules
#-----------------------------------------------------------------------
class ListOfModules( Model ):
  def __init__( s ):
    s.in_ = [ InPort ( 4 ) for x in range(2) ]
    s.out = [ OutPort( 4 ) for x in range(2) ]

  def elaborate_logic( s ):
    s.mod = [ PassThrough( 4 ) for x in range(2) ]

    @s.combinational
    def logic():
      for i in range( 2 ):
        s.mod[i].in_.value = s.in_[i]
        s.out[i].value     = s.mod[i].out

def list_of_modules_tester( setup_sim, ModelType ):
  model      = ModelType()
  model, sim = setup_sim( model )

  model.in_[0].value = 2
  model.in_[1].value = 4
  sim.eval_combinational()
  assert model.out[0] == 2
  assert model.out[1] == 4
  model.in_[0].value = 5
  model.in_[1].value = 6
  sim.eval_combinational()
  assert model.out[0] == 5
  assert model.out[1] == 6

def test_ListOfModules( setup_sim ):
  list_of_modules_tester( setup_sim, ListOfModules )

#-----------------------------------------------------------------------
# ListOfModulesBitslice
#-----------------------------------------------------------------------
class ListOfModulesBitslice( Model ):
  def __init__( s ):
    s.in_ = [ InPort ( 4 ) for x in range(2) ]
    s.out = [ OutPort( 4 ) for x in range(2) ]

  def elaborate_logic( s ):
    s.mod = [ PassThrough( 4 ) for x in range(2) ]

    @s.combinational
    def logic():
      for i in range( 2 ):
        for j in range( 4 ):
          s.mod[i].in_[j].value = s.in_[i][j]
          s.out[i][j].value     = s.mod[i].out[j]

def test_ListOfModulesBitslice( setup_sim ):
  list_of_modules_tester( setup_sim, ListOfModulesBitslice )

#-----------------------------------------------------------------------
# ListOfWires
#-----------------------------------------------------------------------
class ListOfWires( Model ):
  def __init__( s ):
    s.in_ = [ InPort ( 4 ) for x in range(2) ]
    s.out = [ OutPort( 4 ) for x in range(2) ]

  def elaborate_logic( s ):
    s.wire_rd = [ Wire( 4 ) for x in range(2) ]
    s.wire_wr = [ Wire( 4 ) for x in range(2) ]

    for i in range(2):
      s.connect( s.in_[i], s.wire_rd[i] )
      s.connect( s.out[i], s.wire_wr[i] )

    @s.combinational
    def logic():
      for i in range(2):
        s.wire_wr[i].value = s.wire_rd[i]

def test_ListOfWires( setup_sim ):
  list_of_modules_tester( setup_sim, ListOfWires )

#-----------------------------------------------------------------------
# ListOfMixedUseWires
#-----------------------------------------------------------------------
# This works fine in Python Simulation, but does not translate into
# Verilog correctly because we assume all elements of a list of wires
# will have the same assignment structure!
class ListOfMixedUseWires( Model ):
  def __init__( s ):
    s.in_ = [ InPort ( 4 ) for x in range(2) ]
    s.out = [ OutPort( 4 ) for x in range(2) ]

  def elaborate_logic( s ):
    s.wires = [ Wire( 4 ) for x in range(2) ]

    s.connect( s.in_[0], s.wires[0] )

    @s.combinational
    def logic():
      s.out  [0].value = s.wires[0]
      s.wires[1].value = s.in_  [1]

    s.connect( s.out[1], s.wires[1] )

def test_ListOfMixedUseWires( setup_sim ):
  list_of_modules_tester( setup_sim, ListOfMixedUseWires )

#-----------------------------------------------------------------------
# RaiseException
#-----------------------------------------------------------------------
class RaiseException( Model ):
  def __init__( s ):
    s.in_ = InPort ( 2 )
    s.out = OutPort( 2 )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      if s.in_ < 3: s.out.value = s.in_
      else:         raise Exception("Invalid state!")

def test_RaiseException( setup_sim ):
  model      = RaiseException()
  model, sim = setup_sim( model )

  model.in_.value = 0; sim.cycle(); assert model.out == 0
  model.in_.value = 1; sim.cycle(); assert model.out == 1
  model.in_.value = 2; sim.cycle(); assert model.out == 2
  with pytest.raises( Exception ):
    model.in_.value = 3; sim.cycle()

#-----------------------------------------------------------------------
# SliceConst
#-----------------------------------------------------------------------
A = slice(0,2)
class SliceConst( Model ):
  B = slice(2,4)
  def __init__( s ):
    s.in_ = InPort ( 6 )
    s.out = OutPort( 6 )
    s.C   = slice(4,6)

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out[   A ].value = s.in_[   A ]
      s.out[ s.B ].value = s.in_[ s.B ]
      s.out[ s.C ].value = s.in_[ s.C ]

def test_SliceConst( setup_sim ):
  model      = SliceConst()
  model, sim = setup_sim( model )

  model.in_.value = 0b101010
  sim.eval_combinational()
  assert model.out == 0b101010
  model.in_.value = 0b111000
  sim.eval_combinational()
  assert model.out == 0b111000

#-----------------------------------------------------------------------
# BitsConst
#-----------------------------------------------------------------------
class BitsConst( Model ):
  def __init__( s ):
    s.in_  = InPort (2)
    s.out1 = OutPort(8)
    #s.out2 = OutPort(8)
  def elaborate_logic( s ):
    # TODO: Bits stored as members do not simulate!
    #s.a = Bits(2,   1)
    #s.b = Bits(2, 0x1)
    #s.c = Bits(2,0b10)
    @s.combinational
    def logic():
      s.out1.value = concat( s.in_, Bits(2, 0), Bits(2, 0x1), Bits(2, 0b10) )
      #s.out2.value = concat( s.in_, s.a, s.b, s.c )

def test_BitsConst( setup_sim ):
  model      = BitsConst()
  model, sim = setup_sim( model )

  model.in_.value = 0b10
  sim.eval_combinational()
  assert model.out1 == 0b10000110
  #assert model.out2 == 0b10010110
  model.in_.value = 0b11
  sim.eval_combinational()
  assert model.out1 == 0b11000110
  #assert model.out2 == 0b11010110

#-----------------------------------------------------------------------
# SubmodPortList
#-----------------------------------------------------------------------
class SubmodPortList( Model ):
  def __init__( s ):
    s.in_ = InPort [2]( 4 )
    s.out = OutPort[2]( 4 )
  def elaborate_logic( s ):
    s.submod = ListOfWires()
    @s.combinational
    def logic_in():
      s.submod.in_[0].value = s.in_[0]
      s.submod.in_[1].value = s.in_[1]
    @s.combinational
    def logic_out():
      s.out[0].value = s.submod.out[0]
      s.out[1].value = s.submod.out[1]

def test_SubmodPortList( setup_sim ):
  list_of_modules_tester( setup_sim, SubmodPortList )

#-----------------------------------------------------------------------
# SubmodPortBundles
#-----------------------------------------------------------------------
class SubmodPortBundles( Model ):
  def __init__( s ):
    s.in_ = InBundle ( 4 )
    s.out = OutBundle( 4 )
  def elaborate_logic( s ):
    s.submod = BundleChild( 4 )
    @s.combinational
    def logic1():
      s.submod.in_.a.value = s.in_.a
      s.submod.in_.b.value = s.in_.b
    @s.combinational
    def logic2():
      s.out.a.value = s.submod.out.a
      s.out.b.value = s.submod.out.b

def test_SubmodPortBundles( setup_sim ):

  model      = SubmodPortBundles()
  model, sim = setup_sim( model )
  model.in_.a.value = 2
  model.in_.b.value = 3
  sim.eval_combinational()
  assert model.out.a == 3
  assert model.out.b == 2
  model.in_.a.value = 10
  model.in_.b.value = 4
  sim.eval_combinational()
  assert model.out.a == 4
  assert model.out.b == 10

#-----------------------------------------------------------------------
# ListOfSubmodPortBundles
#-----------------------------------------------------------------------
class ListOfSubmodPortBundles( Model ):
  def __init__( s ):
    s.in_ = InBundle [2]( 4 )
    s.out = OutBundle[2]( 4 )
  def elaborate_logic( s ):
    s.submod = BundleChild[2]( 4 )
    @s.combinational
    def logic1():
      for i in range(2):
        s.submod[i].in_.a.value = s.in_[i].a
        s.submod[i].in_.b.value = s.in_[i].b
    @s.combinational
    def logic2():
      for i in range(2):
        s.out[i].a.value = s.submod[i].out.a
        s.out[i].b.value = s.submod[i].out.b

def test_ListOfSubmodPortBundles( setup_sim ):

  model      = ListOfSubmodPortBundles()
  model, sim = setup_sim( model )
  model.in_[0].a.value = 2
  model.in_[0].b.value = 3
  model.in_[1].a.value = 4
  model.in_[1].b.value = 5
  sim.eval_combinational()
  assert model.out[0].a == 3
  assert model.out[0].b == 2
  assert model.out[1].a == 5
  assert model.out[1].b == 4
  model.in_[0].a.value = 10
  model.in_[0].b.value = 4
  model.in_[1].a.value = 10
  model.in_[1].b.value = 4
  sim.eval_combinational()
  assert model.out[0].a == 4
  assert model.out[0].b == 10
  assert model.out[1].a == 4
  assert model.out[1].b == 10

#-----------------------------------------------------------------------
# SubmodPortBundlesList
#-----------------------------------------------------------------------
class BundleListChild( Model ):
  def __init__( s, nbits ):
    s.in_ = InBundle [2]( nbits )
    s.out = OutBundle[2]( nbits )
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range(2):
        s.out[i].a.value = s.in_[i].b
        s.out[i].b.value = s.in_[i].a

class SubmodPortBundlesList( Model ):
  def __init__( s ):
    s.in_ = InBundle [2]( 4 )
    s.out = OutBundle[2]( 4 )
  def elaborate_logic( s ):
    s.submod = BundleListChild( 4 )
    @s.combinational
    def logic1():
      for i in range(2):
        s.submod.in_[i].a.value = s.in_[i].a
        s.submod.in_[i].b.value = s.in_[i].b
    @s.combinational
    def logic2():
      for i in range(2):
        s.out[i].a.value = s.submod.out[i].a
        s.out[i].b.value = s.submod.out[i].b

def test_SubmodPortBundlesList( setup_sim ):

  model      = SubmodPortBundlesList()
  model, sim = setup_sim( model )
  model.in_[0].a.value = 2
  model.in_[0].b.value = 3
  model.in_[1].a.value = 4
  model.in_[1].b.value = 5
  sim.eval_combinational()
  assert model.out[0].a == 3
  assert model.out[0].b == 2
  assert model.out[1].a == 5
  assert model.out[1].b == 4
  model.in_[0].a.value = 10
  model.in_[0].b.value = 4
  model.in_[1].a.value = 10
  model.in_[1].b.value = 4
  sim.eval_combinational()
  assert model.out[0].a == 4
  assert model.out[0].b == 10
  assert model.out[1].a == 4
  assert model.out[1].b == 10

#-----------------------------------------------------------------------
# VariablePartSelects
#-----------------------------------------------------------------------
class VariablePartSelects( Model ):
  def __init__( s, nchunks ):
    s.in_ = InPort ( nchunks*4 )
    s.out = OutPort( nchunks*4 )
    s.chunks = nchunks

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.chunks ):
        s.out[4*i:4*i+4].value = s.in_[4*i:4*i+4]

def test_VariablePartSelects( setup_sim ):

  model      = VariablePartSelects(3)
  model, sim = setup_sim( model )
  model.in_.value = 0xF0F
  sim.eval_combinational()
  assert model.out == 0xF0F
  model.in_.value = 0xFF0
  sim.eval_combinational()
  assert model.out == 0xFF0
  model.in_.value = 0x000
  sim.eval_combinational()
  assert model.out == 0x000

#-----------------------------------------------------------------------
# InferFuncCall
#-----------------------------------------------------------------------
class InferFuncCall( Model ):
  def __init__( s ):
    s.in_ = InPort ( 4 )
    s.o1  = OutPort( 8 )
    s.o2  = OutPort( 8 )
    s.o3  = OutPort( 8 )
    s.o1c = OutPort( 8 )
    s.o2c = OutPort( 8 )
    s.o3c = OutPort( 8 )
    s.tmp = 8

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      a = sext( s.in_, 8 )
      b = zext( s.in_, 8 )
      c = Bits(     8, 4 )
      d = sext( s.in_, s.tmp )
      e = zext( s.in_, s.tmp )
      f = Bits( s.tmp, 4 )
      s.o1 .value = a
      s.o2 .value = b
      s.o3 .value = c
      s.o1c.value = d
      s.o2c.value = e
      s.o3c.value = f

def test_InferFuncCall( setup_sim ):

  model      = InferFuncCall()
  model, sim = setup_sim( model )
  model.in_.value = 0x7
  sim.cycle()
  assert model.o1  == 0x7
  assert model.o2  == 0x7
  assert model.o3  == 0x4
  assert model.o1c == 0x7
  assert model.o2c == 0x7
  assert model.o3c == 0x4
  model.in_.value = 0xF
  sim.cycle()
  assert model.o1  == 0xFF
  assert model.o2  == 0xF
  assert model.o3  == 0x4
  assert model.o1c == 0xFF
  assert model.o2c == 0xF
  assert model.o3c == 0x4
