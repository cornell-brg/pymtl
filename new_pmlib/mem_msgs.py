#=========================================================================
# mem_msgs
#=========================================================================
# This module contains helper classes for working with memory request and
# response messages.

from new_pymtl import *
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

  def __init__( s, addr_nbits, data_nbits ):

    # Checks

    assert data_nbits % 8 == 0

    # Specify the size of each field

    s.type_nbits = 1
    s.addr_nbits = addr_nbits
    s.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    s.data_nbits = data_nbits

    # Total size in bits

    s.nbits = 0
    s.nbits += s.type_nbits
    s.nbits += s.addr_nbits
    s.nbits += s.len_nbits
    s.nbits += s.data_nbits

    # Specify the location of each field

    pos = s.nbits

    s.type_slice = slice( pos - s.type_nbits, pos )
    pos -= s.type_nbits

    s.addr_slice = slice( pos - s.addr_nbits, pos )
    pos -= s.addr_nbits

    s.len_slice = slice( pos - s.len_nbits, pos )
    pos -= s.len_nbits

    s.data_slice = slice( pos - s.data_nbits, pos )
    pos -= s.data_nbits

    # Type enumeration constants

    s.type_read  = 0
    s.type_write = 1

    s.type_to_str = [''] * 2**s.type_nbits
    s.type_to_str[ s.type_read  ] = 'r'
    s.type_to_str[ s.type_write ] = 'w'

  def mk_req( s, type_, addr, len_, data ):

    bits = Bits( s.nbits )
    bits[ s.type_slice ] = type_
    bits[ s.addr_slice ] = addr
    bits[ s.len_slice  ] = len_
    bits[ s.data_slice ] = data

    return bits

  def __hash__( s ):
    return hash( frozenset( (s.addr_nbits, s.data_nbits) ) )


#-------------------------------------------------------------------------
# MemReqFromBits
#-------------------------------------------------------------------------

class MemReqFromBits (Model):

  def __init__( s, memreq_params ):

    s.bits  = InPort  ( memreq_params.nbits      )

    s.type_ = OutPort ( memreq_params.type_nbits )
    s.addr  = OutPort ( memreq_params.addr_nbits )
    s.len_  = OutPort ( memreq_params.len_nbits  )
    s.data  = OutPort ( memreq_params.data_nbits )

    s.memreq_params = memreq_params

  def elaborate_logic( s ):
    # Connections

    #s.connect( s.bits[ s.memreq_params.type_slice ], s.type_ )
    #s.connect( s.bits[ s.memreq_params.addr_slice ], s.addr  )
    #s.connect( s.bits[ s.memreq_params.len_slice  ], s.len_  )
    #s.connect( s.bits[ s.memreq_params.data_slice ], s.data  )
    @s.combinational
    def comb_logic():
      s.type_.value = s.bits[ s.memreq_params.type_slice ].value   
      s.addr.value  = s.bits[ s.memreq_params.addr_slice ].value   
      s.len_.value  = s.bits[ s.memreq_params.len_slice  ].value   
      s.data.value  = s.bits[ s.memreq_params.data_slice ].value   

  def line_trace( s ):
    #print"test_bits"
    #print( s.bits )
    return "{}{}:{}:{}" \
      .format( s.memreq_params.type_to_str[ s.type_.value.uint() ],
               s.len_.value, s.addr.value, s.data.value )

#-------------------------------------------------------------------------
# MemReqToBits
#-------------------------------------------------------------------------

