#=========================================================================
# MeshNetworkBL
#=========================================================================

from new_pymtl   import *
from new_pmlib   import InValRdyBundle, OutValRdyBundle, NetMsg
from collections import deque
from math        import sqrt

class MeshNetworkBL( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, nrouters, nmessages, payload_nbits, nentries ):

    # ensure nrouters is a perfect square
    assert sqrt( nrouters ) % 1 == 0

    s.nrouters  = nrouters
    s.nentries  = nentries
    s.config    = [ nrouters, nmessages, payload_nbits ]

    s.in_ = [ InValRdyBundle ( NetMsg( *s.config ) ) for x in range( nrouters ) ]
    s.out = [ OutValRdyBundle( NetMsg( *s.config ) ) for x in range( nrouters ) ]

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.output_fifos = [ deque() for x in range( s.nrouters ) ]

    # Simulate the network
    @s.tick
    def network_logic():

      # Dequeue logic
      for i, output in enumerate( s.out ):
        if output.val and output.rdy:
          x = s.output_fifos[ i ].popleft()

      # Enqueue logic
      for i, input in enumerate( s.in_ ):
        if input.val and input.rdy:
          s.output_fifos[ input.msg.dest ].append( Bits( input.msg.nbits, input.msg ) )

      # Set valid & ready
      for i, fifo in enumerate( s.output_fifos ):
        is_full  = len( fifo ) == s.nentries
        is_empty = len( fifo ) == 0
        s.out[ i ].val.next = not is_empty
        s.in_[ i ].rdy.next = not is_full
        if not is_empty:
          s.out[ i ].msg.next = fifo[ 0 ]

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    router_traces = []
    for i in range( s.nrouters ):
      in_str  = s.in_[ i ].to_str( s.in_[ i ].msg.seqnum )
      out_str = s.in_[ i ].to_str( s.out[ i ].msg.seqnum )
      router_traces += ['{} {}'.format( in_str, out_str ) ]

    return '|'.join( router_traces )

