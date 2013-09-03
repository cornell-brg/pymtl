#=========================================================================
# NetMsg
#=========================================================================
# A network message consists of the route information ( dest, src ),
# sequence number and payload fields.
#
# The network message is parameterized for given routers present in the
# network, number of total messages  and the payload bitwidth. For example,
# 3 routers in the system, total of 256 messages and payload_nbits = 32,
# would have a network message format as below:
#
#   45  43 42  40 39    32 31             0
#  +------+------+--------+---------------+
#  | dest | src  | seqnum | payload_nbits |
#  +------+------+--------+---------------+
#

from new_pymtl import *

#-------------------------------------------------------------------------
# NetMsg
#-------------------------------------------------------------------------
# BitStruct designed to create network messages.
class NetMsg( BitStructDefinition ):

  def __init__( s, nrouters, nmessages, payload_nbits ):

    # Specify the size of each field

    srcdest_nbits = get_sel_nbits( nrouters  )
    seqnum_nbits  = get_sel_nbits( nmessages )

    # Specify fields

    s.dest    = BitField( srcdest_nbits )
    s.src     = BitField( srcdest_nbits )
    s.seqnum  = BitField( seqnum_nbits  )
    s.payload = BitField( payload_nbits )

    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits

  # TODO: Should this be a class method?
  def mk_msg( s, dest, src, seqnum, payload ):

    msg         = s()
    msg.dest    = dest
    msg.src     = src
    msg.seqnum  = seqnum
    msg.payload = payload

    return msg

  #s.hash = hash(( num_routers, num_messages, payload_nbits ))
  #def __hash__( s ):
  #  return s.hash

  # TODO: Should this be a class method?
  def __str__( s ):
    return "{}:{}:{}:{}".format( s.dest, s.src, s.seqnum, s.payload )

