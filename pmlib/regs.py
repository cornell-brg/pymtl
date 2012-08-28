#=========================================================================
# Registers
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

#-------------------------------------------------------------------------
# Reg
#-------------------------------------------------------------------------

class Reg( Model ):

  def __init__( self, W = 16 ):
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value

#-------------------------------------------------------------------------
# RegEn
#-------------------------------------------------------------------------

class RegEn( Model ):

  def __init__( self, W = 16 ):
    self.en = InPort( 1 )
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @posedge_clk
  def seq_logic( self ):
    if self.en.value == 1:
      self.out.next = self.in_.value

#-------------------------------------------------------------------------
# RegRst
#-------------------------------------------------------------------------
#
# If rst = 1, the value will be reset to 0 on the next clock edge
#

class RegRst( Model ):

  def __init__( self, W = 16 ):
    self.rst = InPort( 1 )
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @posedge_clk
  def seq_logic( self ):
    if self.rst.value == 1:
      self.out.next = 0
    else:
      self.out.next = self.in_.value

#-------------------------------------------------------------------------
# RegEnRst
#-------------------------------------------------------------------------
#
# If rst = 1, the value will be reset to 0 on the next clock edge,
# no matter whether en = 1 or not 
#

class RegEnRst( Model ):

  def __init__( self, W = 16 ):
    self.rst = InPort( 1 )
    self.en = InPort( 1 )
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @posedge_clk
  def seq_logic( self ):
    if self.rst.value == 1:
      self.out.next = 0
    elif self.en.value == 1:
      self.out.next = self.in_.value

