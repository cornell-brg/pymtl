#=========================================================================
# Sorter Cycle-Level Model
#=========================================================================
# A cycle-level model has the correct function and also tries to model
# the number of cycles it takes to execute this function. Often in our
# cycle-level models we simply put all of the logic in a single
# posedge_clk concurrent block. In this model, we use the built-in Python
# function for sorting and then just delay the output for one more cycle.

from pymtl import *

class SorterCL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self ):

    # Ports

    self.in_ = [ InPort  ( 16 ) for x in range(4) ]
    self.out = [ OutPort ( 16 ) for x in range(4) ]

    # Intermediate buffer

    self.buf = [ 0, 0, 0, 0 ]

  #-----------------------------------------------------------------------
  # Sequential logic
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # Delay by one cycle and write outputs

    for i, value in enumerate( self.buf ):
      self.out[i].value = value

    # Sort behavioral level

    self.buf = [ x.value[:] for x in self.in_ ]
    self.buf.sort()

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} () {:04x} {:04x} {:04x} {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint,
               self.in_[2].value.uint, self.in_[3].value.uint,
               self.out[0].value.uint, self.out[1].value.uint,
               self.out[2].value.uint, self.out[3].value.uint )

