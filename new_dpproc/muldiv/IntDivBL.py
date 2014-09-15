#=========================================================================
# IntDiv behavorial-level model
#=========================================================================

# Python division when the result is expected to be negative, rounds it
# towards negative infinity as opposed to positive infinity. We use the
# division operator and cast it to an integer to get the right behavior.

#from   __future__ import division

from   new_pymtl      import *

from new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle
import new_pmlib
from   muldiv_msg import BitStructIndex

class IntDivBL (Model):

  # Constants

  idx= BitStructIndex()

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s ):

    s.in_ = InValRdyBundle( s.idx.length )
    s.out = OutValRdyBundle( 32 )

  def elaborate_logic( s ):

    # Buffer to hold message

    s.buf_a    = 0
    s.buf_b    = 0
    s.buf_full = False
    # Connect ready signal to input to ensure pipeline behavior

    s.connect( s.in_.rdy, s.out.rdy )

    #-----------------------------------------------------------------------
    # Tick
    #-----------------------------------------------------------------------

    @s.tick
    def logic():

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input/output message transactions occured.

      in_go  = s.in_.val and s.in_.rdy
      out_go = s.out.val and s.out.rdy

      # If the output transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the input
      # transaction so we can essentially pipeline this control logic.

      if out_go:
        s.buf_full = False

      # If the input transaction occured, then write the input message into
      # our internal buffer and update the buffer full bit

      if in_go:
        s.buf_full = True
        s.in_op    = s.in_.msg[s.idx.muldiv_op].uint()

        if   s.in_op == s.idx.DIV_OP or s.in_op == s.idx.REM_OP:
          s.buf_a    = s.in_.msg[s.idx.arg_A].int()
          s.buf_b    = s.in_.msg[s.idx.arg_B].int()
        elif s.in_op == s.idx.DIVU_OP or s.in_op == s.idx.REMU_OP:
          s.buf_a    = s.in_.msg[s.idx.arg_A].uint()
          s.buf_b    = s.in_.msg[s.idx.arg_B].uint()


      # The output message is always the division of the operands
      # stored in the buffer

      if (s.buf_b != 0):
        if ( s.in_op == s.idx.DIV_OP or s.in_op == s.idx.DIVU_OP ):
          if (   ( s.buf_a < 0 and s.buf_b < 0 )
              or ( s.buf_a > 0 and s.buf_b > 0 ) ):
            result= int(s.buf_a / s.buf_b)
            s.out.msg.next = Bits( 32, result, trunc=True )
          else:
            result= int(- ( abs( s.buf_a ) / abs( s.buf_b )))
            s.out.msg.next = Bits( 32,  result, trunc=True)
        else:
          if (   ( s.buf_a < 0 and s.buf_b < 0 )
              or ( s.buf_a > 0 and s.buf_b > 0 ) ):
            s.out.msg.next = Bits( 32, s.buf_a % s.buf_b, trunc=True )
          elif( s.buf_a < 0 and s.buf_b > 0 ):
            result = - ( abs( s.buf_a ) % abs( s.buf_b ) )
            s.out.msg.next = Bits( 32, result, trunc=True )
          else:
            result = ( abs( s.buf_a ) % abs( s.buf_b ) )
            s.out.msg.next = Bits( 32, result, trunc=True )
      else:
        s.out.msg.next   = Bits( 32, 0)

      # The output message if valid if the buffer is full

      s.out.val.next = s.buf_full
      #s.in_.rdy.next=  (s.buf_full == False)

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      new_pmlib.valrdy.valrdy_to_str( s.in_.msg.value,
        s.in_.val.value, s.in_.rdy.value )

    out_str = \
      new_pmlib.valrdy.valrdy_to_str( s.out.msg.value,
        s.out.val.value, s.out.rdy.value )

    return "{} ({} {}) {}" \
        .format( in_str, Bits(32,s.buf_a,trunc=True),
                 Bits(32,s.buf_b,trunc=True), out_str )

