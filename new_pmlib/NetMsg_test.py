#=========================================================================
# NetMsg_test.py
#=========================================================================
# Test suite for the network message type.

from new_pymtl import *
from NetMsg    import NetMsg

def test_netmsg_fields():

  # Create msg

  msg = NetMsg( 8, 256, 32 )

  msg.dest    = 1
  msg.src     = 2
  msg.seqnum  = 255
  msg.payload = 0xaabbccdd

  # Verify msg

  assert msg.dest    == 1
  assert msg.src     == 2
  assert msg.seqnum  == 255
  assert msg.payload == 0xaabbccdd

def test_mk_msg():

  # Create msg

  msg = NetMsg( 8, 256, 32 ).mk_msg( 1, 2, 255, 0xaabbccdd )

  # Verify msg

  assert msg.dest    == 1
  assert msg.src     == 2
  assert msg.seqnum  == 255
  assert msg.payload == 0xaabbccdd
