#=========================================================================
# Sorter Behavioral-Level Model
#=========================================================================
# A behavioral-levle model has accurately models the function of the
# target hardware but does not necessarily attempt to model the number of
# cycles it might take to execute the hardware. It is a more abstract
# modeling technique.

from pymtl import *

class SorterBL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self ):
    self.in_ = [ InPort  ( 16 ) for x in range(4) ]
    self.out = [ OutPort ( 16 ) for x in range(4) ]

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    values = [ x.value for x in self.in_ ]
    values.sort()
    for i, value in enumerate( values ):
      self.out[i].value = value

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} () {:04x} {:04x} {:04x} {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint,
               self.in_[2].value.uint, self.in_[3].value.uint,
               self.out[0].value.uint, self.out[1].value.uint,
               self.out[2].value.uint, self.out[3].value.uint )

