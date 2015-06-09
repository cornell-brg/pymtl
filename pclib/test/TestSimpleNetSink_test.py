#=========================================================================
# TestSimpleNetSink_test.py
#=========================================================================

from __future__ import print_function

import pytest

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle, NetMsg

from TestSimpleSource  import TestSimpleSource
from TestSimpleNetSink import TestSimpleNetSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, dtype, src_msgs, sink_msgs ):

    s.src  = TestSimpleSource ( dtype, src_msgs  )
    s.sink = TestSimpleNetSink( dtype, sink_msgs )

    s.connect( s.src.out,  s.sink.in_  )
    s.connect( s.src.done, s.sink.done )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " | " + s.sink.line_trace()

#-------------------------------------------------------------------------
# Message Creator
#-------------------------------------------------------------------------
def mk_msg( src, dest, seqnum, payload ):
  msg         = NetMsg( 4, 16, 32 )
  msg.src     = src
  msg.dest    = dest
  msg.seqnum  = seqnum
  msg.payload = payload
  return msg

#-------------------------------------------------------------------------
# TestSimpleNetSink test runner
#-------------------------------------------------------------------------
def run_test( dump_vcd, src_msgs, sink_msgs ):

  # Instantiate and elaborate the model

  dtype = NetMsg( 4, 16, 32 )
  model = TestHarness( dtype, src_msgs, sink_msgs )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestSimpleNetSink unit test - Inorder Messages
#-------------------------------------------------------------------------
def test_inorder_msgs( dump_vcd ):
  src_msgs = [
            # dest src seqnum payload
      mk_msg( 1,   0,  0,     0x00000100 ),
      mk_msg( 1,   0,  1,     0x00000101 ),
      mk_msg( 1,   0,  2,     0x00000102 ),
      mk_msg( 1,   0,  3,     0x00000103 ),
      mk_msg( 2,   1,  0,     0x00000210 ),
      mk_msg( 2,   1,  1,     0x00000211 ),
      mk_msg( 2,   1,  2,     0x00000212 ),
      mk_msg( 2,   1,  3,     0x00000213 ),
      mk_msg( 3,   2,  0,     0x00000320 ),
      mk_msg( 3,   2,  1,     0x00000321 ),
      mk_msg( 3,   2,  2,     0x00000322 ),
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 0,   3,  0,     0x00000030 ),
      mk_msg( 0,   3,  1,     0x00000031 ),
      mk_msg( 0,   3,  2,     0x00000032 ),
      mk_msg( 0,   3,  3,     0x00000033 ),
  ]

  sink_msgs = src_msgs[:]

  run_test( dump_vcd, src_msgs, sink_msgs )

#-------------------------------------------------------------------------
# TestSimpleNetSink unit test - Out of Order Messages
#-------------------------------------------------------------------------
def test_outoforder_msgs( dump_vcd ):

  # Create test vectors

  src_msgs = [

            # dest src seqnum payload
      mk_msg( 1,   0,  3,     0x00000103 ),
      mk_msg( 1,   0,  1,     0x00000101 ),
      mk_msg( 2,   1,  1,     0x00000211 ),
      mk_msg( 1,   0,  2,     0x00000102 ),
      mk_msg( 2,   1,  0,     0x00000210 ),
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 2,   1,  2,     0x00000212 ),
      mk_msg( 3,   2,  1,     0x00000321 ),
      mk_msg( 0,   3,  2,     0x00000032 ),
      mk_msg( 3,   2,  2,     0x00000322 ),
      mk_msg( 0,   3,  0,     0x00000030 ),
      mk_msg( 3,   2,  0,     0x00000320 ),
      mk_msg( 0,   3,  1,     0x00000031 ),
      mk_msg( 2,   1,  3,     0x00000213 ),
      mk_msg( 0,   3,  3,     0x00000033 ),
      mk_msg( 1,   0,  0,     0x00000100 ),
  ]

  sink_msgs = [

            # dest src seqnum payload
      mk_msg( 1,   0,  0,     0x00000100 ),
      mk_msg( 1,   0,  1,     0x00000101 ),
      mk_msg( 1,   0,  2,     0x00000102 ),
      mk_msg( 1,   0,  3,     0x00000103 ),
      mk_msg( 2,   1,  0,     0x00000210 ),
      mk_msg( 2,   1,  1,     0x00000211 ),
      mk_msg( 2,   1,  2,     0x00000212 ),
      mk_msg( 2,   1,  3,     0x00000213 ),
      mk_msg( 3,   2,  0,     0x00000320 ),
      mk_msg( 3,   2,  1,     0x00000321 ),
      mk_msg( 3,   2,  2,     0x00000322 ),
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 0,   3,  0,     0x00000030 ),
      mk_msg( 0,   3,  1,     0x00000031 ),
      mk_msg( 0,   3,  2,     0x00000032 ),
      mk_msg( 0,   3,  3,     0x00000033 ),
  ]

  run_test( dump_vcd, src_msgs, sink_msgs )

#-------------------------------------------------------------------------
# TestSimpleNetSink unit test - Redundant Messages
#-------------------------------------------------------------------------
def test_redundant_msgs( dump_vcd ):

  src_msgs = [
            # dest src seqnum payload
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 2,   1,  2,     0x00000212 ),
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 0,   3,  2,     0x00000032 ),
  ]

  sink_msgs = [
            # dest src seqnum payload
      mk_msg( 3,   2,  3,     0x00000323 ),
      mk_msg( 2,   1,  2,     0x00000212 ),
      mk_msg( 3,   2,  1,     0x00000321 ),
      mk_msg( 0,   3,  2,     0x00000032 ),
  ]

  with pytest.raises( AssertionError ):
    run_test( dump_vcd, src_msgs, sink_msgs )

