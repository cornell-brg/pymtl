#=========================================================================
# TestSimpleSink
#=========================================================================
# This class will sink messages from a val/rdy interface and compare them
# to a predefined list.
#

from pymtl      import *
from pclib.ifcs import InValRdyBundle

class TestSimpleSink( Model ):

  def __init__( s, nbits, msgs ):

    s.in_  = InValRdyBundle( nbits )
    s.done = OutPort       ( 1     )

    s.msgs = msgs
    s.idx  = 0

    @s.tick
    def tick():

      # Handle reset

      if s.reset:
        s.in_.rdy.next = False
        s.done   .next = False
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input message transaction occured

      in_go = s.in_.val and s.in_.rdy

      # If the input transaction occured, verify that it is what we
      # expected. then increment the index.

      if in_go:
        assert s.in_.msg == s.msgs[s.idx]
        s.idx = s.idx + 1

      # Set the ready and done signals.

      if ( s.idx < len(s.msgs) ):
        s.in_.rdy.next = True
        s.done   .next = False
      else:
        s.in_.rdy.next = False
        s.done   .next = True


  def line_trace( s ):

    return "{} ({:2})".format( s.in_, s.idx )

