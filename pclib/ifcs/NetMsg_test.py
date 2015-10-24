#=========================================================================
# NetMsg_test.py
#=========================================================================
# Test suite for the network message type.

from pymtl  import *
from NetMsg import NetMsg

#-------------------------------------------------------------------------
# test_netmsg_fields
#-------------------------------------------------------------------------
def test_netmsg_fields():

  # Create msg

  msg = NetMsg( 8, 256, 32 )

  msg.dest    = 1
  msg.src     = 2
  msg.opaque  = 255
  msg.payload = 0xaabbccdd

  # Verify msg

  assert msg.dest    == 1
  assert msg.src     == 2
  assert msg.opaque  == 255
  assert msg.payload == 0xaabbccdd

#-------------------------------------------------------------------------
# test_mk_msg
#-------------------------------------------------------------------------
def test_mk_msg():

  # Create msg

  msg = NetMsg( 8, 256, 32 ).mk_msg( 1, 2, 255, 0xaabbccdd )

  # Verify msg

  assert msg.dest    == 1
  assert msg.src     == 2
  assert msg.opaque  == 255
  assert msg.payload == 0xaabbccdd
