#=========================================================================
# Router Unit Tests
#=========================================================================

from   pymtl import *
import pmlib

import pmlib.valrdy     as valrdy
import pmlib.net_msgs   as net_msgs

#from Router import Router
from RingRouter import RingRouter

from pmlib.adapters import ValRdyToValCredit, ValCreditToValRdy

from pmlib.TestSource  import TestSource
from pmlib.TestNetSink import TestNetSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay,
                router_id, num_routers, num_messages, payload_nbits, num_entries ):

    credits = 3  # TODO: this is hardcoded in RingRouter, fix later

    # Instantiate Models

    s.src    = [ TestSource  ( netmsg_params.nbits, src_msgs[x], src_delay   )
                 for x in xrange( 3 ) ]
    #s.router = Router ( router_id, num_routers, num_messages,
    #                    payload_nbits, num_entries )
    s.router = RingRouter ( router_id, num_routers, num_messages, payload_nbits )
    s.sink   = [ TestNetSink ( netmsg_params.nbits, sink_msgs[x], sink_delay )
                 for x in xrange( 3 ) ]

    s.v2c  = []
    s.c2v  = []
    for i in range(3):
      s.v2c  += [ ValRdyToValCredit( netmsg_params.nbits, credits ) ]
      s.c2v  += [ ValCreditToValRdy( netmsg_params.nbits, credits ) ]

    # connect

    for i in range( 3 ):
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
    for i in xrange( 3 ):
      done_flag &= s.src[i].done.value.uint and s.sink[i].done.value.uint
    return done_flag

  def line_trace( self ):
    trace = ''

    for i in range( 3 ):
      trace += self.v2c[i].line_trace() + ' '

    trace += '|| ' + self.router.line_trace() + ' ||'

    for i in range( 3 ):
      trace += self.c2v[i].line_trace() + ' '

    return trace

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_net_test( dump_vcd, vcd_file_name, src_delay, sink_delay,
                 test_msgs, router_id, num_routers, num_messages,
                 payload_nbits, num_entries ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( src_msgs, sink_msgs, src_delay, sink_delay,
                       router_id, num_routers, num_messages,
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

num_routers   = 8
num_messages  = 128
payload_nbits = 8

netmsg_params = net_msgs.NetMsgParams( num_routers, num_messages,
                                       payload_nbits )

def basic_msgs():

  src_msgs  = [ [] for x in xrange( 3 ) ]
  sink_msgs = [ [] for x in xrange( 3 ) ]

  # Syntax helpers

  mk_msg = netmsg_params.mk_msg

  def mk_net_msg( src_, sink, dest, src, seq_num, payload ):
    msg = mk_msg( dest, src, seq_num, payload )
    src_msgs[src_].append( msg )
    sink_msgs[sink].append( msg )

  # constants

  term = 1
  west = 0
  east = 2

  #           src_  sink  dest src seq_num, payload
  mk_net_msg( west, west, 0,   0,  0,       0xaa )
  mk_net_msg( east, term, 1,   2,  0,       0xbb )
  mk_net_msg( term, east, 2,   1,  0,       0xcc )
  mk_net_msg( west, west, 0,   0,  1,       0xdd )
  mk_net_msg( east, term, 1,   2,  1,       0xee )
  mk_net_msg( term, east, 2,   1,  1,       0xff )
  mk_net_msg( west, east, 2,   0,  2,       0x01 )
  mk_net_msg( term, east, 2,   1,  2,       0x02 )
  mk_net_msg( east, east, 2,   2,  2,       0x03 )
  mk_net_msg( east, west, 0,   7,  3,       0x10 )
  mk_net_msg( term, west, 0,   1,  3,       0x20 )
  mk_net_msg( east, west, 0,   6,  3,       0x30 )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# Router basic unit test with delay = 0 x 0, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay0x0( dump_vcd ):
  run_net_test( dump_vcd, "RouterBasic_delay0x0.vcd", 0, 0,
                basic_msgs(), 1, num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 5 x 0, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay5x0( dump_vcd ):
  run_net_test( dump_vcd, "RouterBasic_delay5x0.vcd", 5, 0,
                basic_msgs(), 1, num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 0 x 5, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay0x5( dump_vcd ):
  run_net_test( dump_vcd, "RouterBasic_delay0x5.vcd", 0, 5,
                basic_msgs(), 1, num_routers, num_messages, payload_nbits, 2 )

#-------------------------------------------------------------------------
# Router basic unit test with delay = 3 x 8, id = 1
#-------------------------------------------------------------------------

def test_router_basic_delay3x8( dump_vcd ):
  run_net_test( dump_vcd, "RouterBasic_delay3x8.vcd", 3, 8,
                basic_msgs(), 1, num_routers, num_messages, payload_nbits, 2 )
