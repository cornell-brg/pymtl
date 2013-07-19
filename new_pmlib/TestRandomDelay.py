#=========================================================================
# TestRandomDelay
#=========================================================================
# This class will insert random delays between and input val/rdy
# interface and an output val/rdy interface.
#

from new_pymtl import *
import valrdy
import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

class TestRandomDelay( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits = 1, max_random_delay = 0 ):

    s.in_msg  = InPort  ( nbits )
    s.in_val  = InPort  ( 1     )
    s.in_rdy  = OutPort ( 1     )

    s.out_msg = OutPort ( nbits )
    s.out_val = OutPort ( 1     )
    s.out_rdy = InPort  ( 1     )

    # If the maximum random delay is set to zero, then the inputs are
    # directly connected to the outputs.

    s.max_random_delay = max_random_delay
    if max_random_delay == 0:
      s.connect( s.in_msg, s.out_msg )
      s.connect( s.in_val, s.out_val )
      s.connect( s.in_rdy, s.out_rdy )

    # Buffer to hold message

    s.buf      = 0
    s.buf_full = False
    s.counter  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):
    @s.tick
    def tick():

      # Ideally we could just not include this posedge_clk concurrent block
      # at all in the simulation. We should be able to do this when we have
      # an explicit elaborate function.

      if s.max_random_delay == 0:
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input/output message transactions occured.

      in_go  = s.in_val  and s.in_rdy
      out_go = s.out_val and s.out_rdy

      # If the output transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the input
      # transaction so we can essentially pipeline this control logic.

      if out_go:
        s.buf_full = False

      # If the input transaction occured, then write the input message into
      # our internal buffer, update the buffer full bit, and reset the
      # counter.

      if in_go:
        s.buf      = s.in_msg[:]
        s.buf_full = True
        s.counter  = random.randint( 1, s.max_random_delay )

      if s.counter > 0:
        s.counter = s.counter - 1

      # The output message is always the output of the buffer

      s.out_msg.next = s.buf

      # The input is ready and the output is valid if counter is zero

      s.in_rdy.next  = ( s.counter == 0 ) and not s.buf_full
      s.out_val.next = ( s.counter == 0 ) and s.buf_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.in_msg, s.in_val, s.in_rdy )

    out_str = \
      valrdy.valrdy_to_str( s.out_msg, s.out_val, s.out_rdy )

    return "{} ({:2}) {}" \
      .format( in_str, s.counter, out_str )

