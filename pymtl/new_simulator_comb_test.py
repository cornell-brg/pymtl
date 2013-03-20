from new_model import *
from new_simulator import *

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
  def __init__( self, nbits ):
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )

  @ combinational
  def logic( self ):
    self.out.value = self.in_.value

def test_PassThroughOld():
  passthrough_tester( PassThroughOld )

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( self, nbits ):
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )

  @ combinational
  def logic( self ):
    self.out.v = self.in_

import pytest
@pytest.mark.xfail
def test_PassThrough():
  passthrough_tester( PassThrough )

#-------------------------------------------------------------------------
# FullAdder
#-------------------------------------------------------------------------

class FullAdder( Model ):
  def __init__( self ):
    self.in0  = InPort ( 1 )
    self.in1  = InPort ( 1 )
    self.cin  = InPort ( 1 )
    self.sum  = OutPort( 1 )
    self.cout = OutPort( 1 )

  @combinational
  def logic( self ):
    a = self.in0.value
    b = self.in1.value
    c = self.cin.value
    self.sum.value  = (a ^ b) ^ c
    self.cout.value = (a & b) | (a & c) | (b & c)

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
  def __init__( self, nbits ):
    # Ports
    self.in0 = [ InPort ( 1 ) for x in xrange( nbits ) ]
    self.in1 = [ InPort ( 1 ) for x in xrange( nbits ) ]
    self.sum = [ OutPort( 1 ) for x in xrange( nbits ) ]
    # Submodules
    self.adders = [ FullAdder() for i in xrange( nbits ) ]
    # Connections
    for i in xrange( nbits ):
      connect( self.adders[i].in0, self.in0[i] )
      connect( self.adders[i].in1, self.in1[i] )
      connect( self.adders[i].sum, self.sum[i] )
    for i in xrange( nbits - 1 ):
      connect( self.adders[ i + 1 ].cin, self.adders[ i ].cout )
    connect( self.adders[0].cin, 0 )

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
#  def __init__( self, nbits ):
#    # Ports
#    self.in0 = InPort ( nbits )
#    self.in1 = InPort ( nbits )
#    self.sum = OutPort( nbits )
#    # Submodules
#    self.adders = [ FullAdder() for i in xrange( nbits ) ]
#    # Connections
#    for i in xrange( nbits ):
#      connect( self.adders[i].in0, self.in0[i] )
#      connect( self.adders[i].in1, self.in1[i] )
#      connect( self.adders[i].sum, self.sum[i] )
#    for i in xrange( nbits - 1 ):
#      connect( self.adders[i+1].cin, self.adders[i].cout )
#    connect( self.adders[0].cin, 0 )
#
#def test_RippleCarryAdderNoSlice():
#  def set( signal, value ):
#    signal.v = value
#  def check( signal, value ):
#    assert signal.v == value
#  ripplecarryadder_tester( RippleCarryAdderNoSlice, set, check )
