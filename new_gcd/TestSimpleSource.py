#=========================================================================
# TestSimpleSource
#=========================================================================
# This class will output messages on a val/rdy interface from a
# predefined list.
#

from new_pymtl import *
import valrdy

class TestSimpleSource (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs ):

    self.out_msg = OutPort ( nbits )
    self.out_val = OutPort ( 1     )
    self.out_rdy = InPort  ( 1     )
    self.done    = OutPort ( 1     )

    self.msgs = msgs
    self.idx  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  def elaborate_logic( self ):
    @self.tick
    def tick():

      # Handle reset

      if self.reset.value:
        self.out_msg.next = self.msgs[0]
        self.out_val.next = False
        self.done.next    = False
        return

      # Check if we have more messages to send.

      if ( self.idx == len(self.msgs) ):
        self.out_msg.next = self.msgs[0]
        self.out_val.next = False
        self.done.next    = True
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the output message transaction occured

      out_go = self.out_val.value and self.out_rdy.value

      # If the output transaction occured, then increment the index.

      if out_go:
        self.idx = self.idx + 1

      # The output message is always the indexed message in the list, or if
      # we are done then it is the first message again.

      if ( self.idx < len(self.msgs) ):
        self.out_msg.next = self.msgs[self.idx]
        self.out_val.next = True
        self.done.next    = False
      else:
        self.out_msg.next = self.msgs[0]
        self.out_val.next = False
        self.done.next    = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    out_str = \
      valrdy.valrdy_to_str( self.out_msg.value,
        self.out_val.value, self.out_rdy.value )

    return "({:2}) {}" \
      .format( self.idx, out_str )

