#=========================================================================
# GcdUnit behavorial-level model
#=========================================================================

from pymtl import *
import pmlib
import fractions

class GcdUnitBL (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self ):

    self.in_msg  = InPort  ( 64 )
    self.in_val  = InPort  ( 1  )
    self.in_rdy  = OutPort ( 1  )

    self.out_msg = OutPort ( 32 )
    self.out_val = OutPort ( 1  )
    self.out_rdy = InPort  ( 1  )

    # Buffer to hold message

    self.buf_a    = 0
    self.buf_b    = 0
    self.buf_full = False

    # Connect ready signal to input to ensure pipeline behavior

    connect( self.in_rdy, self.out_rdy )

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @tick
  def logic( self ):

    # At the end of the cycle, we AND together the val/rdy bits to
    # determine if the input/output message transactions occured.

    in_go  = self.in_val.value  and self.in_rdy.value
    out_go = self.out_val.value and self.out_rdy.value

    # If the output transaction occured, then clear the buffer full bit.
    # Note that we do this _first_ before we process the input
    # transaction so we can essentially pipeline this control logic.

    if out_go:
      self.buf_full = False

    # If the input transaction occured, then write the input message into
    # our internal buffer and update the buffer full bit

    if in_go:
      self.buf_a    = self.in_msg.value[ 0:32].uint
      self.buf_b    = self.in_msg.value[32:64].uint
      self.buf_full = True

    # The output message is always the gcd of the buffer

    self.out_msg.next = fractions.gcd( self.buf_a, self.buf_b )

    # The output message if valid if the buffer is full

    self.out_val.next = self.buf_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    out_str = \
      pmlib.valrdy.valrdy_to_str( self.out_msg.value,
        self.out_val.value, self.out_rdy.value )

    return "{} () {}".format( in_str, out_str )

