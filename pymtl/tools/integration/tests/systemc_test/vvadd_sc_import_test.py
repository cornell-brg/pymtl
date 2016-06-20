#=========================================================================
# VvaddXcelSC_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink, TestMemory

from pclib.ifcs  import MemMsg4B
from RoccCoreMsg import RoccCoreCmdMsg, RoccCoreRespMsg

from VvaddXcelSC import VvaddXcelSC

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, xcel, src_msgs, sink_msgs,
                stall_prob, latency, src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( RoccCoreCmdMsg(),  src_msgs,  src_delay  )
    s.xcel = xcel
    s.mem  = TestMemory ( MemMsg4B(), 1, stall_prob, latency, 2**20 )
    s.sink = TestSink   ( RoccCoreRespMsg(), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.xcel.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.xcel = TranslationTool( s.xcel )

    # Connect

    s.connect( s.src.out,       s.xcel.xcelreq )
    s.connect( s.xcel.memreq,   s.mem.reqs[0]  )
    s.connect( s.xcel.memresp,  s.mem.resps[0] )
    s.connect( s.xcel.xcelresp, s.sink.in_     )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.xcel.line_trace() + " | " + \
           s.mem.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, raddr, data ):
  msg = RoccCoreCmdMsg()

  if   type_ == 'rd': msg.inst_funct = 0
  elif type_ == 'wr': msg.inst_funct = 1

  msg.inst_rs2 = raddr
  msg.rs1      = data
  return msg

def resp( type_, data ):
  msg = RoccCoreRespMsg()
  msg.resp_data = data
  msg.resp_rd   = 0
  return msg

#-------------------------------------------------------------------------
# Xcel Protocol
#-------------------------------------------------------------------------
# These are the source sink messages we need to configure the accelerator
# and wait for it to finish. We use the same messages in all of our
# tests. The difference between the tests is the data. The variable i is used
# to offset multiple data sets in memory

def gen_xcel_protocol_msgs( size, i ):
  return [
    req( 'wr', 1, 0x1000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 2, 0x2000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 3, 0x3000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 4, size              ), resp( 'wr', 0 ),
    req( 'wr', 0, 0                 ), resp( 'wr', 0 ),
    req( 'rd', 0, 0                 ), resp( 'rd', 1 ),
  ]

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

mini          = [ [ 0x1, 0x1, 0x1, 0x1],[ 0x1, 0x2, 0x3, 0x4 ] ]
small_data    = [ [ random.randint(0,0xffff)     for i in xrange(32) ], \
                  [ random.randint(0,0xffff)     for i in xrange(32) ] ]
large_data    = [ [ random.randint(0,0x7fffffff) for i in xrange(32) ], \
                  [ random.randint(0,0x7fffffff) for i in xrange(32) ] ]
multiple      = [ [ random.randint(0,0x7fffffff) for i in xrange(32) ] for j in xrange(8) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
                         #                delays   test mem
                         #                -------- ---------
  (                      "data            src sink stall lat"),
  [ "mini",               mini,           0,  0,   0,    0   ],
  [ "mini_delay_x4",      mini,           3, 14,   0.5,  2   ],
  [ "small_data",         small_data,     0,  0,   0,    0   ],
  [ "large_data",         large_data,     0,  0,   0,    0   ],
  [ "multi_data",         multiple,       0,  0,   0,    0   ],
  [ "small_data_3x14x0",  small_data,     3, 14,   0,    0   ],
  [ "small_data_0x0x4",   small_data,     0,  0,   0.5,  4   ],
  [ "multi_data_3x14x4",  multiple,       3, 14,   0.5,  4   ],
])

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( xcel, test_params, dump_vcd, test_verilog=False ):

  # Convert test data into byte array

  data = test_params.data
  data_src0 = data[::2]
  data_src1 = data[1::2]
  src0_bytes = [0]*len(data_src0)
  src1_bytes = [0]*len(data_src1)
  for i in xrange( len(data_src0) ):
    src0_bytes[i] = struct.pack("<{}I".format(len(data_src0[i])),*data_src0[i])
    src1_bytes[i] = struct.pack("<{}I".format(len(data_src1[i])),*data_src1[i])

  # Protocol messages

  xcel_protocol_msgs = []
  for i in xrange( len(data_src0) ):
    xcel_protocol_msgs = xcel_protocol_msgs + gen_xcel_protocol_msgs( len(data_src0[i]), i)
  xreqs  = xcel_protocol_msgs[::2]
  xresps = xcel_protocol_msgs[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( xcel, xreqs, xresps,
                    test_params.stall, test_params.lat,
                    test_params.src, test_params.sink,
                    dump_vcd, test_verilog )

  # Load the data into the test memory

  for i in xrange( len(data_src0) ):
    th.mem.write_mem( 0x1000 + 0x3000*i, src0_bytes[i] )
    th.mem.write_mem( 0x2000 + 0x3000*i, src1_bytes[i] )

  # Run the test

  run_sim( th, dump_vcd, max_cycles=20000 )

  # Retrieve data from test memory

  result_bytes = [0]*len(data_src0)
  for i in xrange( len(data_src0) ):
    result_bytes[i] = th.mem.read_mem( 0x3000+ 0x3000*i, len(src0_bytes[i]) )

  for i in xrange( len(result_bytes) ):

    # Convert result bytes into list of ints
    result = list(struct.unpack("<{}I".format(len(data_src0[i])),buffer(result_bytes[i])))

    # Compare result
    for j in xrange( len(result) ):
      assert result[j] == data_src0[i][j] + data_src1[i][j]
  
#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( VvaddXcelSC(), test_params, dump_vcd )

