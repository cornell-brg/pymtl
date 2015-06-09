#=========================================================================
# TestSink
#=========================================================================

from pymtl      import *
from pclib.test import TestRandomDelay
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from TestSimpleSink import TestSimpleSink

#-------------------------------------------------------------------------
# TestSink
#-------------------------------------------------------------------------
class TestSink( Model ):

  def __init__( s, dtype, msgs, max_random_delay = 0 ):

    s.in_  = InValRdyBundle( dtype )
    s.done = OutPort       ( 1     )

    # Instantiate modules

    s.delay = TestRandomDelay( dtype, max_random_delay )
    s.sink  = TestSimpleSink ( dtype, msgs )

    # Connect the input ports -> random delay -> sink

    s.connect( s.in_,       s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

    # Connect test sink done signal to output port

    s.connect( s.sink.done, s.done )

  def line_trace( s ):

    return "{}".format( s.in_ )

