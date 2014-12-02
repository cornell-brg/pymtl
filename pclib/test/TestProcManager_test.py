#=========================================================================
# TestProcManager_test.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle
from pclib.test   import SparseMemoryImage, TestMemory, TestProcManager
from pclib.test   import TestSource, TestSink

import pclib.ifaces.mem_msgs as mem_msgs

#-------------------------------------------------------------------------
# DummyProc
#-------------------------------------------------------------------------
class DummyProc( Model ):
  """Dummy Processor which contains Test Src/Sink Models"""

  def __init__( s, mem_src_msgs, mem_sink_msgs, src_delay, sink_delay,
                memreq_params, memresp_params ):

    s.proc_go      = InPort (  1 )
    s.proc_status  = OutPort( 32 )

    # Memory Request Port

    s.memreq = OutValRdyBundle( memreq_params.nbits )

    # Memory Respone Port

    s.memresp = InValRdyBundle( memresp_params.nbits )

    # Instantiate models

    s.mem_src  = TestSource( memreq_params.nbits,  mem_src_msgs,  src_delay  )
    s.mem_sink = TestSink  ( memresp_params.nbits, mem_sink_msgs, sink_delay )

  def elaborate_logic( s ):
    s.connect( s.mem_src.out, s.memreq       )
    s.connect( s.memresp,     s.mem_sink.in_ )

    @s.combinational
    def comb():
      s.proc_status.value = \
        s.mem_src.done and s.mem_sink.done

  def line_trace( s ):
    return s.mem_src.line_trace() + " () " + s.mem_sink.line_trace()

#-------------------------------------------------------------------------
# TestHarness
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
                             mem_delay, mem_nbytes = 2**24 )

    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )


    # Wires

    s.procreq_val = Wire( 1 )
    s.memreq_rdy  = Wire( 1 )

  def elaborate_logic( s ):
    # Connect

    s.connect( s.proc_mgr.proc_go,     s.proc.proc_go     )
    s.connect( s.proc_mgr.proc_status, s.proc.proc_status )

    s.connect( s.proc.memreq.msg,  s.mem.reqs[0].msg )
    s.connect( s.procreq_val,      s.mem.reqs[0].val )
    s.connect( s.proc.memreq.rdy,  s.memreq_rdy        )

    s.connect( s.proc.memresp, s.mem.resps[0] )

    @s.combinational
    def comb():
      s.procreq_val.value = s.proc.memreq.val & \
                                s.proc_mgr.proc_go
      s.memreq_rdy.value  = s.mem.reqs[0].rdy & \
                                s.proc_mgr.proc_go.value

  def done( s ):
    return s.proc_mgr.done

  def line_trace( s ):
    return s.proc_mgr.line_trace() + " | " + s.proc.line_trace()

#-------------------------------------------------------------------------
# run_proc_mgr_test
#-------------------------------------------------------------------------

def run_proc_mgr_test( dump_vcd, src_delay, sink_delay,
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
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

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

  label_0 = [ 0x00001000, [0xff]*512 ]
  label_1 = [ 0x00010000, [0xff]*256 ]
  label_2 = [ 0x00100000, [0xff]*128 ]

  sparse_mem_img.load_label( label_0 )
  sparse_mem_img.load_label( label_1 )
  sparse_mem_img.load_label( label_2 )

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
@pytest.mark.parametrize('src_delay,sink_delay,mem_delay', [
  ( 0,  0, 0),
  ( 0,  0, 5),
  ( 5, 10, 2),
  (10,  5, 6),
])
def test_proc_manager_delay0x0_0( dump_vcd, src_delay, sink_delay, mem_delay ):
  run_proc_mgr_test( dump_vcd, src_delay, sink_delay, mem_delay,
                     single_port_mem_test_msgs(), create_sparse_mem_img() )
