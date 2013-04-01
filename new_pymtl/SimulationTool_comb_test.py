from Model          import *
from SimulationTool import *

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
    # Connections
    for i in xrange( s.nbits ):
      connect( s.adders[i].in0, s.in0[i] )
      connect( s.adders[i].in1, s.in1[i] )
      connect( s.adders[i].sum, s.sum[i] )
    for i in xrange( s.nbits - 1 ):
      connect( s.adders[ i + 1 ].cin, s.adders[ i ].cout )
    connect( s.adders[0].cin, 0 )

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

#class RippleCarryAdder( Model ):
#  def __init__( s, nbits ):
#    # Ports
#    s.in0 = InPort ( nbits )
#    s.in1 = InPort ( nbits )
#    s.sum = OutPort( nbits )
#    # Submodules
#    s.adders = [ FullAdder() for i in xrange( nbits ) ]
#    # Connections
#    for i in xrange( nbits ):
#      connect( s.adders[i].in0, s.in0[i] )
#      connect( s.adders[i].in1, s.in1[i] )
#      connect( s.adders[i].sum, s.sum[i] )
#    for i in xrange( nbits - 1 ):
#      connect( s.adders[i+1].cin, s.adders[i].cout )
#    connect( s.adders[0].cin, 0 )
#
#def test_RippleCarryAdderNoSlice():
#  def set( signal, value ):
#    signal.v = value
#  def check( signal, value ):
#    assert signal.v == value
#  ripplecarryadder_tester( RippleCarryAdderNoSlice, set, check )

#-------------------------------------------------------------------------
# Splitter Utility Functions
#-------------------------------------------------------------------------

def setup_splitter( nbits, groups=None ):
  if not groups:
    model = SimpleSplitter( nbits )
  else:
    model = ComplexSplitter( nbits, groups )
  sim = setup_sim( model )
  return model, sim

def verify_splitter( port_array, expected ):
  actual = 0
  for i, port in enumerate(port_array):
    shift = i * port.nbits
    actual |= (port.value.uint() << shift)
  assert bin(actual) == bin(expected)

#-------------------------------------------------------------------------
# SimpleSplitter
#-------------------------------------------------------------------------

class SimpleSplitter( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = InPort( nbits )
    s.out   = [ OutPort(1) for x in xrange( nbits ) ]

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        s.out[i].value = s.in_.value[i]

def test_SimpleSplitter_8_to_8x1():
  model, sim = setup_splitter( 8 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

def test_SimpleSplitter_16_to_16x1():
  model, sim = setup_splitter( 16 )
  model.in_.v = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.v = 0b1111000011001010
  sim.eval_combinational()
  verify_splitter( model.out, 0b1111000011001010 )

#-------------------------------------------------------------------------
# ComplexSplitter
#-------------------------------------------------------------------------

class ComplexSplitter(Model):
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

def test_ComplexSplitter_8_to_8x1():
  model, sim = setup_splitter( 8, 1 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

def test_ComplexSplitter_8_to_4x2():
  model, sim = setup_splitter( 8, 2 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

def test_ComplexSplitter_8_to_2x4():
  model, sim = setup_splitter( 8, 4 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

def test_ComplexSplitter_8_to_1x8():
  model, sim = setup_splitter( 8, 8 )
  model.in_.value = 0b11110000
  sim.eval_combinational()
  verify_splitter( model.out, 0b11110000 )
  model.in_.value = 0b01010101
  sim.eval_combinational()
  verify_splitter( model.out, 0b01010101 )

#-------------------------------------------------------------------------
# Merger Utility Functions
#-------------------------------------------------------------------------

def setup_merger( nbits, groups=None ):
  if not groups:
    model = SimpleMerger( nbits )
  else:
    model = ComplexMerger( nbits, groups )
  sim = setup_sim( model )
  return model, sim

def set_ports( port_array, value ):
  for i, port in enumerate( port_array ):
    shift = i * port.nbits
    # Truncate to ensure no width mismatches -cbatten
    port.value = (value >> shift) & ((1 << port.nbits) - 1)

#-------------------------------------------------------------------------
# SimpleMerger
#-------------------------------------------------------------------------

class SimpleMerger( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_   = [ InPort( 1 ) for x in xrange( nbits ) ]
    s.out   = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      for i in range( s.nbits ):
        s.out.value[i] = s.in_[i].value

def test_SimpleMerger_8x1_to_8():
  model, sim = setup_merger( 8 )
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

def test_SimpleMerger_16x1_to_16():
  model, sim = setup_merger( 16 )
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
# ComplexMerger
#-------------------------------------------------------------------------

class ComplexMerger( Model ):
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

def test_ComplexMerger_8x1_to_8():
  model, sim = setup_merger( 8, 1 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexMerger_4x2_to_8():
  model, sim = setup_merger( 8, 2 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexMerger_2x4_to_8():
  model, sim = setup_merger( 8, 4 )
  set_ports( model.in_, 0b11110000 )
  sim.eval_combinational()
  assert model.out.v == 0b11110000
  set_ports( model.in_, 0b01010101 )
  sim.eval_combinational()
  assert model.out.value == 0b01010101

def test_ComplexMerger_1x8_to_8():
  model, sim = setup_merger( 8, 8 )
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
# Mux
#-------------------------------------------------------------------------
from math import ceil, log

class Mux( Model ):
  def __init__( s, nbits, nports ):
    s.in_ = [ InPort( nbits ) for x in range( nports  ) ]
    s.out = OutPort( nbits )
    s.sel = InPort ( int( ceil( log( nports, 2 ) ) ))
  def elaborate_logic( s ):
    @s.combinational
    def logic():
      assert s.sel < len( s.in_ )
      s.out.v = s.in_[ s.sel.uint() ]

def test_Mux():
  model = Mux( 3, 8 )
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
