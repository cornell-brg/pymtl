#=========================================================================
# BitStruct Test Suite
#=========================================================================

import math

from pymtl import *
from Bits import Bits
from BitStruct import BitStruct, Field

#-------------------------------------------------------------------------
# Example BitStruct and Enums
#-------------------------------------------------------------------------

class MemMsg( BitStruct ):

  # Enums for type field
  rd = 0
  wr = 1

  # Enums for len field
  byte  = 1
  half  = 2
  word  = 0

  def __init__( self, addr_nbits, data_nbits ):

    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    len = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    self.type = Field( 1 )
    self.len  = Field( len )
    self.addr = Field( addr_nbits )
    self.data = Field( data_nbits )

    # TODO: test other Field types (for overlapping fields)
    # Field( width )
    # Field( start, width )
    # Field( start, stop )  # Excl, like python range

#-------------------------------------------------------------------------
# Hacky BitStruct test
#-------------------------------------------------------------------------

def test_bitstruct_fields():

  # Create MemMsg Bitstruct
  x = MemMsg( 16, 32 )

  # Hacky assignment of value for testing
  x._signal = InPort( x.width )
  assert x._signal.value == 0
  x._signal.value = 0x5f0cd0f0f0f0f
  assert x._signal.value == 0x5f0cd0f0f0f0f

  # Test access to attributes
  assert x.type.value == 1
  assert x.len.value  == 1
  assert x.addr.value == 0xf0cd
  assert x.data.value == 0x0f0f0f0f
  assert x.width == 1 + 2 + 16 + 32

  x.type.value = MemMsg.rd
  assert x.type.value == 0

  x.len.value = MemMsg.half
  assert x.len.value == 2

  x.addr.value = 0xbeef
  assert x.addr.value == 0xbeef

  x.data.value = 0xabcd1234
  assert x.data.value == 0xabcd1234

#-------------------------------------------------------------------------
# Check Connectivity
#-------------------------------------------------------------------------

class PortMsgModel( Model ):
  def __init__( self ):
    msg = MemMsg( 16, 32 )

    self.in_ = InPort ( msg )
    self.out = OutPort( msg )

    # TODO: msg.type.width generates a slice object, attached to the
    #       port, but with no other connections.
    #       Probably want to remove this in elaboration?
    # TODO: Would like to do msg.type.width, but this doesn't work since
    #       signal attachment done to copies of msg, not msg itself.
    #       However, self.in_.width works.
    self.type = Wire( msg.type_nbits )
    self.len  = Wire( msg.len_nbits  )
    self.addr = Wire( msg.addr_nbits )
    self.data = Wire( msg.data_nbits )

    connect( self.in_.type, self.type )
    connect( self.in_.len,  self.len  )
    connect( self.in_.addr, self.addr )
    connect( self.in_.data, self.data )

    connect( self.out.type, self.type )
    connect( self.out.len,  self.len  )
    connect( self.out.addr, self.addr )
    connect( self.out.data, self.data )

def test_msg_ports():

  model = PortMsgModel()
  model.elaborate()

  sim = SimulationTool(model)
  #import debug_utils
  #debug_utils.port_walk(model)

  assert model.in_.width      == 1 + 2 + 16 + 32
  assert model.in_.type_nbits == 1
  assert model.in_.len_nbits  == 2
  assert model.in_.addr_nbits == 16
  assert model.in_.data_nbits == 32

  # TODO: Doing port_walk here shows all temporary slices generated
  #       above as connections!  Fix this somehow?
  #debug_utils.port_walk(model)

  assert model.type.value == 0
  assert model.len.value  == 0
  assert model.addr.value == 0
  assert model.data.value == 0

  assert model.out.type.value == 0
  assert model.out.len.value  == 0
  assert model.out.addr.value == 0
  assert model.out.data.value == 0

  model.in_.value = 0x5f0cd0f0f0f0f
  assert model.in_.value == 0x5f0cd0f0f0f0f

  sim.eval_combinational()

  assert model.type.value == 1
  assert model.len.value  == 1
  assert model.addr.value == 0xf0cd
  assert model.data.value == 0x0f0f0f0f

  assert model.out.type.value == 1
  assert model.out.len.value  == 1
  assert model.out.addr.value == 0xf0cd
  assert model.out.data.value == 0x0f0f0f0f
  assert model.out.value      == 0x5f0cd0f0f0f0f

  model.in_.len.value = MemMsg.half
  assert model.out.len.value == MemMsg.half

#-------------------------------------------------------------------------
# Check Logic
#-------------------------------------------------------------------------

class LogicMsgModel( Model ):
  def __init__( self ):
    msg = MemMsg( 16, 32 )

    self.in_ = InPort ( msg )
    self.out = OutPort( msg )

  @combinational
  def logic( self ):

    self.out.type.value = self.in_.type.value
    self.out.len.value  = self.in_.len.value
    self.out.addr.value = self.in_.addr.value
    self.out.data.value = self.in_.data.value


def test_msg_logic():

  model = LogicMsgModel()
  model.elaborate()

  sim = SimulationTool(model)
  #import debug_utils
  #debug_utils.port_walk(model)
  #print model._newsenses

  assert model.in_.width      == 1 + 2 + 16 + 32
  assert model.in_.type_nbits == 1
  assert model.in_.len_nbits  == 2
  assert model.in_.addr_nbits == 16
  assert model.in_.data_nbits == 32

  model.in_.value = 1
  sim.eval_combinational()
  assert model.out.value == 1

  model.in_.value = 2
  sim.eval_combinational()
  assert model.out.value == 2

  model.in_.value = 0x5f0cd0f0f0f0f
  sim.eval_combinational()

  assert model.out.type.value == 1
  assert model.out.len.value  == 1
  assert model.out.addr.value == 0xf0cd
  assert model.out.data.value == 0x0f0f0f0f
  assert model.out.value      == 0x5f0cd0f0f0f0f

  model.in_.len.value = MemMsg.byte
  sim.eval_combinational()
  assert model.out.len.value == MemMsg.byte
