#=========================================================================
# MeshNetworkBL
#=========================================================================

from new_pymtl    import *
from new_pmlib    import InValRdyBundle, OutValRdyBundle, NetMsg
from MeshRouterCL import MeshRouterCL
from collections  import deque
from math         import sqrt

class MeshNetworkCL( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, nrouters, nmessages, payload_nbits, nentries ):

    # ensure nrouters is a perfect square
    assert sqrt( nrouters ) % 1 == 0

    s.nrouters  = nrouters
    s.bparams     = [ nrouters, nmessages, payload_nbits ]
    s.params    = [ nrouters, nmessages, payload_nbits, nentries ]

    s.in_ = [ InValRdyBundle ( NetMsg( *s.bparams ) ) for x in range( nrouters ) ]
    s.out = [ OutValRdyBundle( NetMsg( *s.bparams ) ) for x in range( nrouters ) ]

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    # instantiate routers

    s.routers = [ MeshRouterCL( x, *s.params ) for x in xrange( s.nrouters ) ]

    # connect injection terminals

    for i in xrange( s.nrouters ):
      s.connect( s.in_[i],  s.routers[i].in_[4] )
      s.connect( s.out[i],  s.routers[i].out[4] )

    # connect mesh

    nrouters_1D = int( sqrt( s.nrouters ) )

    for j in range( nrouters_1D ):
      for i in range( nrouters_1D ):
        id_ = i + j * nrouters_1D

        # East
        if i + 1 < nrouters_1D:
          east  = id_ + 1
          s.connect( s.routers[ id_ ].out[ 1 ], s.routers[ east  ].in_[ 3 ] )
          s.connect( s.routers[ id_ ].in_[ 1 ], s.routers[ east  ].out[ 3 ] )

        # South
        if j + 1 < nrouters_1D:
          south = id_ + nrouters_1D
          s.connect( s.routers[ id_ ].out[ 2 ], s.routers[ south ].in_[ 0 ] )
          s.connect( s.routers[ id_ ].in_[ 2 ], s.routers[ south ].out[ 0 ] )


  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    router_traces = []
    for i in range( s.nrouters ):
      in_str  = s.in_[ i ].to_str( s.in_[ i ].msg.dest )
      out_str = s.out[ i ].to_str( s.out[ i ].msg.dest )
      # Detailed
      NORTH = s.routers[ i ].out[ 0 ].to_str( s.routers[ i ].out[ 0 ].msg.dest )
      EAST  = s.routers[ i ].out[ 1 ].to_str( s.routers[ i ].out[ 1 ].msg.dest )
      SOUTH = s.routers[ i ].out[ 2 ].to_str( s.routers[ i ].out[ 2 ].msg.dest )
      WEST  = s.routers[ i ].out[ 3 ].to_str( s.routers[ i ].out[ 3 ].msg.dest )
      router_traces += ['{} ({}{}{}{}) {}'.format( in_str,
        WEST, NORTH, SOUTH, EAST, out_str ) ]
      # Succinct
      #router_traces += ['{} {}'.format( in_str, out_str )

    return '|'.join( router_traces )

