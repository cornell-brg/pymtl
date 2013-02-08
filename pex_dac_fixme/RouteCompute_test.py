#=========================================================================
# RouteCompute Test
#=========================================================================
# Unit tests for Route Computation

import pmlib.net_msgs   as net_msgs

from RouteCompute import RouteCompute
from pmlib.TestVectorSimulator import TestVectorSimulator

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

  model = RouteCompute( router_x_id, router_y_id, num_routers, netmsg_params )
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
