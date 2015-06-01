#=========================================================================
# TestSrcSinkSim_test.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test   import TestSrcSinkSim

#-------------------------------------------------------------------------
# ValRdyBuffer
#-------------------------------------------------------------------------
# Simple example model for testing the TestSrcSinkSim.
class ValRdyBuffer( Model ):

  def __init__( s, MsgType ):

    s.in_ = InValRdyBundle( MsgType )
    s.out = InValRdyBundle( MsgType )

    s.data = None

    @s.tick
    def logic():

      if s.out.val and s.out.rdy:
        s.data = None

      if s.in_.val and s.in_.rdy:
        if s.data == None:
          s.data = s.in_.msg[:]

      if s.data != None:
        s.out.msg.next = s.data
      s.out.val.next = s.data != None
      s.in_.rdy.next = s.data == None

#-------------------------------------------------------------------------
# test_TestSrcSinkSim
#-------------------------------------------------------------------------
# Test with various source and sink delays.
#
@pytest.mark.parametrize( ('src_delay', 'sink_delay'), [
  (0, 0),
  (3, 0),
  (0, 3),
  (3, 5),
])
def test_TestSrcSinkSim( dump_vcd, src_delay, sink_delay ):

  # Create some messages
  src_msgs = sink_msgs = range( 15 )

  # Instantiate the model
  model = ValRdyBuffer( 8 )

  # Dump a vcd if enabled
  model.vcd_file = dump_vcd

  # Create the simulator
  sim = TestSrcSinkSim( model, src_msgs,  sink_msgs,
                               src_delay, sink_delay )

  # Run the test
  sim.run_test()




