#=========================================================================
# TestSink
#=========================================================================
# This class will sink messages from a val/rdy interface and compare them
# to a predefined list. Includes support for random delays.
#

from new_pymtl        import *
from ValRdyBundle     import InValRdyBundle
from TestSimpleSink   import TestSimpleSink
from TestRandomDelay  import TestRandomDelay

class TestSink( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs, max_random_delay = 0 ):

    s.in_  = InValRdyBundle( nbits )
    s.done = OutPort       ( 1     )

    s.nbits            = nbits
    s.msgs             = msgs
    s.max_random_delay = max_random_delay

  def elaborate_logic( s ):

    # Instantiate modules

    s.delay = TestRandomDelay( s.nbits, s.max_random_delay )
    s.sink  = TestSimpleSink ( s.nbits, s.msgs )

    # Connect the input ports -> random delay -> sink

    s.connect( s.in_,       s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

    # Connect test sink done signal to output port

    s.connect( s.sink.done, s.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    return "{}".format( s.in_ )

