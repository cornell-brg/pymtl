#=========================================================================
# Sorter Behavioral-Level Model
#=========================================================================
# A functional-level model the functional behavior of the target hardware
# but not the timing.

from pymtl import *

class SorterFL( Model ):

  def __init__( s ):
    s.in_ = [ InPort  ( 16 ) for x in range(4) ]
    s.out = [ OutPort ( 16 ) for x in range(4) ]

  def elaborate_logic( s ):

    @s.tick
    def logic():

      values = [ x.value for x in s.in_ ]
      values.sort()
      for i, value in enumerate( values ):
        s.out[i].next = value

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} {} {} () {} {} {} {}" \
      .format( s.in_[0], s.in_[1],
               s.in_[2], s.in_[3],
               s.out[0], s.out[1],
               s.out[2], s.out[3] )

