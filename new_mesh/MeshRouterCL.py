#=========================================================================
# MeshRouterCL.py
#=========================================================================

from new_pymtl        import *
from new_pmlib        import InValRdyBundle, OutValRdyBundle, NetMsg
from new_pmlib.queues import InValRdyQueue,  OutValRdyQueue
from collections      import deque
from math             import sqrt

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

    s.input_buffers = [ InValRdyQueue( s.msg_type, s.nentries )
                        for i in range( 5 ) ]
    # TODO: this would ideally be 1 element of buffering, but since
    # dequeue and signal setting are all done in the same tick, we can't
    # pipeline this!
    s.output_regs   = [ OutValRdyQueue( s.msg_type, 1 )
                        for i in range( 5 ) ]
    s.priorities    = [ 0 ] * 5

    # Connect

    for i in range( 5 ):
      s.connect( s.in_[ i ], s.input_buffers[ i ].in_ )
      s.connect( s.out[ i ], s.output_regs  [ i ].out )

    # Logic

    @s.tick
    def router_logic():

      # Xfer data from input ports to input_buffers
      for i in range( 5 ):
        s.input_buffers[ i ].xtick()
        s.output_regs[ i ].xtick()


      # Arbitration and Crossbar Traversal
      s.winners = []
      for i in range( 5 ):

        if not s.output_regs[ i ].is_full():
          data = s.arbitrate( i )
          if data != None:
            s.output_regs[ i ].enq( data )

      # Deque winners
      for winner in s.winners:
        winner.deq()


      # Set output ports
      #for i in range( 5 ):

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
      if not request_q.is_empty():
        if s.route_compute( request_q.peek().dest ) == output:
          #print "*** i", i, "wins!   dest", s.route_compute( request_q[ 0 ].dest ),
          s.priorities[ output ] = ( i + 1 ) % 5
          s.winners.append( request_q )
          return request_q.peek()
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



