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
  model = PassThrough( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  assert model.out == 10

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
  model = PassThroughWrapped( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  # Note: no need to call cycle, no @combinational block
  assert model.out   == 8
  assert model.out.v == 8
  model.in_.v = 9
  model.in_.v = 10
  assert model.out == 10

