#=========================================================================
# Torus Unit Test
#=========================================================================

from   pymtl import *
import pmlib
import random
import pytest

from   math import ceil, log, sqrt

import pmlib.valrdy     as valrdy

from Torus import Torus
from pmlib.net_msgs import NetMsgParams

from pmlib.TestSource  import TestSource
from pmlib.TestNetSink import TestNetSink

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

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
    s.torus  = Torus( num_routers, num_messages, payload_nbits, num_entries )
    s.sink   = [ TestNetSink ( netmsg_params.nbits, sink_msgs[x], sink_delay )
                 for x in xrange( s.num_routers ) ]

    # connect

    for i in xrange( s.num_routers ):

      connect( s.torus.in_msg[i], s.src[i].out_msg )
      connect( s.torus.in_val[i], s.src[i].out_val )
      connect( s.torus.in_rdy[i], s.src[i].out_rdy )

      connect( s.torus.out_msg[i], s.sink[i].in_msg )
      connect( s.torus.out_val[i], s.sink[i].in_val )
      connect( s.torus.out_rdy[i], s.sink[i].in_rdy )

  def done( s ):
    done_flag = 1
    for i in xrange( num_routers ):
      done_flag &= s.src[i].done.value.uint and s.sink[i].done.value.uint
    return done_flag

  def line_trace( s ):
    return s.torus.line_trace()

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
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test Messages
#-------------------------------------------------------------------------

num_routers   = 4
num_messages  = 128
payload_nbits = 32
num_entries   = 4

netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

def terminal_msgs():

  size = 1

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):
      dest = i
      mk_net_msg( dest, i, j, 0 )

  return [ src_msgs, sink_msgs ]

def nearest_neighbor_east_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):
      if ( i == num_routers-1 ):
        dest = 0
      else:
        dest = i + 1

      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

def nearest_neighbor_west_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):
      if ( i == 0 ):
        dest = num_routers-1
      else:
        dest = i - 1

      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

def hotspot_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):

      # all routers send to node 0
      dest = 0
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

def partition_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  # Partition the network into halves
  partition_edge = num_routers / 2

  for i in xrange( num_routers ):
    for j in xrange( size ):
      if ( i < partition_edge ):
        dest_roll = random.randint( 0, partition_edge - 1 )
      else:
        dest_roll = random.randint( partition_edge, num_routers - 1 )
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest_roll, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

def uniform_random_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):
      dest_roll = random.randint( 0, num_routers - 1 )
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest_roll, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

def tornado_msgs( size ):

  src_msgs  = [ [] for x in xrange( num_routers ) ]
  sink_msgs = [ [] for x in xrange( num_routers ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src].append( msg )
    sink_msgs[dest].append( msg )

  for i in xrange( num_routers ):
    for j in xrange( size ):
      dest = ( i + ( (int( num_routers / 2 ) ) - 1 ) )% num_routers
      data_roll = random.randint( 0, pow( 2, 32 ) - 1 )
      mk_net_msg( dest, i, j, data_roll )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# Torus unit tests with delay = 0 x 0
#-------------------------------------------------------------------------

def test_torus_terminal_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_terminal_delay0x0.vcd", 0, 0,
                terminal_msgs(), num_routers, num_messages, payload_nbits,
                num_entries )

def test_torus_nearest_neighbor_east_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_east_delay0x0.vcd", 0, 0,
                nearest_neighbor_east_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_nearest_neighbor_west_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_west_delay0x0.vcd", 0, 0,
                nearest_neighbor_west_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_hotspot_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_hotspot_delay0x0.vcd", 0, 0,
                hotspot_msgs(1), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_partition_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_partition_delay0x0.vcd", 0, 0,
                partition_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_uniform_random_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_uniform_random_delay0x0.vcd", 0, 0,
                uniform_random_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_tornado_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_tornado_delay0x0.vcd", 0, 0,
                tornado_msgs(24), num_routers, num_messages,
                payload_nbits, num_entries )

#-------------------------------------------------------------------------
# Torus unit tests with delay = 5 x 0
#-------------------------------------------------------------------------

def test_torus_terminal_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_terminal_delay5x0.vcd", 5, 0,
                terminal_msgs(), num_routers, num_messages, payload_nbits,
                num_entries )

def test_torus_nearest_neighbor_east_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_east_delay5x0.vcd", 5, 0,
                nearest_neighbor_east_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_nearest_neighbor_west_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_west_delay5x0.vcd", 5, 0,
                nearest_neighbor_west_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_hotspot_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_hotspot_delay5x0.vcd", 5, 0,
                hotspot_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_partition_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_partition_delay5x0.vcd", 5, 0,
                partition_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_uniform_random_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_uniform_random_delay5x0.vcd", 5, 0,
                uniform_random_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_tornado_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "Torus_tornado_delay5x0.vcd", 5, 0,
                tornado_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

#-------------------------------------------------------------------------
# Torus unit tests with delay = 0 x 5
#-------------------------------------------------------------------------

def test_torus_terminal_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_terminal_delay0x5.vcd", 0, 5,
                terminal_msgs(), num_routers, num_messages, payload_nbits,
                num_entries )

def test_torus_nearest_neighbor_east_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_east_delay0x5.vcd", 0, 5,
                nearest_neighbor_east_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_nearest_neighbor_west_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_west_delay0x5.vcd", 0, 5,
                nearest_neighbor_west_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_hotspot_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_hotspot_delay0x5.vcd", 0, 5,
                hotspot_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_partition_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_partition_delay0x5.vcd", 0, 5,
                partition_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_uniform_random_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_uniform_random_delay0x5.vcd", 0, 5,
                uniform_random_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_tornado_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_tornado_delay0x5.vcd", 0, 5,
                tornado_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

#-------------------------------------------------------------------------
# Torus unit tests with delay = 8 x 5
#-------------------------------------------------------------------------

def test_torus_terminal_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_terminal_delay8x5.vcd", 8, 5,
                terminal_msgs(), num_routers, num_messages, payload_nbits,
                num_entries )

def test_torus_nearest_neighbor_east_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_east_delay8x5.vcd", 8, 5,
                nearest_neighbor_east_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_nearest_neighbor_west_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_nearest_neighbor_west_delay8x5.vcd", 8, 5,
                nearest_neighbor_west_msgs(8), num_routers,
                num_messages, payload_nbits, num_entries )

def test_torus_hotspot_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_hotspot_delay8x5.vcd", 8, 5,
                hotspot_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_partition_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_partition_delay8x5.vcd", 8, 5,
                partition_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_uniform_random_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_uniform_random_delay8x5.vcd", 8, 5,
                uniform_random_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )

def test_torus_tornado_delay8x5( dump_vcd ):
  run_net_test( dump_vcd, "Torus_tornado_delay8x5.vcd", 8, 5,
                tornado_msgs(8), num_routers, num_messages,
                payload_nbits, num_entries )
