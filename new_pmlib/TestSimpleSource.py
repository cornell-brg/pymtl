#=========================================================================
# TestSimpleSource
#=========================================================================
# This class will output messages on a val/rdy interface from a
# predefined list.
#

from new_pymtl import *
import valrdy

class TestSimpleSource( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs ):

    s.out_msg = OutPort ( nbits )
    s.out_val = OutPort ( 1     )
    s.out_rdy = InPort  ( 1     )
    s.done    = OutPort ( 1     )

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
        s.out_msg.next = s.msgs[0]
        s.out_val.next = False
        s.done.next    = False
        return

      # Check if we have more messages to send.

      if ( s.idx == len(s.msgs) ):
        s.out_msg.next = s.msgs[0]
        s.out_val.next = False
        s.done.next    = True
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the output message transaction occured

      out_go = s.out_val and s.out_rdy

      # If the output transaction occured, then increment the index.

      if out_go:
        s.idx = s.idx + 1

      # The output message is always the indexed message in the list, or if
      # we are done then it is the first message again.

      if ( s.idx < len(s.msgs) ):
        s.out_msg.next = s.msgs[s.idx]
        s.out_val.next = True
        s.done.next    = False
      else:
        s.out_msg.next = s.msgs[0]
        s.out_val.next = False
        s.done.next    = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    out_str = valrdy.valrdy_to_str( s.out_msg, s.out_val, s.out_rdy )

    return "({:2}) {}" \
      .format( s.idx, out_str )

