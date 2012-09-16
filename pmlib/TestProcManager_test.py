#=========================================================================
# TestProcManager_test
#=========================================================================

from pymtl import *
import pmlib
import mem_msgs

from SparseMemoryImage import SparseMemoryImage
from TestMemory        import TestMemory
from TestProcManager   import TestProcManager

#-------------------------------------------------------------------------
# Dummy Processor which contains Test Src/Sink Models
#-------------------------------------------------------------------------

class DummyProc (Model):

  def __init__( self, mem_src_msgs, mem_sink_msgs, src_delay, sink_delay,
                memreq_params, memresp_params ):

    self.proc_go      = InPort( 1 )
    self.proc_status  = OutPort( 32 )

    # Memory Request Port

    self.memreq_msg  = OutPort( memreq_params.nbits )
    self.memreq_val  = OutPort( 1 )
    self.memreq_rdy  = InPort( 1 )

    # Memory Respone Port

    self.memresp_msg = InPort( memresp_params.nbits )
    self.memresp_val = InPort( 1 )
    self.memresp_rdy = OutPort( 1 )

    # Instantiate models

    self.mem_src  = pmlib.TestSource( memreq_params.nbits, mem_src_msgs,
                                      src_delay )

    self.mem_sink = pmlib.TestSink( memresp_params.nbits, mem_sink_msgs,
                                    sink_delay )
    # Connect

    connect( self.mem_src.out_msg, self.memreq_msg )
    connect( self.mem_src.out_val, self.memreq_val )
    connect( self.mem_src.out_rdy, self.memreq_rdy )

    connect( self.memresp_msg,     self.mem_sink.in_msg )
    connect( self.memresp_val,     self.mem_sink.in_val )
    connect( self.memresp_rdy,     self.mem_sink.in_rdy )

  @combinational
  def comb( self ):
    self.proc_status.value = \
        self.mem_src.done.value.uint and self.mem_sink.done.value.uint

  def line_trace( self ):
    return self.mem_src.line_trace() + " () " + self.mem_sink.line_trace()

#-------------------------------------------------------------------------
# Test harnsess
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, memreq_params, memresp_params, mem_src_msgs,
                mem_sink_msgs, src_delay, sink_delay, mem_delay,
                sparse_mem_img ):

    # Instantiate models

    s.proc     = DummyProc( mem_src_msgs, mem_sink_msgs,
                            src_delay, sink_delay,
                            memreq_params, memresp_params )

    s.mem      = TestMemory( memreq_params, memresp_params, 1,
                             mem_delay )

    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )


    # Wires

    s.procreq_val = Wire( 1 )
    s.memreq_rdy  = Wire( 1 )

    # Connect

    connect( s.proc_mgr.proc_go,     s.proc.proc_go     )
    connect( s.proc_mgr.proc_status, s.proc.proc_status )

    connect( s.proc.memreq_msg,  s.mem.memreq_msg[0] )
    connect( s.procreq_val,      s.mem.memreq_val[0] )
    connect( s.proc.memreq_rdy,  s.memreq_rdy        )

    connect( s.proc.memresp_msg, s.mem.memresp_msg[0] )
    connect( s.proc.memresp_val, s.mem.memresp_val[0] )
    connect( s.proc.memresp_rdy, s.mem.memresp_rdy[0] )

  @combinational
  def comb( s ):
    s.procreq_val.value = s.proc.memreq_val.value & s.proc_mgr.proc_go.value
    s.memreq_rdy.value  = s.mem.memreq_rdy[0].value & s.proc_mgr.proc_go.value

  def done( s ):
    return s.proc_mgr.done.value

  def line_trace( s ):
    return s.proc_mgr.line_trace() + " | " + s.proc.line_trace()

#-------------------------------------------------------------------------
# run_proc_mgr_test
#-------------------------------------------------------------------------

def run_proc_mgr_test( dump_vcd, vcd_file_name, src_delay, sink_delay,
                       mem_delay, test_msgs, sparse_mem_img ):

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  mem_src_msgs  = test_msgs[0]
  mem_sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( memreq_params, memresp_params,
                       mem_src_msgs, mem_sink_msgs,
                       src_delay, sink_delay, mem_delay,
                       sparse_mem_img )
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
# create sparse memory image
#-------------------------------------------------------------------------

