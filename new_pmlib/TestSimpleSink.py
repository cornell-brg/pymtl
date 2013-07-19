#=========================================================================
# TestSimpleSink
#=========================================================================
# This class will sink messages from a val/rdy interface and compare them
# to a predefined list.
#

from new_pymtl import *
import valrdy

class TestSimpleSink( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs ):

    s.in_msg = InPort  ( nbits )
    s.in_val = InPort  ( 1     )
    s.in_rdy = OutPort ( 1     )
    s.done   = OutPort ( 1     )

    s.msgs = msgs
    s.idx  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    @s.tick
    def tick():

      # Handle reset

      if s.reset:
        s.in_rdy.next = False
        s.done.next   = False
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input message transaction occured

      in_go = s.in_val and s.in_rdy

      # If the input transaction occured, verify that it is what we
      # expected. then increment the index.

      if in_go:
        assert s.in_msg == s.msgs[s.idx]
        s.idx = s.idx + 1

      # Set the ready and done signals.

      if ( s.idx < len(s.msgs) ):
        s.in_rdy.next = True
        s.done.next   = False
      else:
        s.in_rdy.next = False
        s.done.next   = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = valrdy.valrdy_to_str( s.in_msg, s.in_val, s.in_rdy )

    return "{} ({:2})" \
      .format( in_str, s.idx )

