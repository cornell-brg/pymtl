#=======================================================================
# MeshRouterRTL_test
#=======================================================================

import pytest

from pymtl         import *

from MeshRouterRTL     import MeshRouterRTL
from MeshRouterCL_test import (
    run_router_test,
    basic_msgs,
    hotspot_msgs,
    nrouters,
    nmessages,
    payload_nbits,
)

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
def test_router( dump_vcd, test_verilog, src_delay, sink_delay, test_msgs ):
  router_id   = 5
  num_entries = 4
  run_router_test( MeshRouterRTL, sink_delay, sink_delay, test_msgs, router_id,
                   nrouters, nmessages, payload_nbits, num_entries, dump_vcd,
                   test_verilog = test_verilog )
