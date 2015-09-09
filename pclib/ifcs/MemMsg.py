#=========================================================================
# MemMsg
#=========================================================================
# Contains memory request and response messages.

from pymtl import *

import math

#-------------------------------------------------------------------------
# MemReqMsg
#-------------------------------------------------------------------------
# Memory request messages can be of various types. The most basic are for
# a read or write, although there is encoding space for more message
# types such as atomic memory operations and prefetch requests. Read
# requests include an address and the number of bytes to read, while
# write requests include an address, the number of bytes to write, and
# the actual data to write. Both kinds of messages include an opaque
# field.
#
# Message Format:
#
#          opaque  addr               data
#    3b    nbits   nbits       calc   nbits
#  +------+------+-----------+------+-----------+
#  | type |opaque| addr      | len  | data      |
#  +------+------+-----------+------+-----------+
#
# The message type is parameterized by the number of opaque, address, and
# data bits. Note that the size of the length field is caclulated from
# the number of bits in the data field, and that the length field is
# expressed in _bytes_. If the value of the length field is zero, then
# the read or write should be for the full width of the data field.
#
# For example, if the opaque field is 8 bits, the address size is 32
# bits, and the data size is also 32 bits, then the message format is as
# follows:
#
#   76  74 73  66 65       34 33  32 31        0
#  +------+------+-----------+------+-----------+
#  | type |opaque| addr      | len  | data      |
#  +------+------+-----------+------+-----------+
#
# The length field is two bits. A length value of one means read or write
# a single byte, a length value of two means read or write two bytes, and
# so on. A length value of zero means read or write all four bytes. Note
# that not all memories will necessarily support any alignment and/or any
# value for the length field.
#
# The opaque field is reserved for use by the requester. Models must
# ensure that the exact same opaque field is included in the
# corresponding response.

class MemReqMsg( BitStructDefinition ):

  TYPE_READ  = 0
  TYPE_WRITE = 1

  def __init__( s, opaque_nbits, addr_nbits, data_nbits ):

    s.type_nbits   = 3
    s.opaque_nbits = opaque_nbits
    s.addr_nbits   = addr_nbits
    s.len_nbits    = int( math.ceil( math.log( data_nbits/8, 2) ) )
    s.data_nbits   = data_nbits

    s.type_  = BitField( s.type_nbits   )
    s.opaque = BitField( s.opaque_nbits )
    s.addr   = BitField( s.addr_nbits   )
    s.len    = BitField( s.len_nbits    )
    s.data   = BitField( s.data_nbits   )

  def mk_rd( s, opaque, addr, len_ ):

    msg        = s()
    msg.type_  = MemReqMsg.TYPE_READ
    msg.opaque = opaque
    msg.addr   = addr
    msg.len    = len_
    msg.data   = 0

    return msg

  def mk_wr( s, opaque, addr, len_, data ):

    msg        = s()
    msg.type_  = MemReqMsg.TYPE_WRITE
    msg.opaque = opaque
    msg.addr   = addr
    msg.len    = len_
    msg.data   = data

    return msg

  def __str__( s ):

    if s.type_ == MemReqMsg.TYPE_READ:
      return "rd:{}:{}:{}".format( s.opaque, s.addr, ' '*(s.data.nbits/4) )

    elif s.type_ == MemReqMsg.TYPE_WRITE:
      return "wr:{}:{}:{}".format( s.opaque, s.addr, s.data )

