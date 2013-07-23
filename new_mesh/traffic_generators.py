#=========================================================================
# Mesh Unit Test
#=========================================================================

from new_pmlib  import NetMsg
from math       import sqrt

import random

#-------------------------------------------------------------------------
# mk_msg
#-------------------------------------------------------------------------
def mk_msg( dest, src, seqnum, payload ):
  msg         = NetMsg( nrouters, nmessages, payload_nbits )
  msg.src     = src
  msg.dest    = dest
  msg.seqnum  = seqnum
  msg.payload = payload
  return msg

#-------------------------------------------------------------------------
# terminal_msgs
#-------------------------------------------------------------------------
def terminal_msgs():

  size = 8

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( nrouters ):
    for j in xrange( size ):
      dest = i
      mk_net_msg( dest, i, j, j )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# nearest_neighbor_east_msgs
#-------------------------------------------------------------------------
def nearest_neighbor_east_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( nrouters ):
    for j in xrange( size ):
      if ( i == nrouters-1 ):
        dest = 0
      else:
        dest = i + 1

      #data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, j )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# nearest_neighbor_west_msgs
#-------------------------------------------------------------------------
def nearest_neighbor_west_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( nrouters ):
    for j in xrange( size ):
      if ( i == 0 ):
        dest = nrouters-1
      else:
        dest = i - 1

      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# hotspot_msgs
#-------------------------------------------------------------------------
def hotspot_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( nrouters ):
    for j in xrange( size ):

      # all routers send to node 0
      dest = 0
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# partition_msgs
#-------------------------------------------------------------------------
def partition_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  # Partition the network into halves
  partition_edge = nrouters / 2

  for i in xrange( nrouters ):
    for j in xrange( size ):
      if ( i < partition_edge ):
        dest_roll = random.randint( 0, partition_edge - 1 )
      else:
        dest_roll = random.randint( partition_edge, nrouters - 1 )
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest_roll, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# uniform_random_msgs
#-------------------------------------------------------------------------
def uniform_random_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( nrouters ):
    for j in xrange( size ):
      dest_roll = random.randint( 0, nrouters - 1 )
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest_roll, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# tornado_msgs
#-------------------------------------------------------------------------
def tornado_msgs( size ):

  src_msgs  = [ [] for x in xrange( nrouters ) ]
  sink_msgs = [ [] for x in xrange( nrouters ) ]

  # Syntax helpers

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  nrouters_1D = int( sqrt( nrouters ) )

  for i in xrange( nrouters ):
    for j in xrange( size ):
      x = ( (i%nrouters_1D) + int( nrouters_1D/2 ) - 1 ) % nrouters_1D
      y = ( (i/nrouters_1D) + int( nrouters_1D/2 ) - 1 ) % nrouters_1D

      dest = x + nrouters_1D * y
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]
