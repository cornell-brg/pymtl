#=========================================================================
# TestSimpleSink
#=========================================================================
# This class will sink messages from a val/rdy interface and compare them
# to a predefined list.
#

from pymtl import *
import valrdy

class TestSimpleSink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs ):

    self.in_msg = InPort  ( nbits )
    self.in_val = InPort  ( 1     )
    self.in_rdy = OutPort ( 1     )
    self.done   = OutPort ( 1     )

    self.msgs = msgs
    self.idx  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # Handle reset

    if self.reset.value:
      self.in_rdy.next = False
      self.done.next   = False
      return

    # At the end of the cycle, we AND together the val/rdy bits to
    # determine if the input message transaction occured

    in_go = self.in_val.value and self.in_rdy.value

    # If the input transaction occured, verify that it is what we
    # expected. then increment the index.

    if in_go:
      assert self.in_msg.value == self.msgs[self.idx]
      self.idx = self.idx + 1

    # Set the ready and done signals.

    if ( self.idx < len(self.msgs) ):
      self.in_rdy.next = True
      self.done.next   = False
    else:
      self.in_rdy.next = False
      self.done.next   = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    return "{} ({:2})" \
      .format( in_str, self.idx )

