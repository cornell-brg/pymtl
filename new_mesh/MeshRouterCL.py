#=========================================================================
# MeshRouterCL.py
#=========================================================================

from new_pymtl   import *
from new_pmlib   import InValRdyBundle, OutValRdyBundle, NetMsg
from collections import deque
from math        import sqrt

#=========================================================================
# MeshRouterCL
#=========================================================================
class MeshRouterCL( Model ):

  NORTH = 0
  EAST  = 1
  SOUTH = 2
  WEST  = 3
  TERM  = 4

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, id_, nrouters, nmessages, payload_nbits, nentries ):

    s.id_       = id_
    s.xnodes    = int( sqrt( nrouters ) )
    s.x         = id_ % s.xnodes
    s.y         = id_ / s.xnodes
    s.msg_type  = NetMsg( nrouters, nmessages, payload_nbits )
    s.nentries  = nentries

    #s.params     = [ nrouters, nmessages, payload_nbits, buffering ]
    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_ = [ InValRdyBundle ( s.msg_type ) for x in range( 5 ) ]
    s.out = [ OutValRdyBundle( s.msg_type ) for x in range( 5 ) ]

    s.east = ( s.in_[ s.EAST ], s.out[ s.EAST ] )
    s.west = ( s.in_[ s.WEST ], s.out[ s.WEST ] )

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    # Instantiate buffers

    s.input_buffers = [ deque() for x in range( 5 ) ]
    s.output_regs   = [ None ] * 5
    s.priorities    = [ 0 ] * 5

    # Logic

    @s.tick
    def router_logic():

      # Dequeue logic
      for i, outport in enumerate( s.out ):
        if outport.val and outport.rdy:
          s.output_regs[ i ] = None

      # Enqueue logic
      for i, inport in enumerate( s.in_ ):
        if inport.val and inport.rdy:
          s.input_buffers[ i ].append( inport.msg[:] )

      # Arbitration and Crossbar Traversal
      s.winners = []
      for i in range( 5 ):
        if not s.output_regs[ i ]:
          s.output_regs[ i ] = s.arbitrate( i )

      # Deque winners
      for i in s.winners:
        i.popleft()

      ## Crossbar Traversal
      #for i in range( 5 ):
      #  buffer = s.input_buffers[ i ]
      #  if len( buffer ) > 0:
      #    port = s.route_compute( buffer[ 0 ].dest )
      #    if s.output_regs[ port ] is None:
      #      msg = buffer.popleft()
      #      s.output_regs[ port ] = msg

      # Set Signals
      for i in range( 5 ):

        in_full  = len( s.input_buffers[ i ] ) == s.nentries
        out_full = s.output_regs[ i ] is not None

        s.out[ i ].val.next = out_full
        s.in_[ i ].rdy.next = not in_full
        if out_full:
          s.out[ i ].msg.next = s.output_regs[ i ]

  #-----------------------------------------------------------------------
  # route_compute
  #-----------------------------------------------------------------------
  # dimension-ordered (x then y) routing algorithm
  def route_compute( s, dest ):

    x_dest = dest.uint() % s.xnodes
    y_dest = dest.uint() / s.xnodes

    if   x_dest < s.x: return s.WEST
    elif x_dest > s.x: return s.EAST
    elif y_dest < s.y: return s.NORTH
    elif y_dest > s.y: return s.SOUTH
    else:
      assert x_dest == s.x
      assert y_dest == s.y
      return s.TERM

  #-----------------------------------------------------------------------
  # arbitrate
  #-----------------------------------------------------------------------
  # round robin arbitration algorithm
  def arbitrate( s, output ):
    first = s.priorities[ output ]
    order = range( 5 )[first:] + range( 5 )[:first]
    #print "arbitrating for r:", s.id_, "out:", output, order,
    for i in order:
      request_q = s.input_buffers[ i ]
      if len( request_q ) > 0:
        if s.route_compute( request_q[ 0 ].dest ) == output:
          #print "*** i", i, "wins!   dest", s.route_compute( request_q[ 0 ].dest ),
          s.priorities[ output ] = ( i + 1 ) % 5
          s.winners.append( request_q )
          return request_q[ 0 ]
    #print "NO WINNER"


  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    router_traces = []
    for i in range( 5 ):
      in_str  = s.in_[ i ].to_str( s.in_[ i ].msg.payload )
      out_str = s.out[ i ].to_str( s.out[ i ].msg.payload )
      router_traces += ['{} {}'.format( in_str, out_str ) ]

    return '|'.join( router_traces )



