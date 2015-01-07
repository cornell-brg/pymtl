#=========================================================================
# MeshRouterCL.py
#=========================================================================

from __future__ import print_function

from math        import sqrt
from collections import deque

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle, NetMsg
from pclib.cl   import InValRdyQueue,  OutValRdyQueue

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

    s.in_ = InValRdyBundle [ 5 ]( s.msg_type )
    s.out = OutValRdyBundle[ 5 ]( s.msg_type )


  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    # Instantiate buffers

    s.input_buffers = InValRdyQueue [ 5 ]( s.msg_type, s.nentries )
    s.output_regs   = OutValRdyQueue[ 5 ]( s.msg_type, 1          )
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
    #print("arbitrating for r:", s.id_, "out:", output, order,)
    for i in order:
      request_q = s.input_buffers[ i ]
      if not request_q.is_empty():
        if s.route_compute( request_q.peek().dest ) == output:
          #print("*** i", i, "wins!   dest", s.route_compute(request_q[0].dest),)
          s.priorities[ output ] = ( i + 1 ) % 5
          s.winners.append( request_q )
          return request_q.peek()
    #print("NO WINNER")


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



