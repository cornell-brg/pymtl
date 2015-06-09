#=========================================================================
# TestNetSink.py
#=========================================================================

from pymtl        import *
from pclib.test   import TestRandomDelay
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from TestSimpleNetSink import TestSimpleNetSink

#-------------------------------------------------------------------------
# TestNetSink
#-------------------------------------------------------------------------
# This class will sink network messages from a val/rdy interface and
# compare them to a predefined list of network messages. Each network
# message has route information, unique sequence number and payload
# information
class TestNetSink( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, dtype, msgs, max_random_delay = 0 ):

    s.in_  = InValRdyBundle( dtype )
    s.done = OutPort       ( 1          )

    s.delay = TestRandomDelay  ( dtype, max_random_delay )
    s.sink  = TestSimpleNetSink( dtype, msgs             )

    s.connect( s.in_,       s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )
    s.connect( s.sink.done, s.done      )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    return "{}".format( s.in_ )


