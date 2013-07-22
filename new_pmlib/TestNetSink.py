#=========================================================================
# TestNetSink.py
#=========================================================================

from new_pymtl         import *
from ValRdyBundle      import InValRdyBundle, OutValRdyBundle
from TestSimpleNetSink import TestSimpleNetSink
from TestRandomDelay   import TestRandomDelay

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
  def __init__( s, msg_type, msgs, max_random_delay = 0 ):

    s.in_  = InValRdyBundle( msg_type )
    s.done = OutPort       ( 1     )

    s.msg_type         = msg_type
    s.msgs             = msgs
    s.max_random_delay = max_random_delay

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.delay = TestRandomDelay  ( s.msg_type, s.max_random_delay )
    s.sink  = TestSimpleNetSink( s.msg_type, s.msgs             )

    s.connect( s.in_,       s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )
    s.connect( s.sink.done, s.done      )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):

    return "{}".format( s.in_ )


