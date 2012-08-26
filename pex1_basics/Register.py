#=========================================================================
# Register
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

class Register( Model ):

  def __init__( self, bits ):
    self.in_ = InPort( bits )
    self.out = OutPort( bits)

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value

