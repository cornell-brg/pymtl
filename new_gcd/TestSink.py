#=========================================================================
# TestSink
#=========================================================================
# This class will sink messages from a val/rdy interface and compare them
# to a predefined list. Includes support for random delays.
#

from new_pymtl import *
import valrdy

from TestSimpleSink   import TestSimpleSink
from TestRandomDelay  import TestRandomDelay

class TestSink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs, max_random_delay = 0 ):

    self.in_msg = InPort  ( nbits )
    self.in_val = InPort  ( 1     )
    self.in_rdy = OutPort ( 1     )
    self.done   = OutPort ( 1     )

    self.delay = TestRandomDelay( nbits, max_random_delay )
    self.sink  = TestSimpleSink( nbits, msgs )

  def elaborate_logic( self ):

    # Connect the input ports to the delay

    self.connect( self.in_msg, self.delay.in_msg )
    self.connect( self.in_val, self.delay.in_val )
    self.connect( self.in_rdy, self.delay.in_rdy )

    # Connect random delay to sink

    self.connect( self.delay.out_msg, self.sink.in_msg )
    self.connect( self.delay.out_val, self.sink.in_val )
    self.connect( self.delay.out_rdy, self.sink.in_rdy )

    # Connect test sink done signal to output port

    self.connect( self.sink.done, self.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    return "{}".format( in_str )

