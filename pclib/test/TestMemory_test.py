#=========================================================================
# TestMemory_test.py
#=========================================================================

from __future__ import print_function

import pytest
import pclib.ifcs.mem_msgs as mem_msgs

from pymtl      import *
from pclib.test import TestSource, TestSink, TestMemory

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, memreq_params, memresp_params, nports,
                src_msgs, sink_msgs, src_delay, sink_delay, mem_delay ):

    # Instantiate models

    s.src  = [ TestSource( memreq_params.nbits, src_msgs[x], src_delay )
               for x in range( nports ) ]

    s.mem  = TestMemory( memreq_params, memresp_params, nports, mem_delay )

    s.sink = [ TestSink( memresp_params.nbits, sink_msgs[x], sink_delay )
               for x in range( nports ) ]

    # connect

    for i in range( nports ):
      s.connect( s.src[i].out,  s.mem.reqs[i]  )
      s.connect( s.sink[i].in_, s.mem.resps[i] )

  def done( s ):

    done_flag = 1
    for src, sink in zip( s.src, s.sink ):
      done_flag &= (src.done.uint() and sink.done.uint())
    return done_flag

  def line_trace( s ):
    return s.mem.line_trace()

#-------------------------------------------------------------------------
# run_mem_test
#-------------------------------------------------------------------------
def run_mem_test( dump_vcd, src_delay, sink_delay,
                  mem_delay, nports, test_msgs ):

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( memreq_params, memresp_params, nports, src_msgs,
                       sink_msgs, src_delay, sink_delay, mem_delay )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# single port memory test messages
