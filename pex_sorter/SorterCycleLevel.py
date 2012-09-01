#=========================================================================
# SorterCycleLevel
#=========================================================================

from pymtl import *

class SorterCycleLevel( Model ):

  def __init__( self ):

    self.in_ = [ InPort( 16 )  for x in range(4) ]
    self.out = [ OutPort( 16 ) for x in range(4) ]

    self.buf0 = [ 0, 0, 0, 0 ]
    self.buf1 = [ 0, 0, 0, 0 ]

  @posedge_clk
  def seq_logic( self ):

    # Delay by one cycle and write outputs

    self.buf1 = self.buf0
    for i, value in enumerate( self.buf1 ):
      self.out[i].value = value

    # Sort behavioral level

    self.buf0 = [ x.value for x in self.in_ ]
    self.buf0.sort()

