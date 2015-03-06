#=========================================================================
# MemMsg_test
#=========================================================================
# Test suite for the memory messages

from pymtl  import *
from MemMsg import MemReqMsg, MemRespMsg

#-------------------------------------------------------------------------
# test_req_fields
#-------------------------------------------------------------------------

def test_req_fields():

  # Create msg

  msg = MemReqMsg(16,40)
  msg.type_ = 0
  msg.addr  = 0x1000
  msg.len   = 3

  # Verify msg

  assert msg.type_ == 0
  assert msg.addr  == 0x1000
  assert msg.len   == 3

  # Create msg

  msg = MemReqMsg(16,40)
  msg.type_ = 1
  msg.addr  = 0x2000
  msg.len   = 4
  msg.data  = 0xdeadbeef

  # Verify msg

  assert msg.type_ == 1
  assert msg.addr  == 0x2000
  assert msg.len   == 4
  assert msg.data  == 0xdeadbeef

#-------------------------------------------------------------------------
# test_req_str
#-------------------------------------------------------------------------

def test_req_str():

  # Create msg

  msg = MemReqMsg(16,40)
  msg.type_ = 0
  msg.addr  = 0x1000
  msg.len   = 3

  # Verify string

  assert str(msg) == "rd:1000:          "

  # Create msg

  msg = MemReqMsg(16,40)
  msg.type_ = 1
  msg.addr  = 0x2000
  msg.len   = 4
  msg.data  = 0xdeadbeef

  # Verify string

  assert str(msg) == "wr:2000:00deadbeef"

#-------------------------------------------------------------------------
# test_resp_fields
#-------------------------------------------------------------------------

def test_resp_fields():

  # Create msg

  msg = MemRespMsg(40)
  msg.type_ = 0
  msg.len   = 3
  msg.data  = 0x0000adbeef

  # Verify msg

  assert msg.type_ == 0
  assert msg.len   == 3
  assert msg.data  == 0x0000adbeef

  # Create msg

  msg = MemRespMsg(40)
  msg.type_ = 1
  msg.len   = 0
  msg.data  = 0

  # Verify msg

  assert msg.type_ == 1
  assert msg.len   == 0
  assert msg.data  == 0

#-------------------------------------------------------------------------
# test_resp_str
#-------------------------------------------------------------------------

def test_resp_str():

  # Create msg

  msg = MemRespMsg(40)
  msg.type_ = 0
  msg.len   = 3
  msg.data  = 0x0000adbeef

  # Verify string

  assert str(msg) == "rd:0000adbeef"

  # Create msg

  msg = MemRespMsg(40)
  msg.type_ = 1
  msg.len   = 0
  msg.data  = 0

  # Verify string

  assert str(msg) == "wr:          "

