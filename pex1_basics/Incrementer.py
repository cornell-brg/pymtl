import sys
sys.path.append('..')
from pymtl import *

class Incrementer( Model ):

  def __init__( self, bits ):
    self.in_ = InPort( bits )
    self.out = OutPort( bits)

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value + 1
