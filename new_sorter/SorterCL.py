#=========================================================================
# Sorter Cycle-Level Model
#=========================================================================
# A cycle-level model has the correct function and also tries to model
# the number of cycles it takes to execute this function. Often in our
# cycle-level models we simply put all of the logic in a single
# posedge_clk concurrent block. In this model, we use the built-in Python
# function for sorting and then just delay the output for one more cycle.

from new_pymtl import *

class SorterCL( Model ):

  def __init__( s, nbits=16, nports=4 ):

    s.in_ = [ InPort  ( nbits ) for x in range( nports ) ]
    s.out = [ OutPort ( nbits ) for x in range( nports ) ]

    s.buf = [ 0 ] * nports

  def elaborate_logic( s ):

    @s.tick
    def logic():

      # Delay by one cycle and write outputs

      for i, value in enumerate( s.buf ):
        s.out[i].value = value

      # Sort behavioral level

      s.buf = [ x.value[:] for x in s.in_ ]
      s.buf.sort()

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} {} {} () {} {} {} {}" \
      .format( s.in_[0], s.in_[1],
               s.in_[2], s.in_[3],
               s.out[0], s.out[1],
               s.out[2], s.out[3] )

