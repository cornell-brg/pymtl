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

class TestSink( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs, max_random_delay = 0 ):

    s.in_msg = InPort  ( nbits )
    s.in_val = InPort  ( 1     )
    s.in_rdy = OutPort ( 1     )
    s.done   = OutPort ( 1     )

    s.delay = TestRandomDelay( nbits, max_random_delay )
    s.sink  = TestSimpleSink( nbits, msgs )

  def elaborate_logic( s ):

    # Connect the input ports to the delay

    s.connect( s.in_msg, s.delay.in_msg )
    s.connect( s.in_val, s.delay.in_val )
    s.connect( s.in_rdy, s.delay.in_rdy )

    # Connect random delay to sink

    s.connect( s.delay.out_msg, s.sink.in_msg )
    s.connect( s.delay.out_val, s.sink.in_val )
    s.connect( s.delay.out_rdy, s.sink.in_rdy )

    # Connect test sink done signal to output port

    s.connect( s.sink.done, s.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.in_msg, s.in_val, s.in_rdy )

    return "{}".format( in_str )

