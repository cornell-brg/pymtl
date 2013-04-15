#=========================================================================
# SimulationTool_struct_test.py
#=========================================================================
# Structural composition tests for the SimulationTool class.

from Model          import *
from SimulationTool import *

from SimulationTool_comb_test import verify_splitter, set_ports

import pytest

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
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  assert model.out == 10

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_PassThrough():
  passthrough_tester( PassThrough )

#-------------------------------------------------------------------------
# PassThroughList
#-------------------------------------------------------------------------

class PassThroughList( Model ):
  def __init__( s, nbits, nports ):
    s.nports = nports
    s.in_ = [ InPort ( nbits ) for x in range( nports ) ]
    s.out = [ OutPort( nbits ) for x in range( nports ) ]
  def elaborate_logic( s ):
    for i in range( s.nports ):
      s.connect( s.in_[i], s.out[i] )

def test_PassThroughList():
  model = PassThroughList( 16, 4 )
  sim = setup_sim( model )
  for i in range( 4 ):
    model.in_[i].v = i
  for i in range( 4 ):
    # Note: no need to call cycle, no @combinational block
    assert model.out[i] == i
  model.in_[2].v = 9
  model.in_[2].v = 10
  assert model.out[2] == 10

#-------------------------------------------------------------------------
# PassThroughListWire
#-------------------------------------------------------------------------

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

def test_PassThroughListWire():
  model = PassThroughListWire( 16, 4 )
  sim = setup_sim( model )
  for i in range( 4 ):
    model.in_[i].v = i
  for i in range( 4 ):
    # Note: no need to call cycle, no @combinational block
    assert model.out[i] == i
  model.in_[2].v = 9
  model.in_[2].v = 10
  assert model.out[2] == 10

#-------------------------------------------------------------------------
# PassThroughWrapped
#-------------------------------------------------------------------------

class PassThroughWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_, s.pt.in_ )
    s.connect( s.out, s.pt.out )

def test_PassThroughWrapped():
  passthrough_tester( PassThroughWrapped )

#-------------------------------------------------------------------------
# PassThroughWrappedChain
#-------------------------------------------------------------------------

class PassThroughWrappedChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0 = PassThrough( s.nbits )
    s.pt1 = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,     s.pt0.in_ )
    s.connect( s.pt0.out, s.pt1.in_ )
    s.connect( s.out,     s.pt1.out )

def test_PassThroughWrappedChain():
  passthrough_tester( PassThroughWrappedChain )

#-------------------------------------------------------------------------
# Utility Test Function for Splitter
#-------------------------------------------------------------------------

def splitter_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  assert model.out0   == 8
  assert model.out0.v == 8
  assert model.out1   == 8
  assert model.out1.v == 8
  model.in_.v = 9
  model.in_.v = 10
  assert model.out0 == 10
  assert model.out1 == 10

#-------------------------------------------------------------------------
# Splitter
#-------------------------------------------------------------------------

class Splitter( Model ):
  def __init__( s, nbits ):
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # s.connections
    s.connect( s.in_, s.out0 )
    s.connect( s.in_, s.out1 )

def test_Splitter():
  splitter_tester( Splitter )

#-------------------------------------------------------------------------
# SplitterWires
#-------------------------------------------------------------------------

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

def test_SplitterWires():
  splitter_tester( SplitterWires )

#-------------------------------------------------------------------------
# SplitterWrapped
#-------------------------------------------------------------------------

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

def test_SplitterWrapped():
  splitter_tester( SplitterWrapped )

#-------------------------------------------------------------------------
# SplitterPassThrough
#-------------------------------------------------------------------------

class SplitterPT_1( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThrough( s.nbits )
    s.pt1  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.in_,  s.pt1.in_ )
    s.connect( s.out0, s.pt0.out )
    s.connect( s.out1, s.pt1.out )

def test_SplitterPT_1():
  splitter_tester( SplitterPT_1 )

class SplitterPT_2( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.out0, s.pt0.out )
    s.connect( s.in_,  s.out1    )

def test_SplitterPT_2():
  splitter_tester( SplitterPT_2 )

class SplitterPT_3( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.pt0  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,  s.pt0.in_ )
    s.connect( s.in_,  s.out0    )
    s.connect( s.out1, s.pt0.out )

def test_SplitterPT_3():
  splitter_tester( SplitterPT_3 )

class SplitterPT_4( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.spl  = Splitter   ( s.nbits )
    s.pt0  = PassThrough( s.nbits )
    s.pt1  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,      s.spl.in_ )
    s.connect( s.spl.out0, s.pt0.in_ )
    s.connect( s.spl.out1, s.pt1.in_ )
    s.connect( s.out0,     s.pt0.out )
    s.connect( s.out1,     s.pt1.out )

