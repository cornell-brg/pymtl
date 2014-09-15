#==============================================================================
# MatrixVecLaneBL_test
#==============================================================================

from new_pymtl        import *
from new_pmlib        import TestSource, TestMemory, mem_msgs
from DotProductRTL import DotProduct

import pytest

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, lane_id, nmul_stages, mem_delay, test_verilog ):


    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    memresp_params = mem_msgs.MemRespParams( 32 )

    s.mem  = TestMemory( memreq_params, memresp_params, 1, mem_delay )
    s.lane = DotProduct( nmul_stages )

    if test_verilog:
      s.lane = get_verilated( s.lane )

  def elaborate_logic( s ):
    s.connect( s.lane.req , s.mem.reqs [0] )
    s.connect( s.lane.resp, s.mem.resps[0] )

  def done( s ):
    return s.lane.to_cpu.val

  def line_trace( s ):
    return "{} -> {}".format( s.lane.line_trace(), s.mem.line_trace() )

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

  sim.cycle()
  model.lane.from_cpu.val.value = 1
  model.lane.from_cpu.msg[0:32] = size
  model.lane.from_cpu.msg[32:37] = 1

  sim.cycle()
  model.lane.from_cpu.val.value = 1
  model.lane.from_cpu.msg[0:32] = m_baseaddr
  model.lane.from_cpu.msg[32:37] = 2

  sim.cycle()
  model.lane.from_cpu.val.value = 1
  model.lane.from_cpu.msg[0:32] = v_baseaddr
  model.lane.from_cpu.msg[32:37] = 3

  sim.cycle()
  model.lane.from_cpu.val.value = 1
  model.lane.from_cpu.msg[0:32] = go
  model.lane.from_cpu.msg[32:37] = 0

  while not model.done() and sim.ncycles < 100:
    sim.print_line_trace()
    sim.cycle()
    model.lane.from_cpu.val.value = 0
  sim.print_line_trace()
  assert model.done()


  assert exp_value == model.lane.to_cpu.msg

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
def test_dotproduct2( dump_vcd, test_verilog, mem_delay, nmul_stages ):
  lane = 0
  run_mvmult_test( dump_vcd, "DP.vcd",
                   TestHarness( lane, nmul_stages, mem_delay, test_verilog ),
                   lane,
                   # NOTE: C++ has dummy data between rows when you have array**!
                   mem_array_32bit(  0, [ 5, 1 ,3, 9, 10 ]),
                   mem_array_32bit( 80, [ 1, 2, 3, 9, 0 ]),
                   16+81,
                 )