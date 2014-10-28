#=========================================================================
# TestSimpleNetSink.py
#=========================================================================

from pymtl       import *
from ValRdyBundle    import InValRdyBundle, OutValRdyBundle

#-------------------------------------------------------------------------
# TestSimpleNetSink
#-------------------------------------------------------------------------
# This class will sink network messages from a val/rdy interface and
# compare them to a predefined list of network messages. Each network
# message has route information, unique sequence number and payload
# information
class TestSimpleNetSink( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, msg_type, msgs ):

    s.in_  = InValRdyBundle( msg_type )
    s.done = OutPort       ( 1        )

    s.msgs        = msgs
    s.recv        = []
    s.idx         = 0
    s.msgs_len    = len( msgs )

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    @s.tick
    def tick():

      # Handle reset

      if s.reset:
        s.in_.rdy.next = False
        s.done.next    = False
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input message transaction occured

      in_go = s.in_.val and s.in_.rdy

      # If the input transaction occured, verify that it is what we
      # expected, then increment the index.

      if in_go:

        # Check if the msg received was valid
        if s.in_.msg not in s.msgs:
          if s.in_.msg in s.recv:
            raise AssertionError( "Message {} arrived twice!"
                                  .format( s.in_.msg ) )
          else:
            raise AssertionError( "Message {} not found in Test Sink!"
                                  .format( s.in_.msg ) )

        # Update State
        s.msgs.remove( s.in_.msg )
        s.recv.append( s.in_.msg )
        s.idx = s.idx + 1

      # Set the ready and done signals.

      if ( s.idx < s.msgs_len ):
        s.in_.rdy.next = True
        s.done.next    = False
      else:
        s.in_.rdy.next = False
        s.done.next    = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    return "{} ({:2})".format( s.in_ , s.idx )

