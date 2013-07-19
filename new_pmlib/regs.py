#=========================================================================
# Register with different implementations
#=========================================================================

from new_pymtl import *

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Reg( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def seq_logic():
      s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-------------------------------------------------------------------------
# Register with enable signal
#-------------------------------------------------------------------------

class RegEn( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):
    s.in_ = InPort  ( nbits )
    s.en  = InPort  ( 1     )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def seq_logic():
      if s.en:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-------------------------------------------------------------------------
# Register with reset signal
#-------------------------------------------------------------------------
# If reset = 1, then value will be reset to a default reset_value on the
# next clock edge

class RegRst( Model ):

  @capture_args
  def __init__( s, nbits = 1, reset_value = 0 ):

    # Ports

    s.in_ = InPort( nbits )
    s.out = OutPort( nbits )

    # Constants

    s.reset_value = reset_value

  def elaborate_logic( s ):
    @s.posedge_clk
    def seq_logic():
      if s.reset:
        s.out.next = s.reset_value
      else:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-------------------------------------------------------------------------
# Register with reset and enable
#-------------------------------------------------------------------------
# If reset = 1, the value will be reset to default reset_value on the
# next clock edge, no matter whether en = 1 or not

class RegEnRst( Model ):

  @capture_args
  def __init__( s, nbits = 1, reset_value = 0 ):

    # Ports

    s.en  = InPort( 1 )
    s.in_ = InPort( nbits )
    s.out = OutPort( nbits )

    # Constants

    s.reset_value = reset_value

  def elaborate_logic( s ):
    @s.posedge_clk
    def seq_logic():
      if s.reset:
        s.out.next = s.reset_value
      elif s.en:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

