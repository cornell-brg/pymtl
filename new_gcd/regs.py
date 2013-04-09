#=========================================================================
# Register with different implementations
#=========================================================================

from new_pymtl import *

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Reg( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):
    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

  def elaborate_logic( self ):
    @self.posedge_clk
    def seq_logic():
      self.out.next = self.in_

  def line_trace( self ):
    return "{:04x} ({:04x}) {:04x}" \
      .format( self.in_.uint(), self.out.uint(), self.out.uint() )

#-------------------------------------------------------------------------
# Register with enable signal
#-------------------------------------------------------------------------

class RegEn( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):
    self.in_ = InPort  ( nbits )
    self.en  = InPort  ( 1     )
    self.out = OutPort ( nbits )

  def elaborate_logic( self ):
    @self.posedge_clk
    def seq_logic():
      if self.en:
        self.out.next = self.in_

  def line_trace( self ):
    return "{:04x} ({:04x}) {:04x}" \
      .format( self.in_.uint(), self.out.uint(), self.out.uint() )

#-------------------------------------------------------------------------
# Register with reset signal
#-------------------------------------------------------------------------
# If reset = 1, then value will be reset to a default reset_value on the
# next clock edge

class RegRst( Model ):

  @capture_args
  def __init__( self, nbits = 1, reset_value = 0 ):

    # Ports

    self.in_ = InPort( nbits )
    self.out = OutPort( nbits )

    # Constants

    self.reset_value = reset_value

  def elaborate_logic( self ):
    @self.posedge_clk
    def seq_logic():
      if self.reset:
        self.out.next = self.reset_value
      else:
        self.out.next = self.in_

  def line_trace( self ):
    return "{:04x} ({:04x}) {:04x}" \
      .format( self.in_.uint(), self.out.uint(), self.out.uint() )

#-------------------------------------------------------------------------
# Register with reset and enable
#-------------------------------------------------------------------------
# If reset = 1, the value will be reset to default reset_value on the
# next clock edge, no matter whether en = 1 or not

class RegEnRst( Model ):

  @capture_args
  def __init__( self, nbits = 1, reset_value = 0 ):

    # Ports

    self.en  = InPort( 1 )
    self.in_ = InPort( nbits )
    self.out = OutPort( nbits )

    # Constants

    self.reset_value = reset_value

  def elaborate_logic( self ):
    @self.posedge_clk
    def seq_logic():
      if self.reset:
        self.out.next = self.reset_value
      elif self.en:
        self.out.next = self.in_

  def line_trace( self ):
    return "{:04x} ({:04x}) {:04x}" \
      .format( self.in_.uint(), self.out.uint(), self.out.uint() )

