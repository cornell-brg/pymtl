#==============================================================================
# MatrixVecMultLaneBL_test
#==============================================================================

from new_pymtl           import *
from new_pmlib           import TestMemory, mem_msgs
from MatrixVecMultLaneBL import MatrixVecMultLaneBL

import pytest

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, lane_id, mem_delay ):

    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    memresp_params = mem_msgs.MemRespParams( 32 )

    s.mem  = TestMemory( memreq_params, memresp_params, 1, mem_delay )
    s.lane = MatrixVecMultLaneBL( lane_id, memreq_params, memresp_params )

  def elaborate_logic( s ):
    s.connect( s.lane.req , s.mem.reqs [0]  )
    s.connect( s.lane.resp, s.mem.resps[0]  )

  def done( s ):
    return s.lane.done

  def line_trace( s ):
    return "{} -> {}".format( s.lane.line_trace(), s.mem.line_trace() )

#------------------------------------------------------------------------------
# run_mvmult_test
#------------------------------------------------------------------------------
def run_mvmult_test( dump_vcd, test_verilog, vcd_file_name, model,
                     src_matrix, src_vector, dest_vector ):

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
  model.lane.m_baseaddr.value = src_matrix [0]
  model.lane.v_baseaddr.value = src_vector [0]
  model.lane.d_baseaddr.value = dest_vector[0]
  model.lane.size      .value = len(src_vector[1]) / 4

  sim.cycle()

  model.lane.go.value = True

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
def test_mvmult_lane0_row0( dump_vcd, mem_delay ):
  run_mvmult_test( dump_vcd, False, "MVMult.vcd",
                   TestHarness( 0, mem_delay ),
                   mem_array_32bit(  0, [ 5, 1 ,3, 1, 1 ,1, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [16, 6, 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_lane0_row2( dump_vcd, mem_delay ):
  run_mvmult_test( dump_vcd, False, "MVMult.vcd",
                   TestHarness( 0, mem_delay ),
                   mem_array_32bit(  0, [ 1, 2, 1] ),
                   mem_array_32bit( 12, [ 1, 2, 3] ),
                   mem_array_32bit( 24, [ 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_lane1_row0( dump_vcd, mem_delay ):
  run_mvmult_test( dump_vcd, False, "MVMult.vcd",
                   TestHarness( 1, mem_delay ),
                   mem_array_32bit(  0, [ 5, 1 ,3, 1, 1 ,1, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [ 6, 8 ]),
                 )

##------------------------------------------------------------------------------
## LaneManagerHarness
##------------------------------------------------------------------------------
#class LaneManagerHarness( Model ):
#
#  def __init__( s, nlanes, mem_delay ):
#
#    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
#    memresp_params = mem_msgs.MemRespParams( 32 )
#
#    s.mgr   = LaneManager( nlanes )
#    s.lane  = [ MatrixVecMultLaneBL ( memreq_params, memresp_params )
#                for x in range( nlanes ) ]
#    s.mem   = TestMemory ( memreq_params, memresp_params, nlanes, mem_delay )
#
#    s.nlanes = nlanes
#
#  def elaborate_logic( s ):
#
#    for i in range( s.nlanes ):
#      s.connect( s.mgr.size,     s.lane[i].size    )
#      s.connect( s.mgr.r_baddr,  s.lane[i].r_baddr )
#      s.connect( s.mgr.v_baddr,  s.lane[i].v_baddr )
#      s.connect( s.mgr.d_baddr,  s.lane[i].d_baddr )
#      s.connect( s.mgr.go,       s.lane[i].go      )
#      s.connect( s.mgr.done[i],  s.lane[i].done    )
#
#      s.connect( s.lane[i].req , s.mem.reqs [i]  )
#      s.connect( s.lane[i].resp, s.mem.resps[i]  )
#
#  def done( s ):
#    return reduce( lambda x, y : x & y, [x.done for x in s.accel ] )
#
#  def line_trace( s ):
#    #return "{} -> {}".format( s.accel.line_trace(), s.mem.line_trace() )
#    return "{} -> {}".format( s.mem.line_trace() )
