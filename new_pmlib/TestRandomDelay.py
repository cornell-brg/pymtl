#=========================================================================
# TestRandomDelay
#=========================================================================
# This class will insert random delays between and input val/rdy
# interface and an output val/rdy interface.
#

from new_pymtl    import *
from ValRdyBundle import InValRdyBundle, OutValRdyBundle

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

class TestRandomDelay( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits = 1, max_random_delay = 0 ):

    s.in_  = InValRdyBundle ( nbits )
    s.out  = OutValRdyBundle( nbits )

    # If the maximum random delay is set to zero, then the inputs are
    # directly connected to the outputs.

    s.max_random_delay = max_random_delay
    if max_random_delay == 0:
      s.connect( s.in_, s.out )

    # Buffer to hold message

    s.buf      = None
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

      in_go  = s.in_.val and s.in_.rdy
      out_go = s.out.val and s.out.rdy

      # If the output transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the input
      # transaction so we can essentially pipeline this control logic.

      if out_go:
        s.buf_full = False

      # If the input transaction occured, then write the input message into
      # our internal buffer, update the buffer full bit, and reset the
      # counter.

      if in_go:
        s.buf      = s.in_.msg[:]
        s.buf_full = True
        s.counter  = random.randint( 1, s.max_random_delay )

      if s.counter > 0:
        s.counter = s.counter - 1

      # The output message is always the output of the buffer

      if s.buf_full:
        s.out.msg.next = s.buf

      # The input is ready and the output is valid if counter is zero

      s.in_.rdy.next = ( s.counter == 0 ) and not s.buf_full
      s.out.val.next = ( s.counter == 0 ) and     s.buf_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    return "{} ({:2}) {}".format( s.in_, s.counter, s.out )

