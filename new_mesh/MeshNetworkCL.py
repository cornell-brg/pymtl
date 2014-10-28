#=========================================================================
# MeshNetworkCL
#=========================================================================

from pymtl    import *
from new_pmlib    import InValRdyBundle, OutValRdyBundle, NetMsg
from MeshRouterCL import MeshRouterCL
from math         import sqrt

#=========================================================================
# MeshNetworkCL.py
#=========================================================================
class MeshNetworkCL( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, nrouters, nmessages, payload_nbits, nentries ):

    # ensure nrouters is a perfect square
    assert sqrt( nrouters ) % 1 == 0

    s.nrouters  = nrouters
    s.params    = [ nrouters, nmessages, payload_nbits, nentries ]

    net_msg = NetMsg( nrouters, nmessages, payload_nbits )
    s.in_   = InValRdyBundle [ nrouters ]( net_msg )
    s.out   = OutValRdyBundle[ nrouters ]( net_msg )

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    # instantiate routers

    R = Router = MeshRouterCL
    s.routers = [ Router( x, *s.params ) for x in xrange( s.nrouters ) ]

    # connect injection terminals

    for i in xrange( s.nrouters ):
      s.connect( s.in_[i],  s.routers[i].in_[ R.TERM ] )
      s.connect( s.out[i],  s.routers[i].out[ R.TERM ] )

    # connect mesh routers

    nrouters_1D = int( sqrt( s.nrouters ) )

    for j in range( nrouters_1D ):
      for i in range( nrouters_1D ):
        idx     = i + j * nrouters_1D
        current = s.routers[ idx ]

        # East
        if i + 1 < nrouters_1D:
          right = s.routers[ idx + 1 ]
          s.connect( current.out[ R.EAST ], right.in_[ R.WEST ] )
          s.connect( current.in_[ R.EAST ], right.out[ R.WEST ] )

        # South
        if j + 1 < nrouters_1D:
          below = s.routers[ idx + nrouters_1D ]
          s.connect( current.out[ R.SOUTH ], below.in_[ R.NORTH ] )
          s.connect( current.in_[ R.SOUTH ], below.out[ R.NORTH ] )


  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    router_traces = []
    for i, r in enumerate( s.routers ):

      in_str  = s.in_[ i ].to_str( s.in_[ i ].msg.dest )
      out_str = s.out[ i ].to_str( s.out[ i ].msg.dest )

      west    = r.out[ r.WEST  ].to_str( r.out[ r.WEST  ].msg.dest )
      north   = r.out[ r.NORTH ].to_str( r.out[ r.NORTH ].msg.dest )
      south   = r.out[ r.SOUTH ].to_str( r.out[ r.SOUTH ].msg.dest )
      east    = r.out[ r.EAST  ].to_str( r.out[ r.EAST  ].msg.dest )

      router_traces  += ['{} ({}{}{}{}) {}'.format( in_str,
                         west, north, south, east, out_str ) ]

      #router_traces += ['{} {}'.format( in_str, out_str ) ]

    return '|'.join( router_traces )

