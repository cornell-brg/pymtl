#=========================================================================
# TestSimpleSource
#=========================================================================
# This class will output messages on a val/rdy interface from a
# predefined list.
#

from pymtl        import *
from pclib.ifaces import OutValRdyBundle

class TestSimpleSource( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs ):

    s.out  = OutValRdyBundle( nbits )
    s.done = OutPort        ( 1     )

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
        if s.msgs:
          s.out.msg.next = s.msgs[0]
        s.out.val.next = False
        s.done.next    = False
        return

      # Check if we have more messages to send.

      if ( s.idx == len(s.msgs) ):
        if s.msgs:
          s.out.msg.next = s.msgs[0]
        s.out.val.next = False
        s.done.next    = True
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the output message transaction occured

      out_go = s.out.val and s.out.rdy

      # If the output transaction occured, then increment the index.

      if out_go:
        s.idx = s.idx + 1

      # The output message is always the indexed message in the list, or if
      # we are done then it is the first message again.

      if ( s.idx < len(s.msgs) ):
        s.out.msg.next = s.msgs[s.idx]
        s.out.val.next = True
        s.done.next    = False
      else:
        s.out.msg.next = s.msgs[0]
        s.out.val.next = False
        s.done.next    = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    return "({:2}) {}".format( s.idx, s.out )

