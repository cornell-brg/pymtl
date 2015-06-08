#=======================================================================
# SimulationTool_struct_test.py
#=======================================================================
# Structural composition tests for the SimulationTool class.

import pytest
import pymtl.model.ConnectionEdge

from random import randrange
from pymtl  import *

from SimulationTool_comb_test import verify_bit_blast, set_ports
from SimulationTool_seq_test  import setup_sim, local_setup_sim

def is_translated( model ):
  return hasattr( model, '_ffi' )

#-----------------------------------------------------------------------
# PassThrough Tester
#-----------------------------------------------------------------------

def passthrough_tester( setup_sim, model_type ):
  model      = model_type( 16 )
  model, sim = setup_sim( model )
  model.in_.v = 8

  # Note: no need to call cycle, no @combinational block unless it is a
  # Verilog translation.
  transl = is_translated( model )

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out == 10

#-----------------------------------------------------------------------
# PassThroughStruct
#-----------------------------------------------------------------------

class PassThroughStruct( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_PassThrough( setup_sim ):
  passthrough_tester( setup_sim, PassThroughStruct )

#-----------------------------------------------------------------------
# PassThroughBitsStruct
#-----------------------------------------------------------------------

class PassThroughBitsStruct( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( Bits( nbits ) )
    s.out = OutPort( Bits( nbits ) )
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_PassThroughBits( setup_sim ):
  passthrough_tester( setup_sim, PassThroughBitsStruct )

#-----------------------------------------------------------------------
# PassThroughList
#-----------------------------------------------------------------------

class PassThroughList( Model ):
  def __init__( s, nbits, nports ):
    s.nports = nports
    s.in_ = [ InPort ( nbits ) for x in range( nports ) ]
    s.out = [ OutPort( nbits ) for x in range( nports ) ]
  def elaborate_logic( s ):
    for i in range( s.nports ):
      s.connect( s.in_[i], s.out[i] )

def test_PassThroughList( setup_sim ):
  model      = PassThroughList( 16, 4 )
  model, sim = setup_sim( model )

  # Note: no need to call cycle, no @combinational block unless it is a
  # Verilog translation.
  transl = is_translated( model )

  for i in range( 4 ):
    model.in_[i].v = i

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  for i in range( 4 ):
    assert model.out[i] == i
  model.in_[2].v = 9
  model.in_[2].v = 10

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out[2] == 10

#-----------------------------------------------------------------------
# PassThroughListWire
#-----------------------------------------------------------------------

class PassThroughListWire( Model ):
  def __init__( s, nbits, nports ):
    s.nports = nports
    s.nbits  = nbits
    s.in_ = [ InPort ( nbits ) for x in range( nports ) ]
    s.out = [ OutPort( nbits ) for x in range( nports ) ]
  def elaborate_logic( s ):
    s.wire = [ Wire( s.nbits ) for x in range( s.nports ) ]
    for i in range( s.nports ):
      s.connect( s.in_[i],  s.wire[i] )
      s.connect( s.wire[i], s.out[i]  )

def test_PassThroughListWire( setup_sim ):
  model      = PassThroughListWire( 16, 4 )
  model, sim = setup_sim( model )

  # Note: no need to call cycle, no @combinational block unless it is a
  # Verilog translation.
  transl = is_translated( model )

  for i in range( 4 ):
    model.in_[i].v = i

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  for i in range( 4 ):
    assert model.out[i] == i
  model.in_[2].v = 9
  model.in_[2].v = 10

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out[2] == 10

#-----------------------------------------------------------------------
# PassThroughWrapped
#-----------------------------------------------------------------------

class PassThroughWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_, s.pt.in_ )
    s.connect( s.out, s.pt.out )

def test_PassThroughWrapped( setup_sim ):
  passthrough_tester( setup_sim, PassThroughWrapped )

#-----------------------------------------------------------------------
# PassThroughWrappedChain
#-----------------------------------------------------------------------

class PassThroughWrappedChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0 = PassThroughStruct( s.nbits )
    s.pt1 = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,     s.pt0.in_ )
    s.connect( s.pt0.out, s.pt1.in_ )
    s.connect( s.out,     s.pt1.out )

def test_PassThroughWrappedChain( setup_sim ):
  passthrough_tester( setup_sim, PassThroughWrappedChain )

#-----------------------------------------------------------------------
# Utility Test Function for Splitter
#-----------------------------------------------------------------------

