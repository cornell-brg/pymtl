#==============================================================================
# MVMultFunc_test
#==============================================================================

from new_pymtl  import *
from new_pmlib  import TestMemory, mem_msgs
from MVMultFunc import MVMultFunc

import pytest

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, mem_delay ):

    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    memresp_params = mem_msgs.MemRespParams( 32 )

    s.mem   = TestMemory ( memreq_params, memresp_params, 1, mem_delay )
    s.accel = MVMultFunc ( memreq_params, memresp_params )

  def elaborate_logic( s ):
    s.connect( s.accel.req , s.mem.reqs [0]  )
    s.connect( s.accel.resp, s.mem.resps[0]  )

  def done( s ):
    return s.accel.done

  def line_trace( s ):
    return "{} -> {}".format( s.accel.line_trace(), s.mem.line_trace() )

#------------------------------------------------------------------------------
# run_mvmult_test
#------------------------------------------------------------------------------
def run_mvmult_test( dump_vcd, test_verilog, vcd_file_name, mem_delay,
                     src_matrix, src_vector, dest_vector ):

  model = TestHarness( mem_delay )
  model.elaborate()

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Load the memory

  model.mem.load_memory( src_matrix  )
  model.mem.load_memory( src_vector  )
  model.mem.load_memory( dest_vector )

  # Run the simulation

  sim.reset()

  # Set the inputs
  model.accel.m_baseaddr.value = src_matrix [0]
  model.accel.v_baseaddr.value = src_vector [0]
  model.accel.d_baseaddr.value = dest_vector[0]
  model.accel.size      .value = len(src_vector[1]) / 4

  sim.cycle()

  model.accel.go.value = True

  print
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  dest_addr  = dest_vector[0]
  dest_value = dest_vector[1][0]
  assert model.mem.mem.mem[ dest_addr ] == dest_value

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()


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
  ('mem_delay'), [0,5]
)
def test_mvmult_row1( dump_vcd, mem_delay ):
  run_mvmult_test( dump_vcd, False, "MVMult.vcd", mem_delay,
                   mem_array_32bit(  0, [ 5, 1 ,3, 1, 1 ,1, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [16, 6, 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_row3( dump_vcd, mem_delay ):
  run_mvmult_test( dump_vcd, False, "MVMult.vcd", mem_delay,
                   mem_array_32bit(  0, [ 1, 2, 1] ),
                   mem_array_32bit( 12, [ 1, 2, 3] ),
                   mem_array_32bit( 24, [ 8 ]),
                 )