class MemReqToBits (Model):

  def __init__( s, memreq_params ):

    s.type_ = InPort  ( memreq_params.type_nbits )
    s.addr  = InPort  ( memreq_params.addr_nbits )
    s.len_  = InPort  ( memreq_params.len_nbits  )
    s.data  = InPort  ( memreq_params.data_nbits )

    s.bits  = OutPort ( memreq_params.nbits      )

    s.memreq_params = memreq_params

  def elaborate_logic( s ):
    # Connections

    s.connect( s.bits[ s.memreq_params.type_slice ], s.type_ )
    s.connect( s.bits[ s.memreq_params.addr_slice ], s.addr  )
    s.connect( s.bits[ s.memreq_params.len_slice  ], s.len_  )
    s.connect( s.bits[ s.memreq_params.data_slice ], s.data  )

  def line_trace( s ):
    return "{}{}:{}:{}" \
      .format( s.memreq_params.type_to_str[ s.type_.value.uint() ],
               s.len_.value, s.addr_.value, s.data.value )

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

  def __init__( s, data_nbits ):

    # Checks

    assert data_nbits % 8 == 0

    # Specify the size of each field

    s.type_nbits = 1
    s.len_nbits  = int( math.ceil( math.log( data_nbits/8, 2 ) ) )
    s.data_nbits = data_nbits

    # Total size in bits

    s.nbits = 0
    s.nbits += s.type_nbits
    s.nbits += s.len_nbits
    s.nbits += s.data_nbits

    # Specify the location of each field

    pos = s.nbits

    s.type_slice = slice( pos - s.type_nbits, pos )
    pos -= s.type_nbits

    s.len_slice = slice( pos - s.len_nbits, pos )
    pos -= s.len_nbits

    s.data_slice = slice( pos - s.data_nbits, pos )
    pos -= s.data_nbits

    # Type enumeration constants

    s.type_read  = 0
    s.type_write = 1

    s.type_to_str = [''] * 2**s.type_nbits
    s.type_to_str[ s.type_read  ] = 'r'
    s.type_to_str[ s.type_write ] = 'w'

  def mk_resp( s, type_, len_, data ):

    bits = Bits( s.nbits )
    bits[ s.type_slice ] = type_
    bits[ s.len_slice  ] = len_
    bits[ s.data_slice ] = data

    return bits

  def __hash__( s ):
    return hash( s.data_nbits )

#-------------------------------------------------------------------------
# MemRespFromBits
#-------------------------------------------------------------------------

class MemRespFromBits (Model):

  def __init__( s, memresp_params ):

    s.bits  = InPort  ( memresp_params.nbits      )

    s.type_ = OutPort ( memresp_params.type_nbits )
    s.len_  = OutPort ( memresp_params.len_nbits  )
    s.data  = OutPort ( memresp_params.data_nbits )

    s.memresp_params = memresp_params

  def elaborate_logic( s ):
    # Connections

    s.connect( s.bits[ s.memresp_params.type_slice ], s.type_ )
    s.connect( s.bits[ s.memresp_params.len_slice  ], s.len_  )
    s.connect( s.bits[ s.memresp_params.data_slice ], s.data  )

  def line_trace( s ):
    return "{}{}:{}" \
      .format( s.memresp_params.type_to_str[ s.type_.value.uint() ],
               s.len_.value, s.data.value )

#-------------------------------------------------------------------------
# MemRespToBits
#-------------------------------------------------------------------------

class MemRespToBits (Model):

  def __init__( s, memresp_params ):

    s.type_ = InPort  ( memresp_params.type_nbits )
    s.len_  = InPort  ( memresp_params.len_nbits  )
    s.data  = InPort  ( memresp_params.data_nbits )

    s.bits  = OutPort ( memresp_params.nbits      )

    s.memresp_params = memresp_params

  def elaborate_logic( s ):
    # Connections

    #s.connect( s.bits[ s.memresp_params.type_slice ], s.type_ )
    #s.connect( s.bits[ s.memresp_params.len_slice  ], s.len_  )
    #s.connect( s.bits[ s.memresp_params.data_slice ], s.data  )
    @s.combinational
    def comb_logic():
      s.bits[ s.memresp_params.type_slice ].value = s.type_.value 
      s.bits[ s.memresp_params.len_slice  ].value = s.len_.value  
      s.bits[ s.memresp_params.data_slice ].value = s.data.value  

  def line_trace( s ):
    return "{}{}:{}" \
      .format( s.memresp_params.type_to_str[ s.type_.value.uint() ],
               s.len_.value, s.data.value )

