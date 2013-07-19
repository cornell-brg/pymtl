#=========================================================================
# GcdUnit behavorial-level model
#=========================================================================

from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle

import fractions

#=========================================================================
# GCD Unit Behavioral-Level Model
#=========================================================================
class GcdUnitBL( Model ):

  #-----------------------------------------------------------------------
  # Constructor: Define Interface
  #-----------------------------------------------------------------------
  def __init__( s ):

    s.in_ = InValRdyBundle ( 64 )
    s.out = OutValRdyBundle( 32 )

    # Buffer to hold message

    s.buf_a    = 0
    s.buf_b    = 0
    s.buf_full = False

  #-----------------------------------------------------------------------
  # Elaborate: Define Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Structural Connectivity
    #---------------------------------------------------------------------
    # Connect ready signal to input to ensure pipeline behavior

    s.connect( s.in_.rdy, s.out.rdy )

    #---------------------------------------------------------------------
    # Tick Logic
    #---------------------------------------------------------------------

    @s.tick
    def logic():

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input/output message transactions occured.

      in_go  = s.in_.val  and s.in_.rdy
      out_go = s.out.val and s.out.rdy

      # If the output transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the input
      # transaction so we can essentially pipeline this control logic.

      if out_go:
        s.buf_full = False

      # If the input transaction occured, then write the input message into
      # our internal buffer and update the buffer full bit

      if in_go:
        s.buf_a    = s.in_.msg[ 0:32].uint()
        s.buf_b    = s.in_.msg[32:64].uint()
        s.buf_full = True

      # The output message is always the gcd of the buffer

      s.out.msg.next = fractions.gcd( s.buf_a, s.buf_b )

      # The output message if valid if the buffer is full

      s.out.val.next = s.buf_full

  #-----------------------------------------------------------------------
  # Line Tracing: Debug Output
  #-----------------------------------------------------------------------
  def line_trace( s ):

    return "{} () {}".format( s.in_, s.out)

