#=========================================================================
# mem_structs
#=========================================================================
# This module contains BitStructs impelmenting memory messages.

from pymtl import *

import math

# TODO: make both MemReqMsg and MemRespMsg inherit from a MemMsg baseclass

#-------------------------------------------------------------------------
# Memory Request Messages
#-------------------------------------------------------------------------
# Memory request messages can either be for a read or write. Read
# requests include an address and the number of bytes to read, while
# write requests include an address, the number of bytes to write, and
# the actual data to write.
#
# Message Format:
#
#    1b     addr_nbits calc   data_nbits
#  +------+-----------+------+-----------+
#  | type | addr      | len  | data      |
#  +------+-----------+------+-----------+
#
# The message type is parameterized, so we use a MemReqParams class to
# hold information about a specific kind of memory request. Note that the
# size of the length field is caclulated from the number of bits in the
# data field, and that the length field is expressed in _bytes_. If the
# value of the length field is zero, then the read or write should be for
# the full width of the data field.
#
# For example, if the address size is 32 bits and the data size is also
# 32 bits, then the message format is as follows:
#
#   66  66 65       34 33  32 31        0
#  +------+-----------+------+-----------+
#  | type | addr      | len  | data      |
#  +------+-----------+------+-----------+
#
# The length field is two bits. A length value of one means read or write
# a single byte, a length value of two means read or write two bytes, and
# so on. A length value of zero means read or write all four bytes. Note
# that not all memories will necessarily support any alignment and/or any
# value for the length field.

class MemReqMsg( BitStruct ):

  # Enums for type field
  rd = 0
  wr = 1
  type_str = ['r', 'w']

  # Enums for len field
  byte  = 1
  half  = 2
  word  = 0

  def __init__( self, addr_nbits, data_nbits ):

    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    # TODO: create utility function for this
    len = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    self.type = Field( 1 )
    self.addr = Field( addr_nbits )
    self.len  = Field( len )
    self.data = Field( data_nbits )

  def line_trace( self ):
    return "{}{}:{}:{}" \
      .format( self.type_str[ self.type.value.uint ],
               self.len.value, self.addr.value, self.data.value )

  def mk_req( self, type, addr, len, data ):

    bits = Bits( self.nbits )
    bits[ self.type_slice ] = type
    bits[ self.addr_slice ] = addr
    bits[ self.len_slice  ] = len
    bits[ self.data_slice ] = data

    return bits

#-------------------------------------------------------------------------
# Memory Response Messages
#-------------------------------------------------------------------------
# Memory response messages can either be for a read or write. Read
# responses include the actual data and the number of bytes, while write
# responses currently include nothing other than the type.
#
# Message Format:
#
#    1b    calc   data_nbits
#  +------+------+-----------+
#  | type | len  | data      |
#  +------+------+-----------+
#
# The message type is parameterized, so we use a MemRespParams class to
# hold information about a specific kind of memory response. Note that
# the size of the length field is caclulated from the number of bits in
# the data field, and that the length field is expressed in _bytes_. If
# the value of the length field is zero, then the read or write should be
# for the full width of the data field.
#
# For example, if the address size is 32 bits and the data size is also
# 32 bits, then the message format is as follows:
#
#   34  34 33  32 31        0
#  +------+------+-----------+
#  | type | len  | data      |
#  +------+------+-----------+
#
# The length field is two bits. A length value of one means a single byte
# of read data is valid, a length value of two means two bytes of read
# data is valid, and so on. A length value of zero means all four bytes
# of the read data is valid. Note that not all memories will necessarily
# support any alignment and/or any value for the length field.


class MemRespMsg( BitStruct ):

  # Enums for type field
  rd = 0
  wr = 1
  type_str = ['r', 'w']

  # Enums for len field
  byte  = 1
  half  = 2
  word  = 0

  def __init__( self, data_nbits ):

    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    # TODO: create utility function for this
    len = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    self.type = Field( 1 )
    self.len  = Field( len )
    self.data = Field( data_nbits )

  def line_trace( self ):
    return "{}{}:{}" \
      .format( self.type_str[ self.type.value.uint ],
               self.len.value, self.data.value )

  def mk_resp( self, type, len, data ):

    bits = Bits( self.nbits )
    bits[ self.type_slice ] = type
    bits[ self.len_slice  ] = len
    bits[ self.data_slice ] = data

    return bits

