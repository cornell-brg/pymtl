#=========================================================================
# Router Unit Tests
#=========================================================================

from   pymtl import *
import pmlib

import pmlib.valrdy     as valrdy
import pmlib.net_msgs   as net_msgs

from TorusRouter    import TorusRouter

from pmlib.adapters import ValRdyToValCredit, ValCreditToValRdy

from pmlib.TestSource  import TestSource
from pmlib.TestNetSink import TestNetSink

from pymtl.verilator_sim import get_verilated

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay,
                router_x_id, router_y_id, num_routers, num_messages,
                payload_nbits, num_entries ):

    # Instantiate Models

    s.src    = [ TestSource  ( netmsg_params.nbits, src_msgs[x], src_delay   )
                 for x in xrange( 5 ) ]
    s.router = get_verilated( TorusRouter ( router_x_id, router_y_id,
                                            num_routers, num_messages,
                                            payload_nbits, num_entries ) )
    s.sink   = [ TestNetSink ( netmsg_params.nbits, sink_msgs[x], sink_delay )
                 for x in xrange( 5 ) ]

    s.v2c  = []
    s.c2v  = []
    for i in range(5):
      s.v2c  += [ ValRdyToValCredit( netmsg_params.nbits, num_entries ) ]
      s.c2v  += [ ValCreditToValRdy( netmsg_params.nbits, num_entries ) ]

    # connect

    for i in range( 5 ):
      connect( s.src[i].out_msg,        s.v2c[i].from_msg     )
      connect( s.src[i].out_val,        s.v2c[i].from_val     )
      connect( s.src[i].out_rdy,        s.v2c[i].from_rdy     )

      connect( s.v2c[i].to_msg,         s.router.in_msg[i]    )
      connect( s.v2c[i].to_val,         s.router.in_val[i]    )
      connect( s.v2c[i].to_credit,      s.router.in_credit[i] )

      connect( s.router.out_msg[i],     s.c2v[i].from_msg     )
      connect( s.router.out_val[i],     s.c2v[i].from_val     )
      connect( s.router.out_credit[i],  s.c2v[i].from_credit  )

      connect( s.c2v[i].to_msg,         s.sink[i].in_msg      )
      connect( s.c2v[i].to_val,         s.sink[i].in_val      )
      connect( s.c2v[i].to_rdy,         s.sink[i].in_rdy      )

  def done( s ):
    done_flag = 1
    for i in xrange( 5 ):
      done_flag &= s.src[i].done.value.uint and s.sink[i].done.value.uint
    return done_flag

  def line_trace( self ):
    trace = ''

    for i in range( 5 ):
      trace += self.v2c[i].line_trace() + ' '

    trace += '|| ' + self.router.line_trace() + ' ||'

    for i in range( 5 ):
      trace += self.c2v[i].line_trace() + ' '

    return trace

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_net_test( dump_vcd, vcd_file_name, src_delay, sink_delay,
                 test_msgs, router_x_id, router_y_id, num_routers, num_messages,
                 payload_nbits, num_entries ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( src_msgs, sink_msgs, src_delay, sink_delay,
                       router_x_id, router_y_id, num_routers, num_messages,
                       payload_nbits, num_entries )
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

num_routers   = 16
num_messages  = 128
payload_nbits = 8

netmsg_params = net_msgs.NetMsgParams( num_routers, num_messages,
                                       payload_nbits )

def basic_msgs():

  src_msgs  = [ [] for x in xrange( 5 ) ]
  sink_msgs = [ [] for x in xrange( 5 ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

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
  mk_net_msg( term,  term,  5,   5,  0,       0xaa )
  mk_net_msg( east,  east,  6,   6,  0,       0xbb )
  mk_net_msg( west,  west,  4,   4,  0,       0xcc )
  mk_net_msg( north, north, 1,   1,  0,       0xdd )
  mk_net_msg( south, south, 9,   9,  0,       0xee )
  mk_net_msg( term,  term,  5,   5,  1,       0xaa )
  mk_net_msg( east,  west,  4,   6,  1,       0xbb )
  mk_net_msg( west,  east,  6,   4,  1,       0xcc )
  mk_net_msg( north, south, 9,   1,  1,       0xdd )
  mk_net_msg( south, north, 1,   9,  1,       0xee )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# Router basic unit test with delay = 0 x 0, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "TRouterBasic_delay0x0.vcd", 0, 0,
                basic_msgs(), 1, 1, num_routers, num_messages, payload_nbits, 4 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 5 x 0, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "TRouterBasic_delay5x0.vcd", 5, 0,
                basic_msgs(), 1, 1, num_routers, num_messages, payload_nbits, 4 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 0 x 5, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "TRouterBasic_delay0x5.vcd", 0, 5,
                basic_msgs(), 1, 1, num_routers, num_messages, payload_nbits, 4 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 3 x 8, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay3x8( dump_vcd ):
  run_net_test( dump_vcd, "TRouterBasic_delay3x8.vcd", 3, 8,
                basic_msgs(), 1, 1, num_routers, num_messages, payload_nbits, 4 )
