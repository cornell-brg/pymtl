#=========================================================================
# TestSimpleNetSink Test Suite
#=========================================================================

from   pymtl import *
import pmlib

import net_msgs

from pmlib.TestSimpleSource import TestSimpleSource
from pmlib.TestSource       import TestSource
from TestNetSink            import TestSimpleNetSink
from TestNetSink            import TestNetSink

#-------------------------------------------------------------------------
# TestHarness for SimpleNetSink
#-------------------------------------------------------------------------

class TestHarness_SimpleNetSink (Model):

  def __init__( self, nbits, src_msgs, sink_msgs ):

    # Instantiate models

    self.src  = TestSimpleSource  ( nbits, src_msgs  )
    self.sink = TestSimpleNetSink ( nbits, sink_msgs )

    # Connect chain

    connect_chain([ self.src, self.sink ])

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " | " + self.sink.line_trace()

#-------------------------------------------------------------------------
# TestSimpleNetSink unit test - Inorder Messages
#-------------------------------------------------------------------------

def test_inorder_msgs( dump_vcd ):

  # Create parameters

  netmsg_params = net_msgs.NetMsgParams( 4, 16, 32 )

  # Test messages

  mk_msg = netmsg_params.mk_msg

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

  # Instantiate and elaborate the model

  model = TestHarness_SimpleNetSink( netmsg_params.nbits, test_msgs, test_msgs )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSimpleNetSink_test_inorder.vcd" )

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
# TestSimpleNetSink unit test - Out of Order Messages
#-------------------------------------------------------------------------

def test_outoforder_msgs( dump_vcd ):

  # Create parameters

  netmsg_params = net_msgs.NetMsgParams( 4, 16, 32 )

  # Test messages

  mk_msg = netmsg_params.mk_msg

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

  # Instantiate and elaborate the model

  model = TestHarness_SimpleNetSink( netmsg_params.nbits, src_msgs, sink_msgs )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSimpleNetSink_test_outoforder.vcd" )

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
# TestHarness for NetSink
#-------------------------------------------------------------------------

class TestHarness_NetSink (Model):

  def __init__( self, nbits, src_msgs, sink_msgs, src_delay, sink_delay ):

    # Instantiate models

    self.src  = TestSource  ( nbits, src_msgs,  src_delay  )
    self.sink = TestNetSink ( nbits, sink_msgs, sink_delay )

    # Connect chain

    connect_chain([ self.src, self.sink ])

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " | " + self.sink.line_trace()

#-------------------------------------------------------------------------
# TestNetSink unit tests
#-------------------------------------------------------------------------

# Create parameters

netmsg_params = net_msgs.NetMsgParams( 4, 16, 32 )

def inorder_msgs():

  # Test messages

  mk_msg = netmsg_params.mk_msg

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


def outoforder_msgs():

  # Test messages

  mk_msg = netmsg_params.mk_msg

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


def run_test( dump_vcd, vcd_filename, src_delay, sink_delay, src_msgs,
              sink_msgs ):

  # Instantiate and elaborate the model

  model = TestHarness_NetSink( netmsg_params.nbits, src_msgs, sink_msgs,
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
  run_test( dump_vcd, "pmlib-TestNetSink_inorder_delay0x0.vcd",
            0, 0, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 5, sink_delay = 0
#-------------------------------------------------------------------------

def test_inorder_5x0( dump_vcd ):
  run_test( dump_vcd, "pmlib-TestNetSink_inorder_delay5x0.vcd",
            5, 0, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 0, sink_delay = 5
#-------------------------------------------------------------------------

def test_inorder_0x5( dump_vcd ):
  run_test( dump_vcd, "pmlib-TestNetSink_inorder_delay0x5.vcd",
            0, 5, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Inorder unit test - src_delay = 10, sink_delay = 5
#-------------------------------------------------------------------------

def test_inorder_10x5( dump_vcd ):
  run_test( dump_vcd, "pmlib-TestNetSink_inorder_delay10x5.vcd",
            10, 5, inorder_msgs(), inorder_msgs() )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 0, sink_delay = 0
#-------------------------------------------------------------------------

def test_outoforder_0x0( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, "pmlib-TestNetSink_outoforder_delay0x0.vcd",
            0, 0, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 5, sink_delay = 0
#-------------------------------------------------------------------------

def test_outoforder_5x0( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, "pmlib-TestNetSink_outoforder_delay5x0.vcd",
            5, 0, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 0, sink_delay = 5
#-------------------------------------------------------------------------

def test_outoforder_0x5( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, "pmlib-TestNetSink_outoforder_delay0x5.vcd",
            0, 5, test_msgs[0], test_msgs[1] )

#-------------------------------------------------------------------------
# TestNetSink Out of Order unit test - src_delay = 10, sink_delay = 5
#-------------------------------------------------------------------------

def test_outoforder_10x5( dump_vcd ):
  test_msgs = outoforder_msgs()
  run_test( dump_vcd, "pmlib-TestNetSink_outoforder_delay10x5.vcd",
            10, 5, test_msgs[0], test_msgs[1] )
