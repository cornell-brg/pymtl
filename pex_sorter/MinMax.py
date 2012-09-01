#=========================================================================
# MinMax
#=========================================================================

from pymtl import *

class MinMax( Model ):

  def __init__( self ):

    self.in0 = InPort( 16 )
    self.in1 = InPort( 16 )

    self.min = OutPort( 16 )
    self.max = OutPort( 16 )

  @combinational
  def comb_logic( self ):

    if self.in0.value >= self.in1.value:
      self.max.value = self.in0.value
      self.min.value = self.in1.value
    else:
      self.max.value = self.in1.value
      self.min.value = self.in0.value

