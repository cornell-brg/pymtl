#=========================================================================
# RegIncrFlat
#=========================================================================

from pymtl import *

class RegIncrFlat( Model ):

  def __init__( self ):
    self.in_ = InPort(16)
    self.out = OutPort(16)

    self.reg = Wire(16)

  # Register

  @posedge_clk
  def register( self ):
    self.reg.next = self.in_.value

  # Incrementer

  @combinational
  def incrementer( self ):
    self.out.value = self.reg.value + 1

