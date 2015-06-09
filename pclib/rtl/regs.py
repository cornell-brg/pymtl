#=======================================================================
# regs.py
#=======================================================================

from pymtl import *

#-----------------------------------------------------------------------
# Reg
#-----------------------------------------------------------------------
class Reg( Model ):
  '''Register without enable or reset.'''

  def __init__( s, dtype = 1 ):

    s.in_ = InPort  ( dtype )
    s.out = OutPort ( dtype )

    @s.posedge_clk
    def seq_logic():
      s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-----------------------------------------------------------------------
# RegEn
#-----------------------------------------------------------------------
class RegEn( Model ):
  '''Register with enable signal.'''

  def __init__( s, dtype = 1 ):

    s.in_ = InPort  ( dtype )
    s.en  = InPort  ( 1     )
    s.out = OutPort ( dtype )

    @s.posedge_clk
    def seq_logic():
      if s.en:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-----------------------------------------------------------------------
# RegRst
#-----------------------------------------------------------------------
class RegRst( Model ):
  '''Register with reset signal.

  When reset == 1 the register will be set to reset_value on the next
  clock edge.
  '''

  def __init__( s, dtype = 1, reset_value = 0 ):

    s.in_ = InPort( dtype )
    s.out = OutPort( dtype )

    @s.posedge_clk
    def seq_logic():
      if s.reset:
        s.out.next = reset_value
      else:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

#-------------------------------------------------------------------------
# Register with reset and enable
#-------------------------------------------------------------------------
# If reset = 1, the value will be reset to default reset_value on the
# next clock edge, no matter whether en = 1 or not

#-----------------------------------------------------------------------
# RegEnRst
#-----------------------------------------------------------------------
class RegEnRst( Model ):
  '''Register with enable and reset.

  When reset == 1 the register will be set to reset_value on the next
  clock edge, whether en == 1 or not.
  '''

  def __init__( s, dtype = 1, reset_value = 0 ):

    s.en  = InPort( 1 )
    s.in_ = InPort ( dtype )
    s.out = OutPort( dtype )

    @s.posedge_clk
    def seq_logic():
      if s.reset:
        s.out.next = reset_value
      elif s.en:
        s.out.next = s.in_

  def line_trace( s ):
    return "{} ({}) {}".format( s.in_, s.out, s.out )

