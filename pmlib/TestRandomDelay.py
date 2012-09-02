#=========================================================================
# TestRandomDelay
#=========================================================================
# This class will insert random delays between and input val/rdy
# interface and an output val/rdy interface.
#

from pymtl import *
import valrdy
import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

class TestRandomDelay (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits = 1, max_random_delay = 0 ):

    self.in_msg  = InPort  ( nbits )
    self.in_val  = InPort  ( 1     )
    self.in_rdy  = OutPort ( 1     )

    self.out_msg = OutPort ( nbits )
    self.out_val = OutPort ( 1     )
    self.out_rdy = InPort  ( 1     )

    # If the maximum random delay is set to zero, then the inputs are
    # directly connected to the outputs.

    self.max_random_delay = max_random_delay
    if max_random_delay == 0:
      connect( self.in_msg, self.out_msg )
      connect( self.in_val, self.out_val )
      connect( self.in_rdy, self.out_rdy )

    self.buf      = 0
    self.buf_full = False
    self.counter  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # Ideally we could just not include this posedge_clk concurrent block
    # at all in the simulation. We should be able to do this when we have
    # an explicit elaborate function.

    if self.max_random_delay == 0:
      return

    # At the end of the cycle, we AND together the val/rdy bits to
    # determine if the input/output message transactions occured

    in_go  = self.in_val.value  and self.in_rdy.value
    out_go = self.out_val.value and self.out_rdy.value

    # If the output transaction occured, then clear the buffer full bit.
    # Note that we do this _first_ before we process the input
    # transaction so we can essentially pipeline this control logic.

    if out_go:
      self.buf_full = False

    # If the input transaction occured, then write the input message into
    # our internal buffer, update the buffer full bit, and reset the
    # counter

    if in_go:
      self.buf      = self.in_msg.value
      self.buf_full = True
      self.counter  = random.randint( 1, self.max_random_delay )

    if self.counter > 0:
      self.counter = self.counter - 1

    # The output message is always the output of the buffer

    self.out_msg.next = self.buf

    # The input is ready and the output is valid if counter is zero

    self.in_rdy.next  = ( self.counter == 0 ) and not self.buf_full
    self.out_val.next = ( self.counter == 0 ) and self.buf_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    out_str = \
      valrdy.valrdy_to_str( self.out_msg.value,
        self.out_val.value, self.out_rdy.value )

    return "{} ({:2}) {}" \
      .format( in_str, self.counter, out_str )

