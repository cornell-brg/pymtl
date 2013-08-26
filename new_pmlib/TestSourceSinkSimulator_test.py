#=========================================================================
# TestSourceSinkSimulator_test.py
#=========================================================================

from new_pymtl               import *
from ValRdyBundle            import InValRdyBundle, OutValRdyBundle
from TestSourceSinkSimulator import TestSourceSinkSimulator

import pytest

#-------------------------------------------------------------------------
# ValRdyBuffer
#-------------------------------------------------------------------------
# Simple example model for testing the TestSourceSinkSimulator.
#
class ValRdyBuffer( Model ):

  def __init__( s, MsgType ):

    s.in_ = InValRdyBundle( MsgType )
    s.out = InValRdyBundle( MsgType )

  def elaborate_logic( s ):

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
# test_TestSourceSinkSimulator
#-------------------------------------------------------------------------
# Test with various source and sink delays.
#
@pytest.mark.parametrize(
    ('src_delay', 'sink_delay'),
    [
      (0, 0),
      (3, 0),
      (0, 3),
      (3, 5),
    ]
)
def test_TestSourceSinkSimulator( dump_vcd, src_delay, sink_delay ):

  # Create some messages
  src_msgs = sink_msgs = range( 15 )

  # Instantiate the model
  model = ValRdyBuffer( 8 )

  # Create the simulator
  sim = TestSourceSinkSimulator( model, src_msgs,  sink_msgs, 
                                        src_delay, sink_delay )
  # Dump a vcd if enabled
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSourceSinkSimulator_test.vcd" )

  # Run the test
  sim.run_test()




