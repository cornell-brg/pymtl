#=========================================================================
# Sorter Behavioral-Level Model
#=========================================================================
# A behavioral-levle model has accurately models the function of the
# target hardware but does not necessarily attempt to model the number of
# cycles it might take to execute the hardware. It is a more abstract
# modeling technique.

from pymtl import *

class SorterBL( Model ):

  def __init__( s ):
    s.in_ = [ InPort  ( 16 ) for x in range(4) ]
    s.out = [ OutPort ( 16 ) for x in range(4) ]

  def elaborate_logic( s ):

    @s.tick
    def logic():

      values = [ x.value for x in s.in_ ]
      values.sort()
      for i, value in enumerate( values ):
        s.out[i].value = value

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} {} {} () {} {} {} {}" \
      .format( s.in_[0], s.in_[1],
               s.in_[2], s.in_[3],
               s.out[0], s.out[1],
               s.out[2], s.out[3] )

