#=========================================================================
# MemMsg
#=========================================================================
# Contains memory request and response messages.

from pymtl import *

import math

#-------------------------------------------------------------------------
# MemReqMsg
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
# The message type is parameterized by the number of address and data
# bits. Note that the size of the length field is caclulated from the
# number of bits in the data field, and that the length field is
# expressed in _bytes_. If the value of the length field is zero, then
# the read or write should be for the full width of the data field.
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

class MemReqMsg( BitStructDefinition ):

  TYPE_READ  = 0
  TYPE_WRITE = 1

  def __init__( s, addr_nbits, data_nbits ):

    s.type_nbits = 1
    s.addr_nbits = addr_nbits
    s.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2) ) )
    s.data_nbits = data_nbits

    s.type_ = BitField( s.type_nbits )
    s.addr  = BitField( s.addr_nbits )
    s.len   = BitField( s.len_nbits  )
    s.data  = BitField( s.data_nbits )

  def mk_msg( s, type_, addr, len_, data ):

    msg       = s()
    msg.type_ = type_
    msg.addr  = addr
    msg.len   = len_
    msg.data  = data

    return msg

  def mk_rd( s, addr, len_ ):

    msg       = s()
    msg.type_ = MemReqMsg.TYPE_READ
    msg.addr  = addr
    msg.len   = len_
    msg.data  = 0

    return msg

  def mk_wr( s, addr, len_, data ):

    msg       = s()
    msg.type_ = MemReqMsg.TYPE_WRITE
    msg.addr  = addr
    msg.len   = len_
    msg.data  = data

    return msg

  def __str__( s ):

    if s.type_ == MemReqMsg.TYPE_READ:
      return "rd:{}:{}".format( s.addr, ' '*(s.data.nbits/4) )

    elif s.type_ == MemReqMsg.TYPE_WRITE:
      return "wr:{}:{}".format( s.addr, s.data )

#-------------------------------------------------------------------------
# MemReqMsg
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
# The message type is parameterized by the number of address and data
# bits. Note that the size of the length field is caclulated from the
# number of bits in the data field, and that the length field is
# expressed in _bytes_. If the value of the length field is zero, then
# the read or write should be for the full width of the data field.
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

class MemRespMsg( BitStructDefinition ):

  TYPE_READ  = 0
  TYPE_WRITE = 1

  def __init__( s, data_nbits ):

    s.type_nbits = 1
    s.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    s.data_nbits = data_nbits

    s.type_ = BitField( s.type_nbits )
    s.len   = BitField( s.len_nbits  )
    s.data  = BitField( s.data_nbits )

  def mk_msg( s, type_, len_, data ):

    msg       = s()
    msg.type_ = type_
    msg.len   = len_
    msg.data  = data

    return msg

  # What exactly is this method for? -cbatten

  def unpck( s, msg ):

    resp = s()
    resp.value = msg
    return resp

  def __str__( s ):

    if s.type_ == MemRespMsg.TYPE_READ:
      return "rd:{}".format( s.data )

    elif s.type_ == MemRespMsg.TYPE_WRITE:
      return "wr:{}".format( ' '*(s.data.nbits/4) )

#-------------------------------------------------------------------------
# MemMsg
#-------------------------------------------------------------------------
# Single class that contains both the memory request and response types.
# This simplifies parameterizing models both both message types since (1)
# we can specifcy the address and data nbits in a single step, and (2) we
# can pass a single object into the parameterized model.

class MemMsg( object ):
  def __init__( s, addr_nbits, data_nbits ):
    s.req  = MemReqMsg ( addr_nbits, data_nbits )
    s.resp = MemRespMsg( data_nbits             )


