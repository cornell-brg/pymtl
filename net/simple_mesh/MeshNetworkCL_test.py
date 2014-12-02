#=========================================================================
# MeshNetworkCL_test
#=========================================================================

import pytest
import random

from pymtl        import *
from pclib.ifaces import NetMsg
from pclib.test   import TestSource, TestNetSink

from traffic_generators import *
from MeshNetworkBL_test import run_net_test
from MeshNetworkCL      import MeshNetworkCL

#-------------------------------------------------------------------------
# network args
#-------------------------------------------------------------------------

import traffic_generators

nrouters      = traffic_generators.nrouters      =  16
nmessages     = traffic_generators.nmessages     = 128
payload_nbits = traffic_generators.payload_nbits =  32

nentries = 4

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

#-------------------------------------------------------------------------
# test_mesh
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay,sink_delay,test_msgs', [
  # terminal tests
  (0, 0, terminal_msgs()),
  (5, 0, terminal_msgs()),
  (0, 5, terminal_msgs()),
  (8, 5, terminal_msgs()),
  # nearest neighbor east tests
  (0, 0, nearest_neighbor_east_msgs(8)),
  (5, 0, nearest_neighbor_east_msgs(8)),
  (0, 5, nearest_neighbor_east_msgs(8)),
  (8, 5, nearest_neighbor_east_msgs(8)),
  # nearest neighbor east tests
  (0, 0, nearest_neighbor_west_msgs(8)),
  (5, 0, nearest_neighbor_west_msgs(8)),
  (0, 5, nearest_neighbor_west_msgs(8)),
  (8, 5, nearest_neighbor_west_msgs(8)),
  # hotspot tests
  (0, 0, hotspot_msgs(8)),
  (5, 0, hotspot_msgs(8)),
  (0, 5, hotspot_msgs(8)),
  (8, 5, hotspot_msgs(8)),
  # partition tests
  (0, 0, partition_msgs(8)),
  (5, 0, partition_msgs(8)),
  (0, 5, partition_msgs(8)),
  (8, 5, partition_msgs(8)),
  # uniform random tests
  (0, 0, uniform_random_msgs(8)),
  (5, 0, uniform_random_msgs(8)),
  (0, 5, uniform_random_msgs(8)),
  (8, 5, uniform_random_msgs(8)),
  # tornado tests
  (0, 0, tornado_msgs(8)),
  (5, 0, tornado_msgs(8)),
  (0, 5, tornado_msgs(8)),
  (8, 5, tornado_msgs(8)),
])
def test_mesh( dump_vcd, src_delay, sink_delay, test_msgs ):
  run_net_test( dump_vcd, MeshNetworkCL, src_delay, sink_delay, test_msgs,
                nrouters, nmessages, payload_nbits, nentries )