#-------------------------------------------------------------------------
# MemRespMsg
#-------------------------------------------------------------------------
# Memory response messages can be of various types. The most basic are
# for a read or write, although there is encoding space for more message
# types such as atomic memory operations and prefetch responses. Read
# responses include the actual data and the number of bytes, while write
# responses currently include just the type. Both kinds of messages
# include an opaque field and corresponding opaque field valid bit, as
# well as a two-bit test field.
#
# Message Format:
#
#          opaque                data
#    3b    nbits   2b     calc   nbits
#  +------+------+------+------+-----------+
#  | type |opaque| test | len  | data      |
#  +------+------+------+------+-----------+
#
# The message type is parameterized by the number of opaque, address, and
# data bits. Note that the size of the length field is caclulated from
# the number of bits in the data field, and that the length field is
# expressed in _bytes_. If the value of the length field is zero, then
# the read or write should be for the full width of the data field.
#
# For example, if the opaque field is 8 bits, the address size is 32
# bits, and the data size is also 32 bits, then the message format is as
# follows:
#
#   46  44 43  36 35  34 33  32 31        0
#  +------+------+------+------+-----------+
#  | type |opaque| test | len  | data      |
#  +------+------+------+------+-----------+
#
# The length field is two bits. A length value of one means read or write
# a single byte, a length value of two means read or write two bytes, and
# so on. A length value of zero means read or write all four bytes. Note
# that not all memories will necessarily support any alignment and/or any
# value for the length field.
#
# The opaque field is reserved for use by the requester. Models must
# ensure that the exact same opaque field is included in the
# corresponding response.
#
# The test field is reserved for use by memory models for testing. For
# example, a cache model could use a test bit to indicate if a memory
# request is a cache hit or miss for testing purposes.

class MemRespMsg( BitStructDefinition ):

  TYPE_READ  = 0
  TYPE_WRITE = 1

  def __init__( s, opaque_nbits, data_nbits ):

    s.type_nbits   = 3
    s.opaque_nbits = opaque_nbits
    s.test_nbits   = 2
    s.len_nbits    = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    s.data_nbits   = data_nbits

    s.type_  = BitField( s.type_nbits   )
    s.opaque = BitField( s.opaque_nbits )
    s.test   = BitField( s.test_nbits )
    s.len    = BitField( s.len_nbits    )
    s.data   = BitField( s.data_nbits   )

  def mk_rd( s, opaque, len_, data ):

    msg        = s()
    msg.type_  = MemReqMsg.TYPE_READ
    msg.opaque = opaque
    msg.test   = 0
    msg.len    = len_
    msg.data   = data

    return msg

  def mk_wr( s, opaque, len_ ):

    msg        = s()
    msg.type_  = MemReqMsg.TYPE_WRITE
    msg.opaque = opaque
    msg.test   = 0
    msg.len    = len_
    msg.data   = 0

    return msg

  def __str__( s ):

    if s.type_ == MemRespMsg.TYPE_READ:
      return "rd:{}:{}".format( s.opaque, s.data )

    elif s.type_ == MemRespMsg.TYPE_WRITE:
      return "wr:{}:{}".format( s.opaque, ' '*(s.data.nbits/4) )

#-------------------------------------------------------------------------
# MemMsg
#-------------------------------------------------------------------------
# Single class that contains both the memory request and response types.
# This simplifies parameterizing models both both message types since (1)
# we can specifcy the opaque, address, and data nbits in a single step,
# and (2) we can pass a single object into the parameterized model.

class MemMsg( object ):
  def __init__( s, opaque_nbits, addr_nbits, data_nbits ):
    s.req  = MemReqMsg ( opaque_nbits, addr_nbits, data_nbits )
    s.resp = MemRespMsg( opaque_nbits, data_nbits             )

#-------------------------------------------------------------------------
# Common Memory Messages
#-------------------------------------------------------------------------

# Memory messages with 8b opaque field, 32b address, and 32b data.

MemReqMsg4B  = MemReqMsg  ( 8, 32, 32 )
MemRespMsg4B = MemRespMsg ( 8,     32 )

class MemMsg4B( object ):
  def __init__( s ):
    s.req  = MemReqMsg4B
    s.resp = MemRespMsg4B

# Memory messages with 8b opaque field, 32b address, and 128b data.

MemReqMsg16B  = MemReqMsg  ( 8, 32, 128 )
MemRespMsg16B = MemRespMsg ( 8,     128 )

class MemMsg16B( object ):
  def __init__( s ):
    s.req  = MemReqMsg16B
    s.resp = MemRespMsg16B