def test_SplitterPT_4():
  splitter_tester( SplitterPT_4 )

class SplitterPT_5( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_  = InPort ( nbits )
    s.out0 = OutPort( nbits )
    s.out1 = OutPort( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.spl  = Splitter   ( s.nbits )
    s.pt0  = PassThrough( s.nbits )
    s.pt1  = PassThrough( s.nbits )
    s.pt2  = PassThrough( s.nbits )
    s.pt3  = PassThrough( s.nbits )
    # s.connections
    s.connect( s.in_,      s.spl.in_ )
    s.connect( s.spl.out0, s.pt0.in_ )
    s.connect( s.spl.out1, s.pt1.in_ )
    s.connect( s.pt0.out,  s.pt2.in_ )
    s.connect( s.pt1.out,  s.pt3.in_ )
    s.connect( s.out0,     s.pt2.out )
    s.connect( s.out1,     s.pt3.out )

def test_SplitterPT_5():
  splitter_tester( SplitterPT_5 )

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

#-------------------------------------------------------------------------
# SimpleBitBlast
#-------------------------------------------------------------------------

class SimpleBitBlast( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = InPort( nbits )
    s.out   = [ OutPort(1) for x in xrange( nbits ) ]

  def elaborate_logic( s ):
    for i in range( s.nbits ):
      s.connect( s.out[i], s.in_[i] )
  #def elaborate_logic( s ):
  #  @s.combinational
  #  def logic():
  #    for i in range( s.nbits ):
  #      s.out[i].value = s.in_.value[i]

@pytest.mark.xfail
def test_SimpleBitBlast_8_to_8x1():
  model, sim = setup_bit_blast( 8 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

@pytest.mark.xfail
def test_SimpleBitBlast_16_to_16x1():
  model, sim = setup_bit_blast( 16 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.v = 0b1111000011001010
  sim.eval_combinational()
  verify_splitter( model.out, 0b1111000011001010 )

#-------------------------------------------------------------------------
# ComplexBitBlast
#-------------------------------------------------------------------------

class ComplexBitBlast( Model ):
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
  #def elaborate_logic( s ):
  #  @s.combinational
  #  def logic():
  #    outport_num = 0
  #    for i in range( 0, s.nbits, s.groupings ):
  #      s.out[outport_num].value = s.in_.value[i:i+s.groupings]
  #      outport_num += 1

@pytest.mark.xfail
def test_ComplexBitBlast_8_to_8x1():
  model, sim = setup_bit_blast( 8, 1 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

@pytest.mark.xfail
def test_ComplexBitBlast_8_to_4x2():
  model, sim = setup_bit_blast( 8, 2 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

@pytest.mark.xfail
def test_ComplexBitBlast_8_to_2x4():
  model, sim = setup_bit_blast( 8, 4 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

@pytest.mark.xfail
def test_ComplexBitBlast_8_to_1x8():
  model, sim = setup_bit_blast( 8, 8 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

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

#-------------------------------------------------------------------------
# SimpleBitMerge
#-------------------------------------------------------------------------

class SimpleBitMerge( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = [ InPort( 1 ) for x in xrange( nbits ) ]
    s.out   = OutPort( nbits )

  def elaborate_logic( s ):
    for i in range( s.nbits ):
      s.connect( s.out[i], s.in_[i] )
  #def elaborate_logic( s ):
  #  @s.combinational
  #  def logic():
  #    for i in range( s.nbits ):
  #      s.out.value[i] = s.in_[i].value

@pytest.mark.xfail
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

@pytest.mark.xfail
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
    inport_num = 0
    for i in range( 0, s.nbits, s.groupings ):
      s.connect( s.out[i:i+s.groupings], s.in_[inport_num] )
      inport_num += 1
  #def elaborate_logic( s ):
  #  @s.combinational
  #  def logic():
  #    inport_num = 0
  #    for i in range( 0, s.nbits, s.groupings ):
  #      s.out.value[i:i+s.groupings] = s.in_[inport_num].value
  #      inport_num += 1

@pytest.mark.xfail
def test_ComplexBitMerge_8x1_to_8():
  model, sim = setup_bit_merge( 8, 1 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

@pytest.mark.xfail
def test_ComplexBitMerge_4x2_to_8():
  model, sim = setup_bit_merge( 8, 2 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

@pytest.mark.xfail
def test_ComplexBitMerge_2x4_to_8():
  model, sim = setup_bit_merge( 8, 4 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

@pytest.mark.xfail
def test_ComplexBitMerge_1x8_to_8():
  model, sim = setup_bit_merge( 8, 8 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101
