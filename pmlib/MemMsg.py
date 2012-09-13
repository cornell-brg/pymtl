#=========================================================================
# MemMsg.py
#=========================================================================
# This file describes the mememory message field widths and has hellper
# functions to create messages.

from pymtl import *

# Constants for Memory messages with 32 bit addr and 32 bit data

NREQBITS  = 67
NRESPBITS = 35

REQ_TYPE = 66
REQ_ADDR = slice( 34, 66 )
REQ_LEN  = slice( 32, 34 )
REQ_DATA = slice( 0,  32 )

RESP_TYPE = 34
RESP_LEN  = slice( 32, 34 )
RESP_DATA = slice( 0,  32 )

MAX_DATA_BYTES = 4

def mk_req( _type, addr, _len, data):
  memreq_msg = Bits( NREQBITS )
  memreq_msg[REQ_TYPE].uint = _type
  memreq_msg[REQ_ADDR].uint = addr
  memreq_msg[REQ_LEN].uint  = _len
  memreq_msg[REQ_DATA].uint = data
  return memreq_msg

def mk_resp( _type, _len, data):
  memresp_msg = Bits( NRESPBITS )
  memresp_msg[RESP_TYPE].uint = _type
  memresp_msg[RESP_LEN].uint  = _len
  memresp_msg[RESP_DATA].uint = data
  return memresp_msg