def create_sparse_mem_img():

  sparse_mem_img = SparseMemoryImage()

  section_0 = [ 0x00001000, [0xff]*512 ]
  section_1 = [ 0x00010000, [0xff]*256 ]
  section_2 = [ 0x00100000, [0xff]*128 ]

  sparse_mem_img.load_section( section_0 )
  sparse_mem_img.load_section( section_1 )
  sparse_mem_img.load_section( section_2 )

  return sparse_mem_img

#-------------------------------------------------------------------------
# single port memory test messages
#-------------------------------------------------------------------------

def single_port_mem_test_msgs():

  # number of memory ports
  nports = 1

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  src_msgs  = [ [] for x in xrange( nports ) ]
  sink_msgs = [ [] for x in xrange( nports ) ]

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
  mk_req_resp( 0,   req_rd( 0x00001000, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ab ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ab ) )
  mk_req_resp( 0,   req_rd( 0x00001001, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00001001, 1, 0x000000cd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001001, 1, 0x00000000 ), resp_rd( 1, 0x000000cd ) )
  mk_req_resp( 0,   req_wr( 0x00001000, 1, 0x000000ef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00001000, 1, 0x00000000 ), resp_rd( 1, 0x000000ef ) )

  mk_req_resp( 0,   req_rd( 0x00010000, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00010000, 2, 0x0000abcd ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00010000, 2, 0x00000000 ), resp_rd( 2, 0x0000abcd ) )
  mk_req_resp( 0,   req_rd( 0x00010002, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00010002, 2, 0x0000ef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00010002, 2, 0x00000000 ), resp_rd( 2, 0x0000ef01 ) )
  mk_req_resp( 0,   req_wr( 0x00010000, 2, 0x00002345 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00010000, 2, 0x00000000 ), resp_rd( 2, 0x00002345 ) )

  mk_req_resp( 0,   req_rd( 0x00100000, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00100000, 0, 0xabcdef01 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00100000, 0, 0x00000000 ), resp_rd( 0, 0xabcdef01 ) )
  mk_req_resp( 0,   req_rd( 0x00100004, 0, 0x00000000 ), resp_rd( 0, 0xffffffff ) )
  mk_req_resp( 0,   req_wr( 0x00100004, 0, 0x23456789 ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00100004, 0, 0x00000000 ), resp_rd( 0, 0x23456789 ) )
  mk_req_resp( 0,   req_wr( 0x00100000, 0, 0xdeadbeef ), resp_wr( 0, 0x00000000 ) )
  mk_req_resp( 0,   req_rd( 0x00100000, 0, 0x00000000 ), resp_rd( 0, 0xdeadbeef ) )

  return [ src_msgs[0], sink_msgs[0] ]

#-------------------------------------------------------------------------
# TestProcManager unit test with delay = 0 x 0, mem_delay = 0
#-------------------------------------------------------------------------

def test_proc_manager_delay0x0_0( dump_vcd ):
  run_proc_mgr_test( dump_vcd, "TestProcManager_test_delay0x0_0.vcd", 0, 0, 0,
                     single_port_mem_test_msgs(), create_sparse_mem_img() )

#-------------------------------------------------------------------------
# TestProcManager unit test with delay = 0 x 0, mem_delay = 5
#-------------------------------------------------------------------------

def test_proc_manager_delay0x0_5( dump_vcd ):
  run_proc_mgr_test( dump_vcd, "TestProcManager_test_delay0x0_5.vcd", 0, 0, 5,
                     single_port_mem_test_msgs(), create_sparse_mem_img() )

#-------------------------------------------------------------------------
# TestProcManager unit test with delay = 5 x 10, mem_delay = 2
#-------------------------------------------------------------------------

def test_proc_manager_delay5x10_2( dump_vcd ):
  run_proc_mgr_test( dump_vcd, "TestProcManager_test_delay5x10_2.vcd", 5, 10, 2,
                     single_port_mem_test_msgs(), create_sparse_mem_img() )

#-------------------------------------------------------------------------
# TestProcManager unit test with delay = 10 x 5, mem_delay = 6
#-------------------------------------------------------------------------

def test_proc_manager_delay10x5_6( dump_vcd ):
  run_proc_mgr_test( dump_vcd, "TestProcManager_test_delay10x5_6.vcd", 10, 5, 6,
                     single_port_mem_test_msgs(), create_sparse_mem_img() )
