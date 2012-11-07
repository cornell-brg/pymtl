#=========================================================================
# net_msgs
#=========================================================================
# This module contains helper classes for working with network messages.

from   pymtl import *
import math

#=========================================================================
# Network Messages
#=========================================================================
# A network message consists of the route information ( dest, src ),
# sequence number and payload fields.
#
# Network Message Format:
#
#  +------+------+-------+---------------+
#  | dest | src  | seqno | payload_nbits |
#  +------+------+-------+---------------+
#
# The network message is parameterized for given routers present in the
# network, number of total messages  and the payload bitwidth. For example,
# 3 routers in the system, total of 256 messages and payload_nbits = 32,
# would have a network message format as below:
#
#   45  43 42  40 39   32 31            0
#  +------+------+-------+---------------+
#  | dest | src  | seqno | payload_nbits |
#  +------+------+-------+---------------+
#
# We include a model that can unpack/pack a message from/to bits. This
# should be translatable because it uses pure structural conectivity.
# Eventually, all of this should be replaced by a BitsStruct.

#-------------------------------------------------------------------------
# NetMsgParams
#-------------------------------------------------------------------------

class NetMsgParams:

  def __init__( self, num_routers, num_messages, payload_nbits ):

    # Specify the size of each field

    self.srcdest_nbits = int( math.ceil( math.log( num_routers, 2 ) ) )
    self.seqnum_nbits  = int( math.ceil( math.log( num_messages, 2 ) ) )
    self.payload_nbits = payload_nbits

    # Total size in bits

    self.nbits = 0
    self.nbits += self.payload_nbits
    self.nbits += self.seqnum_nbits
    self.nbits += 2*self.srcdest_nbits

    # Specify the location of each field

    pos = self.nbits

    self.dest_slice = slice( pos - self.srcdest_nbits, pos )
    pos -= self.srcdest_nbits

    self.src_slice = slice( pos - self.srcdest_nbits, pos )
    pos -= self.srcdest_nbits

    self.seqnum_slice = slice( pos - self.seqnum_nbits, pos )
    pos -= self.seqnum_nbits

    self.payload_slice = slice( pos - self.payload_nbits, pos )
    pos -= self.payload_nbits

  def mk_msg( self, dest, src, seqnum, payload ):

    bits = Bits( self.nbits )
    bits[ self.dest_slice    ] = dest
    bits[ self.src_slice     ] = src
    bits[ self.seqnum_slice  ] = seqnum
    bits[ self.payload_slice ] = payload

    return bits

#-------------------------------------------------------------------------
# NetMsgFromBits
#-------------------------------------------------------------------------

class NetMsgFromBits (Model):

  def __init__( self, netmsg_params ):

    self.bits     = InPort  ( netmsg_params.nbits         )

    self.dest     = OutPort ( netmsg_params.srcdest_nbits )
    self.src      = OutPort ( netmsg_params.srcdest_nbits )
    self.seqnum   = OutPort ( netmsg_params.seqnum_nbits  )
    self.payload  = OutPort ( netmsg_params.payload_nbits )

    self.netmsg_params = netmsg_params

    # Connections

    connect( self.bits[ self.netmsg_params.dest_slice    ], self.dest    )
    connect( self.bits[ self.netmsg_params.src_slice     ], self.src     )
    connect( self.bits[ self.netmsg_params.seqnum_slice  ], self.seqnum  )
    connect( self.bits[ self.netmsg_params.payload_slice ], self.payload )

  def line_trace( self ):
    return "{}:{}:{}:{}" \
      .format( self.dest.value, self.src.value, self.seqnum.value,
               self.payload.value )

#-------------------------------------------------------------------------
# NetMsgToBits
#-------------------------------------------------------------------------

class NetMsgToBits (Model):

  def __init__( self, netmsg_params ):

    self.dest    = InPort  ( netmsg_params.srcdest_nbits )
    self.src     = InPort  ( netmsg_params.srcdest_nbits )
    self.seqnum  = InPort  ( netmsg_params.seqnum_nbits  )
    self.payload = InPort  ( netmsg_params.payload_nbits )

    self.bits    = OutPort ( netmsg_params.nbits         )

    self.netmsg_params = netmsg_params

    # Connections

    connect( self.bits[ self.netmsg_params.dest_slice     ], self.dest    )
    connect( self.bits[ self.netmsg_params.src_slice      ], self.src     )
    connect( self.bits[ self.netmsg_params.seqnum_slice   ], self.seqnum  )
    connect( self.bits[ self.netmsg_params.payload_slice  ], self.payload )

  def line_trace( self ):
    return "{}:{}:{}:{}" \
      .format( self.dest.value, self.src.value, self.seqnum.value,
               self.payload.value )
