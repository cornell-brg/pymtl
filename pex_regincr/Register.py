#=========================================================================
# Register
#=========================================================================

from pymtl import *

class Register( Model ):

  def __init__( self, bits ):
    self.in_ = InPort  ( bits )
    self.out = OutPort ( bits )

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value

  def line_trace( self ):
    return "{} ({}) {}" \
      .format( self.in_.value, self.out.value, self.out.value )

