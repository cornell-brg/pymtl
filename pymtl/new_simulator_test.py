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
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  assert model.out == 10

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )
    # Connections
    connect( self.in_, self.out )

def test_PassThrough():
  passthrough_tester( PassThrough )

#-------------------------------------------------------------------------
# PassThroughList
#-------------------------------------------------------------------------

class PassThroughList( Model ):
  def __init__( self, nbits, nports ):
    # Ports
    self.in_ = [ InPort ( nbits ) for x in range( nports ) ]
    self.out = [ OutPort( nbits ) for x in range( nports ) ]
    # Connections
    for i in range( nports ):
      connect( self.in_[i], self.out[i] )

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
# PassThroughWrapped
#-------------------------------------------------------------------------

class PassThroughWrapped( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )
    # Submodules
    self.pt  = PassThrough( nbits )
    # Connections
    connect( self.in_, self.pt.in_ )
    connect( self.out, self.pt.out )

def test_PassThroughWrapped():
  passthrough_tester( PassThroughWrapped )

#-------------------------------------------------------------------------
# PassThroughWrappedChain
#-------------------------------------------------------------------------

class PassThroughWrappedChain( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_ = InPort ( nbits )
    self.out = OutPort( nbits )
    # Submodules
    self.pt0 = PassThrough( nbits )
    self.pt1 = PassThrough( nbits )
    # Connections
    connect( self.in_,     self.pt0.in_ )
    connect( self.pt0.out, self.pt1.in_ )
    connect( self.out,     self.pt1.out )

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
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Connections
    connect( self.in_, self.out0 )
    connect( self.in_, self.out1 )

def test_Splitter():
  splitter_tester( Splitter )

#-------------------------------------------------------------------------
# SplitterWrapped
#-------------------------------------------------------------------------

class SplitterWrapped( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.spl  = Splitter( nbits )
    # Connections
    connect( self.in_,  self.spl.in_  )
    connect( self.out0, self.spl.out0 )
    connect( self.out1, self.spl.out1 )

def test_SplitterWrapped():
  splitter_tester( SplitterWrapped )

#-------------------------------------------------------------------------
# SplitterPassThrough
#-------------------------------------------------------------------------

class SplitterPT_1( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.pt0  = PassThrough( nbits )
    self.pt1  = PassThrough( nbits )
    # Connections
    connect( self.in_,  self.pt0.in_ )
    connect( self.in_,  self.pt1.in_ )
    connect( self.out0, self.pt0.out )
    connect( self.out1, self.pt1.out )

def test_SplitterPT_1():
  splitter_tester( SplitterPT_1 )

class SplitterPT_2( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.pt0  = PassThrough( nbits )
    # Connections
    connect( self.in_,  self.pt0.in_ )
    connect( self.out0, self.pt0.out )
    connect( self.in_,  self.out1    )

def test_SplitterPT_2():
  splitter_tester( SplitterPT_2 )

class SplitterPT_3( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.pt0  = PassThrough( nbits )
    # Connections
    connect( self.in_,  self.pt0.in_ )
    connect( self.in_,  self.out0    )
    connect( self.out1, self.pt0.out )

def test_SplitterPT_3():
  splitter_tester( SplitterPT_3 )

class SplitterPT_4( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.spl  = Splitter( nbits )
    self.pt0  = PassThrough( nbits )
    self.pt1  = PassThrough( nbits )
    # Connections
    connect( self.in_,      self.spl.in_ )
    connect( self.spl.out0, self.pt0.in_ )
    connect( self.spl.out1, self.pt1.in_ )
    connect( self.out0,     self.pt0.out )
    connect( self.out1,     self.pt1.out )

def test_SplitterPT_4():
  splitter_tester( SplitterPT_4 )

class SplitterPT_5( Model ):
  def __init__( self, nbits ):
    # Ports
    self.in_  = InPort ( nbits )
    self.out0 = OutPort( nbits )
    self.out1 = OutPort( nbits )
    # Submodules
    self.spl  = Splitter( nbits )
    self.pt0  = PassThrough( nbits )
    self.pt1  = PassThrough( nbits )
    self.pt2  = PassThrough( nbits )
    self.pt3  = PassThrough( nbits )
    # Connections
    connect( self.in_,      self.spl.in_ )
    connect( self.spl.out0, self.pt0.in_ )
    connect( self.spl.out1, self.pt1.in_ )
    connect( self.pt0.out,  self.pt2.in_ )
    connect( self.pt1.out,  self.pt3.in_ )
    connect( self.out0,     self.pt2.out )
    connect( self.out1,     self.pt3.out )

def test_SplitterPT_5():
  splitter_tester( SplitterPT_5 )
