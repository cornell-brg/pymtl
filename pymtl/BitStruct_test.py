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
  x.value = Bits( 64, 0x5f0cd0f0f0f0f )
  #print bin( x.value.uint )

  # Test access to attributes
  assert x.type == 1
  assert x.len  == 1
  assert x.addr == 0xf0cd
  assert x.data == 0x0f0f0f0f
  assert x.width == 1 + 2 + 16 + 32

  x.type = MemMsg.rd
  assert x.type == 0

  x.len = MemMsg.half
  assert x.len == 2

  x.addr = 0xbeef
  assert x.addr == 0xbeef

  x.data = 0xabcd1234
  assert x.data == 0xabcd1234

#-------------------------------------------------------------------------
# Check Connectivity
#-------------------------------------------------------------------------

class PortMsgModel( Model ):
  def __init__( self ):
    msg = MemMsg( 16, 32 )

    self.in_ = InPort ( msg )
    self.out = OutPort( msg )

    #self.type = Wire( msg.type.width )
    #self.len  = Wire( msg.len.width  )
    #self.addr = Wire( msg.addr.width )
    #self.data = Wire( msg.data.width )

    #connect( self.in_.type, self.type )
    #connect( self.in_.len,  self.len  )
    #connect( self.in_.addr, self.addr )
    #connect( self.in_.data, self.data )

    #connect( self.out.type, self.type )
    #connect( self.out.len,  self.type )
    #connect( self.out.addr, self.addr )
    #connect( self.out.data, self.data )

def test_msg_ports():

  model = PortMsgModel()
  model.elaborate()

  assert model.in_.width      == 1 + 2 + 16 + 32
  assert model.in_.type.width == 1
  assert model.in_.len.width  == 2
  assert model.in_.addr.width == 16
  assert model.in_.data.width == 32


# def __init__( self ):
#   my_msg = MemMsg.MemMsg( 16, 32 )
#   self.in_ = InPort ( my_msg )
#   self.out = OutPort( my_msg )
#
#   # self.in_ returns an InPort, not a MemMsg!
#   # How do we get it to retrieve the attribute from the MemMsg?
#   connect( self.in_.addr, some_other_thing )

#-------------------------------------------------------------------------
# Check Logic
#-------------------------------------------------------------------------
#
# @combinational
# def logic( self ):
#   # self.out returns an OutPort, not a MemMsg!
#   # How do we get it to retrieve the attribute from the MemMsg?
#   self.out.data.value = self.in_.data.value


