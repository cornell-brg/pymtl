#=======================================================================
# TestRandomDelay
#=======================================================================

import random

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

#-----------------------------------------------------------------------
# TestRandomDelay
#-----------------------------------------------------------------------
class TestRandomDelay( Model ):
  'Inserts random delays between input and output val/rdy interfaces.'

  def __init__( s, dtype, max_random_delay = 0, seed=0xb601bc01 ):

    s.in_  = InValRdyBundle ( dtype )
    s.out  = OutValRdyBundle( dtype )

    # We keep our own internal random number generator to keep the state
    # of this generator completely separate from other generators. This
    # ensure that any delays are reproducable.

    s.rgen = random.Random()
    s.rgen.seed(seed)

    # If the maximum random delay is set to zero, then the inputs are
    # directly connected to the outputs.

    s.max_random_delay = max_random_delay
    if max_random_delay == 0:
      s.connect( s.in_, s.out )

    # Buffer to hold message

    s.buf      = None
    s.buf_full = False
    s.counter  = 0

    #---------------------------------------------------------------------
    # Tick
    #---------------------------------------------------------------------
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
        s.counter  = s.rgen.randint( 1, s.max_random_delay )

      if s.counter > 0:
        s.counter = s.counter - 1

      # The output message is always the output of the buffer

      if s.buf_full:
        s.out.msg.next = s.buf

      # The input is ready and the output is valid if counter is zero

      s.in_.rdy.next = ( s.counter == 0 ) and not s.buf_full
      s.out.val.next = ( s.counter == 0 ) and     s.buf_full

  def line_trace( s ):

    return "{} ({:2}) {}".format( s.in_, s.counter, s.out )

