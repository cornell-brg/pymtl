import sys
sys.path.append('..')
from pymtl import *

class RegIncrFlat( Model ):

  def __init__( self ):
    self.in_ = InPort(16)
    self.out = OutPort(16)

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value + 1
