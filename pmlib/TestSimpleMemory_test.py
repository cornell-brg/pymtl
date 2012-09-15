#=========================================================================
# TestSimpleMemory Test Suite
#=========================================================================

from pymtl import *
import pmlib
import mem_msgs

from TestSimpleMemory import TestSimpleMemory

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, memreq_params, memresp_params,
                src_msgs, sink_msgs, src_delay, sink_delay ):

    # Instantiate models

    self.src  = pmlib.TestSource ( 67, src_msgs,  src_delay  )
    self.mem  = TestSimpleMemory ( memreq_params, memresp_params )
    self.sink = pmlib.TestSink   ( 35, sink_msgs, sink_delay )

    # connect
    connect( self.src.out_msg, self.mem.memreq_msg  )
    connect( self.src.out_val, self.mem.memreq_val  )
    connect( self.src.out_rdy, self.mem.memreq_rdy  )

    connect( self.sink.in_msg, self.mem.memresp_msg )
    connect( self.sink.in_val, self.mem.memresp_val )
    connect( self.sink.in_rdy, self.mem.memresp_rdy )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.mem.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_mem_test( dump_vcd, vcd_file_name, src_delay, sink_delay ):

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

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

  # Test messages

  test_msgs = [

    req_wr( 0x00001000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ),
    req_wr( 0x00001001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00001001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ),
    req_wr( 0x00001000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ),

    req_wr( 0x00002000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ),
    req_wr( 0x00002002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00002002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ),
    req_wr( 0x00002000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00002000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ),

    req_wr( 0x00004000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ),
    req_wr( 0x00004004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00004004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ),
    req_wr( 0x00004000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ),
    req_rd( 0x00004000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ),

  ]

  src_msgs  = test_msgs[::2]
  sink_msgs = test_msgs[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( memreq_params, memresp_params, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestSimpleMemory unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_mem_test( dump_vcd, "TestSimpleMemory_test_delay0x0.vcd", 0, 0 )

#-------------------------------------------------------------------------
# TestSimpleMemory unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  run_mem_test( dump_vcd, "TestSimpleMemory_test_delay5x10.vcd", 5, 10 )

#-------------------------------------------------------------------------
# TestSimpleMemory unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  run_mem_test( dump_vcd, "TestSimpleMemory_test_delay10x5.vcd", 10, 5 )

