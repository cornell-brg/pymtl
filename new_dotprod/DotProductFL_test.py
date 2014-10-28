#==============================================================================
# DotProductFL_test
#==============================================================================
# TODO: clean this up!!!

from pymtl        import *
from new_pmlib        import TestSource, TestMemory, mem_msgs
from DotProductFL     import DotProductFL as DotProduct
from new_pmlib        import MemMsg
from new_pmlib        import CP2Msg

import pytest

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, lane_id, nmul_stages, mem_delay, test_verilog ):


    s.memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    s.memresp_params = mem_msgs.MemRespParams( 32 )

    s.mem  = TestMemory( s.memreq_params, s.memresp_params, 1, mem_delay )
    mem_ifc = MemMsg   ( 32, 32)
    cpu_ifc = CP2Msg   ( 5, 32 )

    s.lane = DotProduct(mem_ifc, cpu_ifc )

    if test_verilog:
      s.lane = get_verilated( s.lane )


  def elaborate_logic( s ):
    s.mem_req =  Wire( s.memreq_params.nbits  )
    s.mem_resp = Wire( s.memresp_params.nbits )

    @s.combinational
    def connect_structs():
      s.mem_req.value = s.lane.mem_ifc.req_msg
      s.mem.reqs[0].msg.value = s.memreq_params.mk_req(
        s.lane.mem_ifc.req_msg.type,
        s.lane.mem_ifc.req_msg.addr,
        s.lane.mem_ifc.req_msg.len,
        s.lane.mem_ifc.req_msg.data)

      s.mem_resp.value = s.mem.resps[0].msg
      #print "RESP", s.mem.resps[0].msg[s.memresp_params.data_slice]
      tup = s.memresp_params.unpck_resp(s.mem_resp)
      #print "REQ ", s.mem.reqs[0].msg[s.memreq_params.addr_slice], s.lane.mem_ifc.req_msg.addr
      s.lane.mem_ifc.resp_msg.type.value = tup[0]
      s.lane.mem_ifc.resp_msg.len.value = tup[1]
      s.lane.mem_ifc.resp_msg.data.value = tup[2]

      s.mem.reqs[0].val.value = s.lane.mem_ifc.req_val
      s.lane.mem_ifc.req_rdy.value = s.mem.reqs[0].rdy

      s.mem.resps[0].rdy.value =  s.lane.mem_ifc.resp_rdy
      s.lane.mem_ifc.resp_val.value = s.mem.resps[0].val



  def done( s ):
    return s.lane.cpu_ifc.resp_val

  #def line_trace( s ):
  #  return "{} -> {}".format( s.lane.line_trace(), s.mem.line_trace() )

#------------------------------------------------------------------------------
# run_mvmult_test
#------------------------------------------------------------------------------
def run_mvmult_test( dump_vcd, vcd_file_name, model, lane_id,
                     src_matrix, src_vector, exp_value):

  model.elaborate()

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Load the memory

  model.mem.load_memory( src_matrix )
  model.mem.load_memory( src_vector )

  # Run the simulation

  sim.reset()

  # Set the inputs
  m_baseaddr = src_matrix [0]
  v_baseaddr = src_vector [0]
  size = len(src_vector[1]) / 4
  go = True

  sim.print_line_trace()
  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc.req_val.next = 1
  model.lane.cpu_ifc.req_msg.data.next = size
  model.lane.cpu_ifc.req_msg.ctrl_msg.next = 1
  #print model.lane.cpu_ifc.req_msg.addr

  sim.print_line_trace()
  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc.req_val.next = 1
  model.lane.cpu_ifc.req_msg.data.next = m_baseaddr
  model.lane.cpu_ifc.req_msg.ctrl_msg.next = 2
  #print model.lane.cpu_ifc.req_msg.addr

  sim.print_line_trace()
  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc.req_val.next = 1
  model.lane.cpu_ifc.req_msg.data.next = v_baseaddr
  model.lane.cpu_ifc.req_msg.ctrl_msg.next = 3

  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc.req_val.next = 1
  model.lane.cpu_ifc.req_msg.data.next = True
  model.lane.cpu_ifc.req_msg.ctrl_msg.next = 0
  #print model.lane.cpu_ifc.req_msg.addr

  while not model.done() and sim.ncycles < 300:
    sim.print_line_trace()
    sim.cycle()
    model.lane.cpu_ifc.req_val.next = 0
  sim.print_line_trace()
  assert model.done()


  assert exp_value == model.lane.cpu_ifc.resp_msg

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()


#------------------------------------------------------------------------------
# mem_array_32bit
#------------------------------------------------------------------------------
# Utility function for creating arrays formatted for memory loading.
from itertools import chain
def mem_array_32bit( base_addr, data ):
  return [base_addr,
          list( chain.from_iterable([ [x,0,0,0] for x in data ] ))
         ]

#------------------------------------------------------------------------------
# test_mvmult
#------------------------------------------------------------------------------
#  5 1 3   1    16
#  1 1 1 . 2  =  6
#  1 2 1   3     8
#
@pytest.mark.parametrize(
  ('mem_delay','nmul_stages'), [(0,1),(0,4),(5,1),(5,4)]
)
def test_dotproduct( dump_vcd, test_verilog, mem_delay, nmul_stages ):
  lane = 0
  run_mvmult_test( dump_vcd, "DP.vcd",
                   TestHarness( lane, nmul_stages, mem_delay, test_verilog ),
                   lane,
                   # NOTE: C++ has dummy data between rows when you have array**!
                   mem_array_32bit(  0, [ 5, 1 ,3 ]),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   16,
                 )

@pytest.mark.parametrize(
  ('mem_delay','nmul_stages'), [(0,1),(0,4),(5,1),(5,4)]
)
def test_2dotprod( dump_vcd, test_verilog, mem_delay, nmul_stages ):
  lane = 0
  run_mvmult_test( dump_vcd, "DP.vcd",
                   TestHarness( lane, nmul_stages, mem_delay, test_verilog ),
                   lane,
                   # NOTE: C++ has dummy data between rows when you have array**!
                   mem_array_32bit(  0, [ 5, 1 ,3, 9, 10 ]),
                   mem_array_32bit( 80, [ 1, 2, 3, 9, 0 ]),
                   16+81,
                 )
