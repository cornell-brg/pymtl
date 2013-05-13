#=========================================================================
# GcdUnit behavorial-level model
#=========================================================================

from new_pymtl import *
from new_pmlib import valrdy

import fractions

class GcdUnitBL( Model ):

  #-----------------------------------------------------------------------
  # Constructor: Define Interface
  #-----------------------------------------------------------------------

  def __init__( s ):

    s.in_msg  = InPort  ( 64 )
    s.in_val  = InPort  ( 1  )
    s.in_rdy  = OutPort ( 1  )

    s.out_msg = OutPort ( 32 )
    s.out_val = OutPort ( 1  )
    s.out_rdy = InPort  ( 1  )

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

    s.connect( s.in_rdy, s.out_rdy )

    #---------------------------------------------------------------------
    # Tick Logic
    #---------------------------------------------------------------------

    @s.tick
    def logic():

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input/output message transactions occured.

      in_go  = s.in_val.value  and s.in_rdy.value
      out_go = s.out_val.value and s.out_rdy.value

      # If the output transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the input
      # transaction so we can essentially pipeline this control logic.

      if out_go:
        s.buf_full = False

      # If the input transaction occured, then write the input message into
      # our internal buffer and update the buffer full bit

      if in_go:
        s.buf_a    = s.in_msg.value[ 0:32].uint()
        s.buf_b    = s.in_msg.value[32:64].uint()
        s.buf_full = True

      # The output message is always the gcd of the buffer

      s.out_msg.next = fractions.gcd( s.buf_a, s.buf_b )

      # The output message if valid if the buffer is full

      s.out_val.next = s.buf_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_msg = "{:8d} {:8d}".format( s.in_msg[ 0:32].uint(),
                                   s.in_msg[32:64].uint() )

    in_str = \
      valrdy.valrdy_to_str( in_msg, s.in_val, s.in_rdy )

    out_msg = "{:8d}".format( s.out_msg.uint() )

    out_str = \
      valrdy.valrdy_to_str( out_msg, s.out_val, s.out_rdy )

    return "{} () {}".format( in_str, out_str )

