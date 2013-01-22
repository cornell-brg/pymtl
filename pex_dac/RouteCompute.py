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

class RouteCompute (Model):

  @capture_args
  def __init__( s, router_x_id, router_y_id, num_routers, srcdest_nbits ):

    # Local Constants

    s.router_x_id = router_x_id
    s.router_y_id = router_y_id

    # Note: Currently, converting a linear router_id into the x and y
    # dimensions assumes square torus networks with the number of nodes to
    # be a power of 2**n
    # CHANGED: Assuming that we pass in the x,y mapping to the router and
    # preserve it once it has been statically elaborated

    s.num_routers_1D = int( sqrt( num_routers ) )
    s.dim_nbits      = int( ceil( log( s.num_routers_1D, 2 ) ) )

    # Interface Ports

    s.dest          = InPort  ( srcdest_nbits )
    s.route         = OutPort ( 3 )

    # Temporary Wires

    s.dist_east     = Wire    ( s.dim_nbits )
    s.dist_west     = Wire    ( s.dim_nbits )
    s.dist_north    = Wire    ( s.dim_nbits )
    s.dist_south    = Wire    ( s.dim_nbits )

    s.x_dest        = Wire    ( s.dim_nbits )
    s.y_dest        = Wire    ( s.dim_nbits )
    s.x_self        = Wire    ( s.dim_nbits )
    s.y_self        = Wire    ( s.dim_nbits )

    #connect( s.x_self, s.router_x_id )
    #connect( s.y_self, s.router_y_id )

    #connect( s.x_dest, s.dest[ 0           :   s.dim_nbits ] )
    #connect( s.y_dest, s.dest[ s.dim_nbits : 2*s.dim_nbits ] )

    # Route Constants

    s.north = 0
    s.east  = 1
    s.south = 2
    s.west  = 3
    s.term  = 4

  @combinational
  def comb( s ):

    # self coordinates

    s.x_self.value = s.router_x_id
    s.y_self.value = s.router_y_id

    # self coordinates

    # HACKY: Remove .uint for translation

    s.x_dest.value = s.dest.value.uint % s.num_routers_1D
    s.y_dest.value = s.dest.value.uint / s.num_routers_1D
    #s.x_dest.value = s.dest.value % s.num_routers_1D
    #s.y_dest.value = s.dest.value / s.num_routers_1D

    # north, east, south & west dist calculations

    if ( s.y_dest.value < s.y_self.value ):
      s.dist_north.value = s.y_self.value - s.y_dest.value
    else:
      s.dist_north.value = \
        s.y_self.value + 1 + ~s.y_dest.value

    if ( s.y_dest.value > s.y_self.value ):
      s.dist_south.value = s.y_dest.value - s.y_self.value
    else:
      s.dist_south.value = \
        s.y_dest.value + 1 + ~s.y_self.value

    if ( s.x_dest.value < s.x_self.value ):
      s.dist_west.value = s.x_self.value - s.x_dest.value
    else:
      s.dist_west.value = \
        s.x_self.value + 1 + ~s.x_dest.value

    if ( s.x_dest.value > s.x_self.value ):
      s.dist_east.value = s.x_dest.value - s.x_self.value
    else:
      s.dist_east.value = \
        s.x_dest.value + 1 + ~s.x_self.value

    # route calculations

    if   (    ( s.x_dest.value == s.x_self.value )
          and ( s.y_dest.value == s.y_self.value ) ):
      s.route.value = s.term
    elif ( s.x_dest.value != s.x_self.value ):
      if ( s.dist_west.value < s.dist_east.value ):
        s.route.value = s.west
      else:
        s.route.value = s.east
    else:
      if ( s.dist_south.value < s. dist_north.value ):
        s.route.value = s.south
      else:
        s.route.value = s.north

# Unit tests for Route Computation

def test_routecompute( dump_vcd ):

  # network params

  num_routers   = 16
  num_messages  = 32
  payload_nbits = 32

  netmsg_params = net_msgs.NetMsgParams( num_routers, num_messages,
                                         payload_nbits )

  # constants

  north = 0
  east  = 1
  south = 2
  west  = 3
  term  = 4

  router_x_id = 0
  router_y_id = 0

  # Test vectors

  test_vectors = [
    # dest route
    [ 0,   term  ],
    [ 1,   east  ],
    [ 3,   west  ],
    [ 12,  north ],
    [ 4,   south ],
    [ 10,  east  ],
    [ 8,   north ]
      ]

  # Instantiate and elaborate the model

  model = RouteCompute( router_x_id, router_y_id, num_routers,
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
    sim.dump_vcd( "RouteCompute.vcd" )
  sim.run_test()