def splitter_tester( setup_sim, model_type ):
  model      = model_type( 16 )
  model, sim = setup_sim( model )

  # Note: no need to call cycle, no @combinational block unless it is a
  # Verilog translation.
  transl = is_translated( model )

  model.in_.v = 8

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out0   == 8
  assert model.out0.v == 8
  assert model.out1   == 8
  assert model.out1.v == 8
  model.in_.v = 9
  model.in_.v = 10

  # call eval if this is a Verilog translated model
  if transl: sim.eval_combinational()

  assert model.out0 == 10
  assert model.out1 == 10

#-----------------------------------------------------------------------
# Splitter
#-----------------------------------------------------------------------

class Splitter( Model ):
  def __init__( s, nbits ):
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # s.connections
    s.connect( s.in_, s.out0 )
    s.connect( s.in_, s.out1 )

def test_Splitter( setup_sim ):
  splitter_tester( setup_sim, Splitter )

#-----------------------------------------------------------------------
# SplitterWires
#-----------------------------------------------------------------------

class SplitterWires( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # s.connections
    s.wire0 = Wire( s.nbits )
    s.wire1 = Wire( s.nbits )
    s.connect( s.in_,   s.wire0 )
    s.connect( s.in_,   s.wire1 )
    s.connect( s.wire0, s.out0  )
    s.connect( s.wire1, s.out1  )

def test_SplitterWires( setup_sim ):
  splitter_tester( setup_sim, SplitterWires )

#-----------------------------------------------------------------------
# SplitterWrapped
#-----------------------------------------------------------------------

class SplitterWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.spl  = Splitter( s.nbits )
    # s.connections
    s.connect( s.in_,  s.spl.in_  )
    s.connect( s.out0, s.spl.out0 )
    s.connect( s.out1, s.spl.out1 )

def test_SplitterWrapped( setup_sim ):
  splitter_tester( setup_sim, SplitterWrapped )

#-----------------------------------------------------------------------
# SplitterPassThrough
#-----------------------------------------------------------------------

class SplitterPT_1( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThroughStruct( s.nbits )
    s.pt1  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.in_,  s.pt1.in_ )
    s.connect( s.out0, s.pt0.out )
    s.connect( s.out1, s.pt1.out )

def test_SplitterPT_1( setup_sim ):
  splitter_tester( setup_sim, SplitterPT_1 )

class SplitterPT_2( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.out0, s.pt0.out )
    s.connect( s.in_,  s.out1    )

def test_SplitterPT_2( setup_sim ):
  splitter_tester( setup_sim, SplitterPT_2 )

class SplitterPT_3( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.in_,  s.out0    )
    s.connect( s.out1, s.pt0.out )

def test_SplitterPT_3( setup_sim ):
  splitter_tester( setup_sim, SplitterPT_3 )

class SplitterPT_4( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.spl  = Splitter   ( s.nbits )
    s.pt0  = PassThroughStruct( s.nbits )
    s.pt1  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,      s.spl.in_ )
    s.connect( s.spl.out0, s.pt0.in_ )
    s.connect( s.spl.out1, s.pt1.in_ )
    s.connect( s.out0,     s.pt0.out )
    s.connect( s.out1,     s.pt1.out )

def test_SplitterPT_4( setup_sim ):
  splitter_tester( setup_sim, SplitterPT_4 )

class SplitterPT_5( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.spl  = Splitter   ( s.nbits )
    s.pt0  = PassThroughStruct( s.nbits )
    s.pt1  = PassThroughStruct( s.nbits )
    s.pt2  = PassThroughStruct( s.nbits )
    s.pt3  = PassThroughStruct( s.nbits )
    # s.connections
    s.connect( s.in_,      s.spl.in_ )
    s.connect( s.spl.out0, s.pt0.in_ )
    s.connect( s.spl.out1, s.pt1.in_ )
    s.connect( s.pt0.out,  s.pt2.in_ )
    s.connect( s.pt1.out,  s.pt3.in_ )
    s.connect( s.out0,     s.pt2.out )
    s.connect( s.out1,     s.pt3.out )

def test_SplitterPT_5( setup_sim ):
  splitter_tester( setup_sim, SplitterPT_5 )

#-----------------------------------------------------------------------
# BitBlast Utility Functions
#-----------------------------------------------------------------------

def setup_bit_blast( setup_sim, nbits, groups=None ):
  if not groups:
    model      = SimpleBitBlastStruct( nbits )
  else:
    model      = ComplexBitBlastStruct( nbits, groups )
  model, sim = setup_sim( model )
  return model, sim

#-----------------------------------------------------------------------
# SimpleBitBlastStruct
#-----------------------------------------------------------------------

class SimpleBitBlastStruct( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = InPort( nbits )
    s.out   = [ OutPort(1) for x in xrange( nbits ) ]

  def elaborate_logic( s ):
    for i in range( s.nbits ):
      s.connect( s.out[i], s.in_[i] )

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
# ComplexBitBlastStruct
#-----------------------------------------------------------------------

class ComplexBitBlastStruct( Model ):
  def __init__( s, nbits, groupings ):
    s.nbits     = nbits
    s.groupings = groupings
    s.in_       = InPort( nbits )
    s.out       = [ OutPort( groupings ) for x in
                    xrange( 0, nbits, groupings ) ]

  def elaborate_logic( s ):
    outport_num = 0
    for i in range( 0, s.nbits, s.groupings ):
      s.connect( s.out[outport_num], s.in_[i:i+s.groupings] )
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
    model      = SimpleBitMergeStruct( nbits )
  else:
    model      = ComplexBitMergeStruct( nbits, groups )
  model, sim = setup_sim( model )
  return model, sim

#-----------------------------------------------------------------------
# SimpleBitMergeStruct
#-----------------------------------------------------------------------

class SimpleBitMergeStruct( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = [ InPort( 1 ) for x in xrange( nbits ) ]
    s.out   = OutPort( nbits )

  def elaborate_logic( s ):
    for i in range( s.nbits ):
      s.connect( s.out[i], s.in_[i] )

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

class ComplexBitMergeStruct( Model ):
  def __init__( s, nbits, groupings ):
    s.nbits     = nbits
    s.groupings = groupings
    s.in_       = [ InPort( groupings) for x in
                    xrange( 0, nbits, groupings ) ]
    s.out       = OutPort(nbits)

  def elaborate_logic( s ):
    inport_num = 0
    for i in range( 0, s.nbits, s.groupings ):
      s.connect( s.out[i:i+s.groupings], s.in_[inport_num] )
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
# ConstantPort
#-----------------------------------------------------------------------

class ConstantPort( Model ):
  def __init__( s ):
    s.out = OutPort( 32 )
  def elaborate_logic( s ):
    s.connect( s.out, 4 )

def test_ConstantPort( setup_sim ):
    model      = ConstantPort()
    model, sim = setup_sim( model )

    # if this is a verilog translation, need to perform a reset/cycle
    # before this is applied
    if is_translated( model ):
      sim.eval_combinational()

    assert model.out == 4

    # TODO: catch writing to a constant?
    sim.cycle()
    assert model.out == 4

#-----------------------------------------------------------------------
# ConstantSlice
#-----------------------------------------------------------------------

class ConstantSlice( Model ):
  def __init__( s ):
    s.out = OutPort( 32 )
  def elaborate_logic( s ):
    s.connect( s.out[ 0:16], 4 )
    s.connect( s.out[16:32], 8 )

def test_ConstantSlice( setup_sim ):
  model      = ConstantSlice()
  model, sim = setup_sim( model )

  # if this is a verilog translation, need to perform a reset/cycle
  # before this is applied
  if is_translated( model ):
    sim.eval_combinational()

  assert model.out.v[ 0:16] == 4
  assert model.out.v[16:32] == 8
  sim.cycle()
  assert model.out.v[ 0:16] == 4
  assert model.out.v[16:32] == 8

#-----------------------------------------------------------------------
# ConstantModule
#-----------------------------------------------------------------------

class Shifter( Model ):
  def __init__( s, inout_nbits = 1, shamt_nbits = 1 ):
    s.in_   = InPort  ( inout_nbits )
    s.shamt = InPort  ( shamt_nbits )
    s.out   = OutPort ( inout_nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.v = s.in_ << s.shamt

class ConstantModule( Model ):
  def __init__( s ):
    s.in_ = InPort  ( 8 )
    s.out = OutPort ( 8 )

  def elaborate_logic( s ):
    s.shift = m = Shifter( 8, 2 )
    s.connect_dict({
      m.in_   : s.in_,
      m.shamt : 2,
      m.out   : s.out,
    })

def test_ConstantModule( setup_sim ):
  model      = ConstantModule()
  model, sim = setup_sim( model )
  sim.reset()
  model.in_.v = 0b1111
  sim.eval_combinational()
  assert model.out == 0b111100
  sim.cycle()
  model.in_.v = 0b0101
  sim.cycle()
  assert model.out == 0b010100
  model.in_.v = 0b110110
  sim.cycle()
  assert model.out == 0b11011000
  sim.cycle()

from ...model.PortBundle_test import InValRdyBundle, OutValRdyBundle
#from BitStruct_test  import MemMsg

#-----------------------------------------------------------------------
# ListOfPortBundles
#-----------------------------------------------------------------------
# Test added to catch use case of a list of PortBundles.
def test_ListOfPortBundles( setup_sim ):

  class ListOfPortBundlesStruct( Model ):
    def __init__( s ):
      s.in_ = [ InValRdyBundle ( 8 ) for x in range( 4 ) ]
      s.out = [ OutValRdyBundle( 8 ) for x in range( 4 ) ]
      for i in range( 4 ):
        s.connect( s.in_[ i ], s.out[ i ] )

  model      = ListOfPortBundlesStruct()
  model, sim = setup_sim( model )
  sim.reset()

  for i in range( 4 ):
    # TODO add assert to prevent this
    #model.in_[ i ].v = i
    model.in_[ i ].msg.v = i

  # if this is a verilog translation, need to perform a reset/cycle
  # before this is applied
  if is_translated( model ):
    sim.eval_combinational()

  for i in range( 4 ):
    assert model.out[ i ].msg.v == i

#-----------------------------------------------------------------------
# ConnectPairs
#-----------------------------------------------------------------------
def test_ConnectPairs( setup_sim ):
  class ConnectPairs( Model ):
    def __init__( s, config ):
      s.a = InPort [ 4 ]( 8 )
      s.b = OutPort[ 4 ]( 8 )
      if config == 'good':
        s.connect_pairs(
          s.a[0], s.b[0],
          s.a[1], s.b[1],
          s.a[2], s.b[2],
          s.a[3], s.b[3],
        )
      elif config == 'bad':
        s.connect_pairs(
          s.a[0], s.b[0],
          s.a[1], s.b[1],
          s.a[2], s.b[2],
          s.a[3],
        )

  with pytest.raises( pymtl.model.ConnectionEdge.PyMTLConnectError ):
    model      = ConnectPairs('bad')

  model      = ConnectPairs('good')
  model, sim = setup_sim( model )
  sim.reset()
  for i in range( 5 ):
    for j in range( 4 ):  model.a[j].value = i+j
    sim.cycle()
    for j in range( 4 ):  model.b[j]      == i+j

#=======================================================================
# BitStructs
#=======================================================================
# Helper classes/methods.

class BitStructGlobal( BitStructDefinition ):
  def __init__( s, src_nbits, dest_nbits ):
    s.src  = BitField(  src_nbits )
    s.dest = BitField( dest_nbits )

class BitStructConnect( Model ):
  def __init__( s, MsgType ):
    s.in_ = InPort ( MsgType )
    s.out = OutPort( MsgType )
    s.connect( s.in_.src,  s.out.dest )
    s.connect( s.in_.dest, s.out.src  )

def bitstruct_verifier( model, sim, src, dest ):
  max_ = 2**src
  for i in range( 10 ):
    src, dest = randrange(0,max_), randrange(0,max_)
    model.in_.src .value = src
    model.in_.dest.value = dest
    sim.cycle()
    print model.in_.src,  model.out.src,  src
    print model.in_.dest, model.out.dest, dest
    assert model.out.src  == dest
    assert model.out.dest == src

#-----------------------------------------------------------------------
# BitStructGlobal
#-----------------------------------------------------------------------
@pytest.mark.parametrize('src,dest', [(8,8),(16,16)])
def test_BitStructGlobal( setup_sim, src, dest ):
  model      = BitStructConnect( BitStructGlobal( src, dest ) )
  model, sim = setup_sim( model )
  bitstruct_verifier( model, sim, src, dest )

#-----------------------------------------------------------------------
# BitStructLocal
#-----------------------------------------------------------------------
@pytest.mark.parametrize('src,dest', [(8,8),(16,16)])
def test_BitStructLocal( setup_sim, src, dest ):
  class BitStructLocal( BitStructDefinition ):
    def __init__( s, src_nbits, dest_nbits ):
      s.src  = BitField(  src_nbits )
      s.dest = BitField( dest_nbits )
  model      = BitStructConnect( BitStructLocal( src, dest ) )
  model, sim = setup_sim( model )
  bitstruct_verifier( model, sim, src, dest )


# alejandro innarutu
# kevin thompson




