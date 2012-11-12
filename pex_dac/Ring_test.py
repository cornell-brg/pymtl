#=========================================================================
# Ring Unit Test
#=========================================================================

from   pymtl import *
import pmlib

import pmlib.valrdy     as valrdy

from Ring import Ring
from pmlib.net_msgs import NetMsgParams

from pmlib.TestSource  import TestSource
from pmlib.TestNetSink import TestNetSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay,
                num_routers, num_messages, payload_nbits,
                num_entries ):

    # Local Constants

    s.num_routers = num_routers
    netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

    # Instantiate Models

    s.src    = [ TestSource  ( netmsg_params.nbits, src_msgs[x], src_delay   )
                 for x in xrange( s.num_routers ) ]
    s.ring = Ring( num_routers, num_messages, payload_nbits, num_entries )
    s.sink   = [ TestNetSink ( netmsg_params.nbits, sink_msgs[x], sink_delay )
                 for x in xrange( s.num_routers ) ]

    # connect

    for i in xrange( s.num_routers ):

      connect( s.ring.in_msg[i], s.src[i].out_msg )
      connect( s.ring.in_val[i], s.src[i].out_val )
      connect( s.ring.in_rdy[i], s.src[i].out_rdy )

      connect( s.ring.out_msg[i], s.sink[i].in_msg )
      connect( s.ring.out_val[i], s.sink[i].in_val )
      connect( s.ring.out_rdy[i], s.sink[i].in_rdy )

  def done( s ):
    done_flag = 1
    for i in xrange( 8 ):
      done_flag &= s.src[i].done.value.uint and s.sink[i].done.value.uint
    return done_flag

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_net_test( dump_vcd, vcd_file_name, src_delay, sink_delay,
                  test_msgs, num_routers, num_messages, payload_nbits,
                  num_entries ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( src_msgs, sink_msgs, src_delay, sink_delay,
                       num_routers, num_messages, payload_nbits, num_entries )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.num_cycles < 100:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test Messages
#-------------------------------------------------------------------------

num_routers   = 8
num_messages  = 128
payload_nbits = 32

netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

def terminal_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  mk_net_msg( 0,   0,  0,       0xaaaaaaaa )
  mk_net_msg( 1,   1,  0,       0xbbbbbbbb )
  mk_net_msg( 2,   2,  0,       0xcccccccc )
  mk_net_msg( 3,   3,  0,       0xdddddddd )
  mk_net_msg( 4,   4,  0,       0xeeeeeeee )
  mk_net_msg( 5,   5,  0,       0xffffffff )
  mk_net_msg( 6,   6,  0,       0x11111111 )
  mk_net_msg( 7,   7,  0,       0x22222222 )

  return [ src_msgs, sink_msgs ]

def east_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  mk_net_msg( 1,   0,  0,       0xaaaaaaaa )
  mk_net_msg( 2,   1,  0,       0xbbbbbbbb )
  mk_net_msg( 3,   2,  0,       0xcccccccc )
  mk_net_msg( 4,   3,  0,       0xdddddddd )
  mk_net_msg( 5,   4,  0,       0xeeeeeeee )
  mk_net_msg( 6,   5,  0,       0xffffffff )
  mk_net_msg( 7,   6,  0,       0x11111111 )
  mk_net_msg( 0,   7,  0,       0x22222222 )

  return [ src_msgs, sink_msgs ]

def west_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  mk_net_msg( 0,   1,  0,       0xaaaaaaaa )
  mk_net_msg( 1,   2,  0,       0xbbbbbbbb )
  mk_net_msg( 2,   3,  0,       0xcccccccc )
  mk_net_msg( 3,   4,  0,       0xdddddddd )
  mk_net_msg( 4,   5,  0,       0xeeeeeeee )
  mk_net_msg( 5,   6,  0,       0xffffffff )
  mk_net_msg( 6,   7,  0,       0x11111111 )
  mk_net_msg( 7,   0,  0,       0x22222222 )

  return [ src_msgs, sink_msgs ]


def deadlock_east_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  # ADD YOUR TEST CASES HERE

#--- gen-harness : begin  cut ---------------------------------------------
  # Permutation Traffic - Sending East by 3
  #           dest src seq_num, payload
  mk_net_msg( 3,   0,  1,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  1,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  1,       0xcccccccc )
  mk_net_msg( 6,   3,  1,       0xdddddddd )
  mk_net_msg( 7,   4,  1,       0xeeeeeeee )
  mk_net_msg( 0,   5,  1,       0xffffffff )
  mk_net_msg( 1,   6,  1,       0x11111111 )
  mk_net_msg( 2,   7,  1,       0x22222222 )
  mk_net_msg( 3,   0,  2,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  2,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  2,       0xcccccccc )
  mk_net_msg( 6,   3,  2,       0xdddddddd )
  mk_net_msg( 7,   4,  2,       0xeeeeeeee )
  mk_net_msg( 0,   5,  2,       0xffffffff )
  mk_net_msg( 1,   6,  2,       0x11111111 )
  mk_net_msg( 2,   7,  2,       0x22222222 )
  mk_net_msg( 3,   0,  3,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  3,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  3,       0xcccccccc )
  mk_net_msg( 6,   3,  3,       0xdddddddd )
  mk_net_msg( 7,   4,  3,       0xeeeeeeee )
  mk_net_msg( 0,   5,  3,       0xffffffff )
  mk_net_msg( 1,   6,  3,       0x11111111 )
  mk_net_msg( 2,   7,  3,       0x22222222 )
  mk_net_msg( 3,   0,  4,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  4,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  4,       0xcccccccc )
  mk_net_msg( 6,   3,  4,       0xdddddddd )
  mk_net_msg( 7,   4,  4,       0xeeeeeeee )
  mk_net_msg( 0,   5,  4,       0xffffffff )
  mk_net_msg( 1,   6,  4,       0x11111111 )
  mk_net_msg( 2,   7,  4,       0x22222222 )
  mk_net_msg( 3,   0,  5,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  5,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  5,       0xcccccccc )
  mk_net_msg( 6,   3,  5,       0xdddddddd )
  mk_net_msg( 7,   4,  5,       0xeeeeeeee )
  mk_net_msg( 0,   5,  5,       0xffffffff )
  mk_net_msg( 1,   6,  5,       0x11111111 )
  mk_net_msg( 2,   7,  5,       0x22222222 )
  mk_net_msg( 3,   0,  6,       0xaaaaaaaa )
  mk_net_msg( 4,   1,  6,       0xbbbbbbbb )
  mk_net_msg( 5,   2,  6,       0xcccccccc )
  mk_net_msg( 6,   3,  6,       0xdddddddd )
  mk_net_msg( 7,   4,  6,       0xeeeeeeee )
  mk_net_msg( 0,   5,  6,       0xffffffff )
  mk_net_msg( 1,   6,  6,       0x11111111 )
  mk_net_msg( 2,   7,  6,       0x22222222 )
#--- gen-harness : end cut ---------------------------------------------

  return [ src_msgs, sink_msgs ]

def deadlock_west_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  # ADD YOUR TEST CASES HERE

  return [ src_msgs, sink_msgs ]

def adaptive_non_minimal_msgs():

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  #           dest src seq_num, payload
  # ADD YOUR TEST CASES HERE

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# Ring unit tests with delay = 0 x 0
#-------------------------------------------------------------------------

def test_ring_terminal_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_terminal_delay0x0.vcd", 0, 0,
                terminal_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_east_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_east_delay0x0.vcd", 0, 0,
                east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_west_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_west_delay0x0.vcd", 0, 0,
                west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_east_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_east_delay0x0.vcd", 0, 0,
                deadlock_east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_west_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_west_delay0x0.vcd", 0, 0,
                deadlock_west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_adaptive_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_adaptive_delay0x0.vcd", 0, 0,
                adaptive_non_minimal_msgs(), num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Ring unit tests with delay = 5 x 0
#-------------------------------------------------------------------------

def test_ring_terminal_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_terminal_delay5x0.vcd", 5, 0,
                terminal_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_east_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_east_delay5x0.vcd", 5, 0,
                east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_west_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_west_delay5x0.vcd", 5, 0,
                west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_east_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_east_delay5x0.vcd", 5, 0,
                deadlock_east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_west_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_west_delay5x0.vcd", 5, 0,
                deadlock_west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_adaptive_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Ring_adaptive_delay5x0.vcd", 5, 0,
                adaptive_non_minimal_msgs(), num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Ring unit tests with delay = 0 x 5
#-------------------------------------------------------------------------

def test_ring_terminal_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_terminal_delay0x5.vcd", 0, 5,
                terminal_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_east_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_east_delay0x5.vcd", 0, 5,
                east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_west_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_west_delay0x5.vcd", 0, 5,
                west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_east_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_east_delay0x5.vcd", 0, 5,
                deadlock_east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_west_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_west_delay0x5.vcd", 0, 5,
                deadlock_west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_adaptive_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_adaptive_delay0x5.vcd", 0, 5,
                adaptive_non_minimal_msgs(), num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Ring unit tests with delay = 8 x 5
#-------------------------------------------------------------------------

def test_ring_terminal_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_terminal_delay8x5.vcd", 8, 5,
                terminal_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_east_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_east_delay8x5.vcd", 8, 5,
                east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_west_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_west_delay8x5.vcd", 8, 5,
                west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_east_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_east_delay8x5.vcd", 8, 5,
                deadlock_east_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_deadlock_west_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_deadlock_west_delay8x5.vcd", 8, 5,
                deadlock_west_msgs(), num_routers, num_messages, payload_nbits, 2 )

def test_ring_adaptive_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Ring_adaptive_delay8x5.vcd", 8, 5,
                adaptive_non_minimal_msgs(), num_routers, num_messages, payload_nbits, 2 )
