#=========================================================================
# RouteCompute
#=========================================================================
# This class implements the logic for route computation based on greedy
# routing algorithm. We assume a ring network with provided netmsg_params
# parameters, obtained from the net_msgs model, to calculate a route. We
# use each routers_id and route information to caculate the route.

from   pymtl import *
import pmlib

from   math import log,ceil,sqrt

import pmlib.net_msgs   as net_msgs
from   pmlib.TestVectorSimulator import TestVectorSimulator

class RingRouteCompute (Model):

  @capture_args
  def __init__( s, router_id, num_routers, srcdest_nbits ):

    # Local Constants

    s.router_id = router_id
    s.end_node  = num_routers-1

    # Interface Ports

    s.dest      = InPort  ( srcdest_nbits )
    s.route     = OutPort ( 2 )

    # Temporary Wires

    s.dist_east = Wire    ( srcdest_nbits )
    s.dist_west = Wire    ( srcdest_nbits )

    # Route Constants

    s.east  = 2
    s.west  = 1
    s.term  = 0

  @combinational
  def comb( s ):

    # HACKY Remove .uints for translation to work
    # east & west dist calculations

    if ( s.dest.value < s.router_id ):
      s.dist_east.value = \
        s.dest.value + ( s.end_node - s.router_id ) + 1
    else:
      s.dist_east.value = \
        s.dest.value - s.router_id

    if   ( s.dest.value > s.router_id ):
      s.dist_west.value = \
        s.router_id + ( s.end_node - s.dest.value ) + 1
    else:
      s.dist_west.value = \
        s.router_id + ~s.dest.value + 1

    if   ( s.dest.value == s.router_id ):
      s.route.value = s.term
    elif ( s.dist_west.value < s.dist_east.value ):
      s.route.value = s.west
    else:
      s.route.value = s.east

# Unit tests for Route Computation

def test_routecompute( dump_vcd ):

  # network params

  num_routers   = 4
  num_messages  = 32
  payload_nbits = 32

  netmsg_params = net_msgs.NetMsgParams( num_routers, num_messages,
                                         payload_nbits )

  # constants

  east  = 2
  west  = 1
  term  = 0

  router_id = 0

  # Test vectors

  test_vectors = [
    # dest route
    [ 0,   term  ],
    [ 1,   east  ],
    [ 3,   west  ],
    [ 2,   east  ],
      ]

  # Instantiate and elaborate the model

  model = RingRouteCompute( router_id, num_routers,
            netmsg_params.srcdest_nbits )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.dest.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.route.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "RingRouteCompute.vcd" )
  sim.run_test()
