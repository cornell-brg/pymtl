#=========================================================================
# MeshNetworkBL.py
#=========================================================================

from new_pymtl   import *
from new_pmlib   import InValRdyBundle, OutValRdyBundle, NetMsg
from collections import deque
from math        import sqrt

#=========================================================================
# MeshNetworkBL
#=========================================================================
class MeshNetworkBL( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, nrouters, nmessages, payload_nbits, nentries ):

    # ensure nrouters is a perfect square
    assert sqrt( nrouters ) % 1 == 0

    s.nrouters  = nrouters
    s.nentries  = nentries
    s.config    = [ nrouters, nmessages, payload_nbits ]

    s.in_ = [ InValRdyBundle ( NetMsg( *s.config ) ) for x in range( nrouters ) ]
    s.out = [ OutValRdyBundle( NetMsg( *s.config ) ) for x in range( nrouters ) ]

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.output_fifos = [ deque() for x in range( s.nrouters ) ]

    # Simulate the network
    @s.tick
    def network_logic():

      # Dequeue logic
      for i, outport in enumerate( s.out ):
        if outport.val and outport.rdy:
          s.output_fifos[ i ].popleft()

      # Enqueue logic
      for i, inport in enumerate( s.in_ ):
        if inport.val and inport.rdy:
          s.output_fifos[ inport.msg.dest ].append( inport.msg[:] )

      # Set output signals
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
      in_ = s.in_[ i ]
      out = s.out[ i ]
      in_str  = in_.to_str( in_.msg.dest )
      out_str = out.to_str( out.msg.dest )
      router_traces += ['{} {}'.format( in_str, out_str ) ]

    return '|'.join( router_traces )