#-------------------------------------------------------------------------
def single_port_mem_test_msgs():

  # number of memory ports
  nports = 1

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  src_msgs  = [ [] for x in range( nports ) ]
  sink_msgs = [ [] for x in range( nports ) ]

  # Syntax helpers

  req  = memreq_params.mk_req
  resp = memresp_params.mk_resp

  def req_rd( addr, len_, data ):
    return req( memreq_params.type_read, addr, len_, data )

  def req_wr( addr, len_, data ):
    return req( memreq_params.type_write, addr, len_, data )

  def resp_rd( len_, data ):
    return resp( memresp_params.type_read, len_, data )

  def resp_wr( len_, data ):
    return resp( memresp_params.type_write, len_, data )

  def mk_req_resp( idx, req, resp ):
    src_msgs[idx].append( req )
    sink_msgs[idx].append( resp )

  # Test messages

  #            port mem_request                          mem_response
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 0,   req_wr( 0x00001001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )

  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 0,   req_wr( 0x00002002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )

  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 0,   req_wr( 0x00004004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# dual port memory test messages
#-------------------------------------------------------------------------
def dual_port_mem_test_msgs():

  # number of memory ports
  nports = 2

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  src_msgs  = [ [] for x in range( nports ) ]
  sink_msgs = [ [] for x in range( nports ) ]

  # Syntax helpers

  req  = memreq_params.mk_req
  resp = memresp_params.mk_resp

  def req_rd( addr, len_, data ):
    return req( memreq_params.type_read, addr, len_, data )

  def req_wr( addr, len_, data ):
    return req( memreq_params.type_write, addr, len_, data )

  def resp_rd( len_, data ):
    return resp( memresp_params.type_read, len_, data )

  def resp_wr( len_, data ):
    return resp( memresp_params.type_write, len_, data )

  def mk_req_resp( idx, req, resp ):
    src_msgs[idx].append( req )
    sink_msgs[idx].append( resp )

  # Test messages

  # Note: Set the address of port 1 to large enough offset such that there
  # will be no overlap between port 0 and port 1 requests

  #            port mem_request                          mem_response
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 1,   req_rd( 0x00011000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 0,   req_wr( 0x00001001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 1,   req_rd( 0x00011001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )
  mk_req_resp( 1,   req_rd( 0x00011000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )

  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 1,   req_rd( 0x00012000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 0,   req_wr( 0x00002002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 1,   req_rd( 0x00012002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )
  mk_req_resp( 1,   req_rd( 0x00012000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )

  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 1,   req_rd( 0x00014000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 0,   req_wr( 0x00004004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 1,   req_rd( 0x00014004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )
  mk_req_resp( 1,   req_rd( 0x00014000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# quad port memory test messages
#-------------------------------------------------------------------------
def quad_port_mem_test_msgs():

  # number of memory ports
  nports = 4

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  src_msgs  = [ [] for _ in range( nports ) ]
  sink_msgs = [ [] for _ in range( nports ) ]

  # Syntax helpers

  req  = memreq_params.mk_req
  resp = memresp_params.mk_resp

  def req_rd( addr, len_, data ):
    return req( memreq_params.type_read, addr, len_, data )

  def req_wr( addr, len_, data ):
    return req( memreq_params.type_write, addr, len_, data )

  def resp_rd( len_, data ):
    return resp( memresp_params.type_read, len_, data )

  def resp_wr( len_, data ):
    return resp( memresp_params.type_write, len_, data )

  def mk_req_resp( idx, req, resp ):
    src_msgs[idx].append( req )
    sink_msgs[idx].append( resp )

  # Test messages

  # Note: Set the address of ports to large enough offset such that there
  # will be no overlap between port 0, port 1, port 2 and port 3 requests

  #            port mem_request                          mem_response
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00021000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00031000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 1,   req_rd( 0x00011000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 2,   req_rd( 0x00021000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 3,   req_rd( 0x00031000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 0,   req_wr( 0x00001001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00021001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00031001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 1,   req_rd( 0x00011001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 2,   req_rd( 0x00021001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 3,   req_rd( 0x00031001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00011000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00021000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00031000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )
  mk_req_resp( 1,   req_rd( 0x00011000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )
  mk_req_resp( 2,   req_rd( 0x00021000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )
  mk_req_resp( 3,   req_rd( 0x00031000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )

  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00022000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00032000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 1,   req_rd( 0x00012000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 2,   req_rd( 0x00022000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 3,   req_rd( 0x00032000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 0,   req_wr( 0x00002002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00022002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00032002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 1,   req_rd( 0x00012002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 2,   req_rd( 0x00022002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 3,   req_rd( 0x00032002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 0,   req_wr( 0x00002000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00012000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00022000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00032000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )
  mk_req_resp( 1,   req_rd( 0x00012000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )
  mk_req_resp( 2,   req_rd( 0x00022000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )
  mk_req_resp( 3,   req_rd( 0x00032000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )

  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00024000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00034000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 1,   req_rd( 0x00014000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 2,   req_rd( 0x00024000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 3,   req_rd( 0x00034000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 0,   req_wr( 0x00004004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00024004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00034004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 1,   req_rd( 0x00014004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 2,   req_rd( 0x00024004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 3,   req_rd( 0x00034004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 0,   req_wr( 0x00004000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 1,   req_wr( 0x00014000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 2,   req_wr( 0x00024000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 3,   req_wr( 0x00034000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )
  mk_req_resp( 1,   req_rd( 0x00014000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )
  mk_req_resp( 2,   req_rd( 0x00024000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )
  mk_req_resp( 3,   req_rd( 0x00034000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------
# test_single_port
#-------------------------------------------------------------------------
@pytest.mark.parametrize('src_delay,sink_delay,mem_delay,nports',[
  ( 0,  0,  3,  1),
  ( 5, 10,  8,  1),
  (10,  5,  2,  1),
])
def test_single_port( dump_vcd, src_delay, sink_delay, mem_delay, nports ):
  run_mem_test( dump_vcd, src_delay, sink_delay, mem_delay, nports,
                single_port_mem_test_msgs() )

#-------------------------------------------------------------------------
# test_dual_port
#-------------------------------------------------------------------------
@pytest.mark.parametrize('src_delay,sink_delay,mem_delay,nports',[
  ( 0,  0,  4,  2),
  ( 5, 10,  3,  2),
  (10,  5,  3,  2),
])
def test_dual_port( dump_vcd, src_delay, sink_delay, mem_delay, nports ):
  run_mem_test( dump_vcd, src_delay, sink_delay, mem_delay, nports,
                dual_port_mem_test_msgs() )

#-------------------------------------------------------------------------
# test_quad_port
#-------------------------------------------------------------------------
@pytest.mark.parametrize('src_delay,sink_delay,mem_delay,nports',[
  ( 0,  0,  7,  4),
  ( 5, 10,  4,  4),
  (10,  5,  6,  4),
])
def test_quad_port( dump_vcd, src_delay, sink_delay, mem_delay, nports ):
  run_mem_test( dump_vcd, src_delay, sink_delay, mem_delay, nports,
                quad_port_mem_test_msgs() )

