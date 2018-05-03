#=========================================================================
# TestSynchronizer_test.py
#=========================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.test import TestSource, TestSink

from TestSynchronizer import TestSynchronizer, TestSynchInfo

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, dtype, msgs1, msgs2, synch_info, src_delay, sink_delay ):

    s.src1  = TestSource( dtype, msgs1, src_delay )
    s.src2  = TestSource( dtype, msgs2, src_delay )
    s.synch1 = TestSynchronizer( dtype, 0, synch_info )
    s.synch2 = TestSynchronizer( dtype, 1, synch_info )
    s.sink1 = TestSink( dtype, msgs1, sink_delay )
    s.sink2 = TestSink( dtype, msgs2, sink_delay )

    s.synch_info = synch_info
    s.synch_idx = 0
    s.expected_num_msgs = [ i for i, _ in synch_info.synch_table[0] ][ : -1 ]

    s.connect( s.src1.out, s.synch1.in_ )
    s.connect( s.synch1.out, s.sink1.in_ )
    s.connect( s.src2.out, s.synch2.in_ )
    s.connect( s.synch2.out, s.sink2.in_ )

  def check( s ):
    """ Ensure the synchronization is respected by checking how many
    messages the sinks received. """
    assert s.sink1.sink.idx <= s.expected_num_msgs[0]
    assert s.sink2.sink.idx <= s.expected_num_msgs[1]

    if s.sink1.sink.idx == s.expected_num_msgs[0] and \
       s.sink2.sink.idx == s.expected_num_msgs[1]:

      # Once we receive enough messages, mimic the fake synchronizer (idx
      # 2) to have sent its token.
      s.synch_info.token_sent( 2 )

      s.synch_idx += 1
      if s.synch_idx < len( s.synch_info.synch_table ):
        s.expected_num_msgs[0] += s.synch_info.synch_table[ s.synch_idx ][0][0]
        s.expected_num_msgs[1] += s.synch_info.synch_table[ s.synch_idx ][1][0]
      else:
        # The end of the synch table, so set a large number of expected
        # messages.
        s.expected_num_msgs[0] = 10000
        s.expected_num_msgs[1] = 10000

  def done( s ):
    return s.src1.done and s.src2.done and s.sink1.done and s.sink2.done

  def line_trace( s ):
    return s.src1.line_trace() + " > " + s.sink1.line_trace() + " | " + \
           s.src2.line_trace() + " > " + s.sink2.line_trace() + " | " + \
           s.synch_info.line_trace()

#-------------------------------------------------------------------------
# do_test
#-------------------------------------------------------------------------
def do_test( dump_vcd, src_delay, sink_delay ):

  # Test messages

  test_msgs1 = [
    0x0000,
    0x0a0a,
    0x0b0b,
    # synch 0
    0x0c0c,
    0x0d0d,
    # synch 1
    # synch 2
    0xf0f0,
    0xe0e0,
    0xd0d0,
    0x1441,
    0x2255,
    0x1d01,
    0xf0f1,
    # synch 3
    0xe011,
    0xd022,
  ]

  test_msgs2 = [
    0x1234,
    0x1122,
    0xaabb,
    0x00aa,
    0x1a1a,
    0x21aa,
    # synch 0
    # synch 1
    0x0001,
    0x1111,
    0x4444,
    0x1050,
    # synch 2
    0x1100,
    0x0099,
    # synch 3
    0x1094,
    0x1859,
    0x1859,
    0x1953,
    0x1551,
    0x3355,
  ]

  # Note that we're using a fake synchronizer at index 2 for testing with
  # a single token. The test harness will use this to ensure number of
  # messages that went through is what we expect.

  synch_table = [ [ [3,0], [6,0], [1,0], ],
                  [ [2,0], [0,0], [1,0], ],
                  [ [0,0], [4,0], [1,0], ], ]

  synch_info = TestSynchInfo( synch_table )

  # Instantiate and elaborate the model

  model = TestHarness( 16, test_msgs1, test_msgs2, synch_info,
                       src_delay, sink_delay )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    model.check()
    sim.cycle()

  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

@pytest.mark.parametrize( 'src_delay,sink_delay', [
  ( 0, 0 ),
  ( 1, 1 ),
  ( 1, 0 ),
  ( 5, 1 ),
  ( 0, 1 ),
  ( 1, 5 ),
  ( 10, 10 ),
])
def test_TestSource( dump_vcd, src_delay, sink_delay ):
  do_test( dump_vcd, src_delay, sink_delay )

