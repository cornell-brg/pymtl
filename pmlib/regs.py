#=========================================================================
# Register with different implementations
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Reg( Model ):

  def __init__( self, nbits = 1 ):
    self.in_ = InPort( nbits )
    self.out = OutPort( nbits )

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value

#-------------------------------------------------------------------------
# Register with enable signal
#-------------------------------------------------------------------------

class RegEn( Model ):

  def __init__( self, nbits = 1 ):
    self.in_ = InPort( nbits )
    self.en  = InPort( 1 )
    self.out = OutPort( nbits )

  @posedge_clk
  def seq_logic( self ):
    if self.en.value:
      self.out.next = self.in_.value

#-------------------------------------------------------------------------
# Register with reset signal
#-------------------------------------------------------------------------
#
# If reset = 1, the value will be reset to a default reset_value on the next clock edge
#

class RegRst( Model ):

  def __init__( self, nbits = 1, reset_value = 0 ):
    self.in_ = InPort( nbits )
    self.out = OutPort( nbits )
    self.reset_value = reset_value

  @posedge_clk
  def seq_logic( self ):
    if self.reset.value:
      self.out.next = self.reset_value
    else:
      self.out.next = self.in_.value

#-------------------------------------------------------------------------
# Register with reset and enable
#-------------------------------------------------------------------------
#
# If reset = 1, the value will be reset to default reset_value on the next clock edge,
# no matter whether en = 1 or not 
#

class RegEnRst( Model ):

  def __init__( self, nbits = 1, reset_value = 0 ):
    self.en  = InPort( 1 )
    self.in_ = InPort( nbits )
    self.out = OutPort( nbits )
    self.reset_value = reset_value

  @posedge_clk
  def seq_logic( self ):
    if self.reset.value:
      self.out.next = self.reset_value
    elif self.en.value:
      self.out.next = self.in_.value

