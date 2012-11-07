#=========================================================================
# TestSimpleNetSink
#=========================================================================
# This class will sink network messages from a val/rdy interface and
# compare them to a predefined list of network messages. Each network
# message has route information, unique sequence number and payload
# information

from   pymtl import *
import pmlib

from   pmlib    import valrdy
import net_msgs

class TestSimpleNetSink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs ):

    self.in_msg      = InPort  ( nbits )
    self.in_val      = InPort  ( 1     )
    self.in_rdy      = OutPort ( 1     )
    self.done        = OutPort ( 1     )

    self.msgs        = msgs
    self.idx         = 0
    self.msgs_len    = len( msgs )
    print self.msgs_len

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
    # expected, then increment the index.

    if in_go:
      assert self.in_msg.value in self.msgs
      self.idx = self.idx + 1

    # Set the ready and done signals.

    if ( self.idx < self.msgs_len ):
      self.in_rdy.next = True
      self.done.next   = False
    else:
      print "DONE"
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

#=========================================================================
# TestNetSink
#=========================================================================
# This class will sink network messages from a val/rdy interface and
# compare them to a predefined list of network messages. Each network
# message has route information, unique sequence number and payload
# information

from pmlib.TestRandomDelay import TestRandomDelay

class TestNetSink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs, max_random_delay = 0 ):

    self.in_msg = InPort  ( nbits )
    self.in_val = InPort  ( 1     )
    self.in_rdy = OutPort ( 1     )
    self.done   = OutPort ( 1     )

    self.delay = TestRandomDelay( nbits, max_random_delay )
    self.sink  = TestSimpleNetSink( nbits, msgs )

    # Connect the input ports to the delay

    connect( self.in_msg, self.delay.in_msg )
    connect( self.in_val, self.delay.in_val )
    connect( self.in_rdy, self.delay.in_rdy )

    # Connect random delay to sink

    connect( self.delay.out_msg, self.sink.in_msg )
    connect( self.delay.out_val, self.sink.in_val )
    connect( self.delay.out_rdy, self.sink.in_rdy )

    # Connect test sink done signal to output port

    connect( self.sink.done, self.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    return "{}".format( in_str )

