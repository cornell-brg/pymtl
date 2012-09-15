#=========================================================================
# mem_msgs
#=========================================================================
# This module contains helper classes for working with memory request and
# response messages.

from pymtl import *
import math

#=========================================================================
# Memory Request Messages
#=========================================================================
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
#
# We include a model that can unpack/pack a message from/to bits. This
# should be translatable because it uses pure structural conectivity.
# Eventually, all of this should be replaced by a BitsStruct.
#

#-------------------------------------------------------------------------
# MemReqParams
#-------------------------------------------------------------------------

class MemReqParams:

  def __init__( self, addr_nbits, data_nbits ):

    # Checks

    assert data_nbits % 8 == 0

    # Specify the size of each field

    self.type_nbits = 1
    self.addr_nbits = addr_nbits
    self.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    self.data_nbits = data_nbits

    # Total size in bits

    self.nbits = 0
    self.nbits += self.type_nbits
    self.nbits += self.addr_nbits
    self.nbits += self.len_nbits
    self.nbits += self.data_nbits

    # Specify the location of each field

    pos = self.nbits

    self.type_slice = slice( pos - self.type_nbits, pos )
    pos -= self.type_nbits

    self.addr_slice = slice( pos - self.addr_nbits, pos )
    pos -= self.addr_nbits

    self.len_slice = slice( pos - self.len_nbits, pos )
    pos -= self.len_nbits

    self.data_slice = slice( pos - self.data_nbits, pos )
    pos -= self.data_nbits

    # Type enumeration constants

    self.type_read  = 0
    self.type_write = 1

    self.type_to_str = [''] * 2**self.type_nbits
    self.type_to_str[ self.type_read  ] = 'r'
    self.type_to_str[ self.type_write ] = 'w'

  def mk_req( self, type_, addr, len_, data ):

    bits = Bits( self.nbits )
    bits[ self.type_slice ] = type_
    bits[ self.addr_slice ] = addr
    bits[ self.len_slice  ] = len_
    bits[ self.data_slice ] = data

    return bits

#-------------------------------------------------------------------------
# MemReqFromBits
#-------------------------------------------------------------------------

class MemReqFromBits (Model):

  def __init__( self, memreq_params ):

    self.bits  = InPort  ( memreq_params.nbits      )

    self.type_ = OutPort ( memreq_params.type_nbits )
    self.addr  = OutPort ( memreq_params.addr_nbits )
    self.len_  = OutPort ( memreq_params.len_nbits  )
    self.data  = OutPort ( memreq_params.data_nbits )

    self.memreq_params = memreq_params

    # Connections

    connect( self.bits[ self.memreq_params.type_slice ], self.type_ )
    connect( self.bits[ self.memreq_params.addr_slice ], self.addr  )
    connect( self.bits[ self.memreq_params.len_slice  ], self.len_  )
    connect( self.bits[ self.memreq_params.data_slice ], self.data  )

  def line_trace( self ):
    return "{}{}:{}:{}" \
      .format( self.memreq_params.type_to_str[ self.type_.value.uint ],
               self.len_.value, self.addr.value, self.data.value )

#-------------------------------------------------------------------------
# MemReqToBits
#-------------------------------------------------------------------------

class MemReqToBits (Model):

  def __init__( self, memreq_params ):

    self.type_ = InPort  ( memreq_params.type_nbits )
    self.addr  = InPort  ( memreq_params.addr_nbits )
    self.len_  = InPort  ( memreq_params.len_nbits  )
    self.data  = InPort  ( memreq_params.data_nbits )

    self.bits  = OutPort ( memreq_params.nbits      )

    self.memreq_params = memreq_params

    # Connections

    connect( self.bits[ self.memreq_params.type_slice ], self.type_ )
    connect( self.bits[ self.memreq_params.addr_slice ], self.addr  )
    connect( self.bits[ self.memreq_params.len_slice  ], self.len_  )
    connect( self.bits[ self.memreq_params.data_slice ], self.data  )

  def line_trace( self ):
    return "{}{}:{}:{}" \
      .format( self.memreq_params.type_to_str[ self.type_.value.uint ],
               self.len_.value, self.addr_.value, self.data.value )

#=========================================================================
# Memory Response Messages
#=========================================================================
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
#
# We include a model that can unpack/pack a message from/to bits. This
# should be translatable because it uses pure structural conectivity.
# Eventually, all of this should be replaced by a BitsStruct.
#

#-------------------------------------------------------------------------
# MemRespParams
#-------------------------------------------------------------------------

class MemRespParams:

  def __init__( self, data_nbits ):

    # Checks

    assert data_nbits % 8 == 0

    # Specify the size of each field

    self.type_nbits = 1
    self.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    self.data_nbits = data_nbits

    # Total size in bits

    self.nbits = 0
    self.nbits += self.type_nbits
    self.nbits += self.len_nbits
    self.nbits += self.data_nbits

    # Specify the location of each field

    pos = self.nbits

    self.type_slice = slice( pos - self.type_nbits, pos )
    pos -= self.type_nbits

    self.len_slice = slice( pos - self.len_nbits, pos )
    pos -= self.len_nbits

    self.data_slice = slice( pos - self.data_nbits, pos )
    pos -= self.data_nbits

    # Type enumeration constants

    self.type_read  = 0
    self.type_write = 1

    self.type_to_str = [''] * 2**self.type_nbits
    self.type_to_str[ self.type_read  ] = 'r'
    self.type_to_str[ self.type_write ] = 'w'

  def mk_resp( self, type_, len_, data ):

    bits = Bits( self.nbits )
    bits[ self.type_slice ] = type_
    bits[ self.len_slice  ] = len_
    bits[ self.data_slice ] = data

    return bits

#-------------------------------------------------------------------------
# MemRespFromBits
#-------------------------------------------------------------------------

class MemRespFromBits (Model):

  def __init__( self, memresp_params ):

    self.bits  = InPort  ( memresp_params.nbits      )

    self.type_ = OutPort ( memresp_params.type_nbits )
    self.len_  = OutPort ( memresp_params.len_nbits  )
    self.data  = OutPort ( memresp_params.data_nbits )

    self.memresp_params = memresp_params

    # Connections

    connect( self.bits[ self.memresp_params.type_slice ], self.type_ )
    connect( self.bits[ self.memresp_params.len_slice  ], self.len_  )
    connect( self.bits[ self.memresp_params.data_slice ], self.data  )

  def line_trace( self ):
    return "{}{}:{}" \
      .format( self.memresp_params.type_to_str[ self.type_.value.uint ],
               self.len_.value, self.data.value )

#-------------------------------------------------------------------------
# MemRespToBits
#-------------------------------------------------------------------------

class MemRespToBits (Model):

  def __init__( self, memresp_params ):

    self.type_ = InPort  ( memresp_params.type_nbits )
    self.len_  = InPort  ( memresp_params.len_nbits  )
    self.data  = InPort  ( memresp_params.data_nbits )

    self.bits  = OutPort ( memresp_params.nbits      )

    self.memresp_params = memresp_params

    # Connections

    connect( self.bits[ self.memresp_params.type_slice ], self.type_ )
    connect( self.bits[ self.memresp_params.len_slice  ], self.len_  )
    connect( self.bits[ self.memresp_params.data_slice ], self.data  )

  def line_trace( self ):
    return "{}{}:{}" \
      .format( self.memresp_params.type_to_str[ self.type_.value.uint ],
               self.len_.value, self.data.value )

