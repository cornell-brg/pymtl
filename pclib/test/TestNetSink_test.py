#=========================================================================
# TestNetSink_test.py
#=========================================================================

from pymtl        import *
from pclib.test   import TestSource, TestNetSink
from pclib.ifaces import InValRdyBundle, OutValRdyBundle, NetMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, msg_type, src_msgs, sink_msgs, src_delay, sink_delay ):

    s.msg_type   = msg_type
    s.src_msgs   = src_msgs
    s.sink_msgs  = sink_msgs
    s.src_delay  = src_delay
    s.sink_delay = sink_delay

  def elaborate_logic( s ):

    # Instantiate models

    s.src  = TestSource  ( s.msg_type, s.src_msgs,  s.src_delay  )
    s.sink = TestNetSink ( s.msg_type, s.sink_msgs, s.sink_delay )

    # Connect

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
# TestNetSink unit test - Inorder Messages
#-------------------------------------------------------------------------
def inorder_msgs():

  # Test messages

  test_msgs = [

      #       dest src seqnum payload
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

  return test_msgs

#-------------------------------------------------------------------------
# TestSimpleNetSink unit test - Out of Order Messages
#-------------------------------------------------------------------------
def outoforder_msgs():

  # Test messages

  src_msgs = [

      #       dest src seqnum payload
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

      #       dest src seqnum payload
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

  return [ src_msgs, sink_msgs ]


#-------------------------------------------------------------------------
# TestSimpleNetSink test runner
#-------------------------------------------------------------------------
def run_test( dump_vcd, vcd_filename, src_delay, sink_delay, src_msgs,
              sink_msgs ):

  # Instantiate and elaborate the model

  msg_type = NetMsg( 4, 16, 32 )
  model = TestHarness( msg_type, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_filename )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 0, sink_delay = 0
#-------------------------------------------------------------------------

def test_inorder_0x0( dump_vcd ):
  run_test( dump_vcd, get_vcd_filename(),
            0, 0, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 5, sink_delay = 0
#-------------------------------------------------------------------------

def test_inorder_5x0( dump_vcd ):
  run_test( dump_vcd, get_vcd_filename(),
            5, 0, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 0, sink_delay = 5
#-------------------------------------------------------------------------

def test_inorder_0x5( dump_vcd ):
  run_test( dump_vcd, get_vcd_filename(),
            0, 5, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 10, sink_delay = 5
#-------------------------------------------------------------------------

def test_inorder_10x5( dump_vcd ):
  run_test( dump_vcd, get_vcd_filename(),
            10, 5, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 0, sink_delay = 0
#-------------------------------------------------------------------------

def test_outoforder_0x0( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, get_vcd_filename(),
            0, 0, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 5, sink_delay = 0
#-------------------------------------------------------------------------

def test_outoforder_5x0( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, get_vcd_filename(),
            5, 0, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 0, sink_delay = 5
#-------------------------------------------------------------------------

def test_outoforder_0x5( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, get_vcd_filename(),
            0, 5, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 10, sink_delay = 5
#-------------------------------------------------------------------------

def test_outoforder_10x5( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, get_vcd_filename(),
            10, 5, test_msgs[0], test_msgs[1] )
