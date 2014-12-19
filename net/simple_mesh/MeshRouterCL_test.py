#=========================================================================
# MeshRouterCL_test
#=========================================================================

import pytest

from pymtl        import *
from pclib.test   import TestSource, TestNetSink
from pclib.ifcs import NetMsg

from MeshRouterCL import MeshRouterCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs, sink_msgs, src_delay, sink_delay,
                id_, nrouters, nmessages, payload_nbits, nentries ):

    s.src_msgs      = src_msgs
    s.sink_msgs     = sink_msgs
    s.src_delay     = src_delay
    s.sink_delay    = sink_delay
    s.id_           = id_
    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits
    s.nentries      = nentries
    s.ModelType     = ModelType

  def elaborate_logic( s ):

    # Instantiate Models

    msg_type = lambda: NetMsg( s.nrouters, s.nmessages, s.payload_nbits )

    s.src    = [ TestSource  ( msg_type(), s.src_msgs[x],  s.src_delay  )
                 for x in xrange( 5 ) ]

    s.router = s.ModelType( s.id_, s.nrouters, s.nmessages,
                            s.payload_nbits, s.nentries )

    s.sink   = [ TestNetSink ( msg_type(), s.sink_msgs[x], s.sink_delay )
                 for x in xrange( 5 ) ]

    if s.test_verilog:
      s.router.vcd_file = s.vcd_file
      s.router = get_verilated( s.router )

    # connect

    for i in xrange( 5 ):
      s.connect( s.router.in_[i], s.src[i].out  )
      s.connect( s.router.out[i], s.sink[i].in_ )

  def done( s ):
    done_flag = 1
    for i in xrange( 5 ):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  def line_trace( s ):
    in_ = ' '.join( [ x.out.to_str( x.out.msg.dest ) for x in s.src ] )
    out = ' '.join( [ x.in_.to_str( x.in_.msg.dest ) for x in s.sink ] )
    return in_ + ' >>> ' + s.router.line_trace() + ' >>> '+ out

#-------------------------------------------------------------------------
# run_router_test
#-------------------------------------------------------------------------
def run_router_test( ModelType, src_delay, sink_delay, test_msgs, id_,
                     nrouters, nmessages, payload_nbits, num_entries,
                     dump_vcd, test_verilog=False ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs, src_delay, sink_delay,
                       id_, nrouters, nmessages, payload_nbits,
                       num_entries )
  model.vcd_file     = dump_vcd
  model.test_verilog = test_verilog
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check for success

  if not model.done():
    raise AssertionError( "Simulation did not complete!" )

#=========================================================================
# Test Messages
#=========================================================================
#
#   00 - 01 - 02 - 03
#   |    |    |    |
#   04 - 05 - 06 - 07
#   |    |    |    |
#   08 - 09 - 10 - 11
#   |    |    |    |
#   12 - 13 - 14 - 15
#

nrouters      = 16
nmessages     = 128
payload_nbits = 8

#-------------------------------------------------------------------------
# mk_msg
#-------------------------------------------------------------------------
def mk_msg( dest, src, seqnum, payload ):
  """Utility function to create a NetMsg object."""
  msg         = NetMsg( nrouters, nmessages, payload_nbits )
  msg.src     = src
  msg.dest    = dest
  msg.seqnum  = seqnum
  msg.payload = payload
  return msg

#-------------------------------------------------------------------------
# basic_msgs
#-------------------------------------------------------------------------
def basic_msgs():

  src_msgs  = [ [] for x in xrange( 5 ) ]
  sink_msgs = [ [] for x in xrange( 5 ) ]

  # mk_net_msg
  def mk_net_msg( src_, sink, dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src_].append( msg )
    sink_msgs[sink].append( msg )

  # constants

  north = 0
  east  = 1
  south = 2
  west  = 3
  term  = 4

  #           src_   sink   dest src seq_num, payload
  mk_net_msg( term,  term,  5,   5,  0,       0x0a )
  mk_net_msg( east,  east,  6,   6,  0,       0x0b )
  mk_net_msg( west,  west,  4,   4,  0,       0x0c )
  mk_net_msg( north, north, 1,   1,  0,       0x0d )
  mk_net_msg( south, south, 9,   9,  0,       0x0e )
  mk_net_msg( term,  term,  5,   5,  1,       0x1a )
  mk_net_msg( east,  west,  4,   6,  1,       0x1b )
  mk_net_msg( west,  east,  6,   4,  1,       0x1c )
  mk_net_msg( north, south, 9,   1,  1,       0x1d )
  mk_net_msg( south, north, 1,   9,  1,       0x1e )

  mk_net_msg( term,  east,  6,   5,  2,       0x2a )
  mk_net_msg( east,  east,  6,   6,  2,       0x2b )
  mk_net_msg( west,  east,  6,   4,  2,       0x2c )
  mk_net_msg( north, east,  6,   1,  2,       0x2d )
  mk_net_msg( south, east,  6,   9,  2,       0x2e )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# hotspot_msgs
#-------------------------------------------------------------------------
def hotspot_msgs():

  src_msgs  = [ [] for x in xrange( 5 ) ]
  sink_msgs = [ [] for x in xrange( 5 ) ]

  # mk_net_msg
  def mk_net_msg( src_, sink, dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src_].append( msg )
    sink_msgs[sink].append( msg )

  # constants

  north = 0
  east  = 1
  south = 2
  west  = 3
  term  = 4

  #           src_   sink   dest src seq_num, payload
  mk_net_msg( term,  east,  6,   5,  0,       0x0a )
  mk_net_msg( east,  east,  6,   6,  0,       0x0b )
  mk_net_msg( west,  east,  6,   4,  0,       0x0c )
  mk_net_msg( north, east,  6,   1,  0,       0x0d )
  mk_net_msg( south, east,  6,   9,  0,       0x0e )
  mk_net_msg( term,  east,  6,   5,  1,       0x1a )
  mk_net_msg( east,  east,  6,   6,  1,       0x1b )
  mk_net_msg( west,  east,  6,   4,  1,       0x1c )
  mk_net_msg( north, east,  6,   1,  1,       0x1d )
  mk_net_msg( south, east,  6,   9,  1,       0x1e )

  mk_net_msg( term,  east,  6,   5,  2,       0x2a )
  mk_net_msg( east,  east,  6,   6,  2,       0x2b )
  mk_net_msg( west,  east,  6,   4,  2,       0x2c )
  mk_net_msg( north, east,  6,   1,  2,       0x2d )
  mk_net_msg( south, east,  6,   9,  2,       0x2e )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# test_router
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay, test_msgs', [
  # basic messages
  (0, 0, basic_msgs()),
  (5, 0, basic_msgs()),
  (0, 5, basic_msgs()),
  (3, 8, basic_msgs()),

  # hotspot messages
  (0, 0, hotspot_msgs()),
  (5, 0, hotspot_msgs()),
  (0, 5, hotspot_msgs()),
  (3, 8, hotspot_msgs()),

  # TODO: arbitration test, need specific order
])
def test_router( dump_vcd, src_delay, sink_delay, test_msgs ):
  router_id   = 5
  num_entries = 4
  run_router_test( MeshRouterCL, sink_delay, sink_delay, test_msgs, router_id,
                   nrouters, nmessages, payload_nbits, num_entries, dump_vcd )

