#==============================================================================
# MatrixVecLaneFL_test
#==============================================================================

import pytest

from pymtl        import *
from pclib.ifaces import mem_msgs
from pclib.test   import TestSource, TestMemory

from MatrixVecLaneFL import MatrixVecLaneFL
from LaneManager     import LaneManager

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, lane_id, mem_delay ):

    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    memresp_params = mem_msgs.MemRespParams( 32 )

    s.mem  = TestMemory( memreq_params, memresp_params, 1, mem_delay )
    s.lane = MatrixVecLaneFL( lane_id, memreq_params, memresp_params )

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
def run_mvmult_test( dump_vcd, test_verilog, vcd_file_name, model, lane_id,
                     src_matrix, src_vector, dest_vector ):

  model.elaborate()

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Load the memory

  model.mem.load_memory( src_matrix  )
  model.mem.load_memory( src_vector  )

  # Run the simulation

  sim.reset()

  # Set the inputs
  print src_matrix[0]
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
    model.lane.go.value = False

  dest_addr  = dest_vector[0]
  dest_value = dest_vector[1][0]
  assert model.mem.mem.mem[ dest_addr+(lane_id*4) ] == dest_value

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
  ('mem_delay'), [0,5]
)
def test_mvmult_lane0_row0( dump_vcd, mem_delay ):
  lane = 0
  run_mvmult_test( dump_vcd, False, get_vcd_filename(),
                   TestHarness( lane, mem_delay ), lane,
                   mem_array_32bit(  0, [ 5, 1 ,3, 99, 1, 1 ,1, 99, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [16, 6, 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_lane0_row2( dump_vcd, mem_delay ):
  lane = 0
  run_mvmult_test( dump_vcd, False, get_vcd_filename(),
                   TestHarness( lane, mem_delay ), lane,
                   mem_array_32bit(  0, [ 1, 2, 1] ),
                   mem_array_32bit( 12, [ 1, 2, 3] ),
                   mem_array_32bit( 24, [ 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_lane2_row0( dump_vcd, mem_delay ):
  lane = 2
  run_mvmult_test( dump_vcd, False, get_vcd_filename(),
                   TestHarness( lane, mem_delay ), lane,
                   mem_array_32bit(  0, [ 5, 1 ,3, 99, 1, 1 ,1, 99, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [ 8 ]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_mvmult_lane1_row0( dump_vcd, mem_delay ):
  lane = 1
  run_mvmult_test( dump_vcd, False, get_vcd_filename(),
                   TestHarness( lane, mem_delay ), lane,
                   mem_array_32bit(  0, [ 5, 1 ,3, 99, 1, 1 ,1, 99, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [ 6 ]),
                 )

#------------------------------------------------------------------------------
# LaneManagerHarness
#------------------------------------------------------------------------------
class LaneManagerHarness( Model ):

  def __init__( s, nlanes, mem_delay, src_delay, config_msgs ):

    memreq_params  = mem_msgs.MemReqParams( 32, 32 )
    memresp_params = mem_msgs.MemRespParams( 32 )

    s.src   = TestSource( 5 + 32, config_msgs, src_delay )
    s.mgr   = LaneManager( nlanes )
    s.lane  = [ MatrixVecLaneFL( x, memreq_params, memresp_params )
                for x in range( nlanes ) ]
    s.mem   = TestMemory( memreq_params, memresp_params, nlanes, mem_delay )

    assert nlanes > 0
    s.nlanes = nlanes

  def elaborate_logic( s ):

    for i in range( s.nlanes ):
      s.connect( s.src.out,      s.mgr.from_cpu       )

      s.connect( s.mgr.size,     s.lane[i].size       )
      s.connect( s.mgr.r_baddr,  s.lane[i].m_baseaddr )
      s.connect( s.mgr.v_baddr,  s.lane[i].v_baseaddr )
      s.connect( s.mgr.d_baddr,  s.lane[i].d_baseaddr )
      s.connect( s.mgr.go,       s.lane[i].go         )
      s.connect( s.mgr.done[i],  s.lane[i].done       )

      s.connect( s.lane[i].req , s.mem.reqs [i]  )
      s.connect( s.lane[i].resp, s.mem.resps[i]  )

  def done( s ):
    return reduce( lambda x, y : x & y, [x.done for x in s.lane ] )

  def line_trace( s ):
    #return "{} -> {}".format( s.accel.line_trace(), s.mem.line_trace() )
    return "{} () {}".format( s.mgr.line_trace(), s.mem.line_trace() )

#------------------------------------------------------------------------------
# run_lane_managed_test
#------------------------------------------------------------------------------
def run_lane_managed_test( dump_vcd, test_verilog, vcd_file_name, model,
                           src_matrix, src_vector, dest_vector ):

  model.elaborate()

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Load the memory

  model.mem.load_memory( src_matrix  )
  model.mem.load_memory( src_vector  )
  #model.mem.load_memory( dest_vector )

  # Run the simulation

  sim.reset()

  print
  while not model.done() and sim.ncycles < 80:
    sim.print_line_trace()
    sim.cycle()

  dest_addr   = dest_vector[0]
  for i, dest_value in enumerate( dest_vector[1] ):
    assert model.mem.mem.mem[ dest_addr+i ] == dest_value

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#------------------------------------------------------------------------------
# config_msg
#------------------------------------------------------------------------------
# Utility method for creating config messages
def config_msg( addr, value ):
  return concat( Bits(3, addr), Bits(32, value) )


@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_managed_1lane( dump_vcd, mem_delay ):
  run_lane_managed_test( dump_vcd, False, get_vcd_filename(),
                  LaneManagerHarness( 1, mem_delay, 0,
                     [ config_msg( 1,   3), # size
                       config_msg( 2,   0), # r_addr
                       config_msg( 3,  80), # v_addr
                       config_msg( 4, 160), # d_addr
                       config_msg( 0,   1), # go
                     ]
                   ),
                   mem_array_32bit(  0, [ 5, 1 ,3, 99, 1, 1 ,1, 99, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [16]),
                 )

@pytest.mark.parametrize(
  ('mem_delay'), [0,5]
)
def test_managed_3lane( dump_vcd, mem_delay ):
  run_lane_managed_test( dump_vcd, False, get_vcd_filename(),
                  LaneManagerHarness( 3, mem_delay, 0,
                     [ config_msg( 1,   3), # size
                       config_msg( 2,   0), # r_addr
                       config_msg( 3,  80), # v_addr
                       config_msg( 4, 160), # d_addr
                       config_msg( 0,   1), # go
                     ]
                   ),
                   mem_array_32bit(  0, [ 5, 1 ,3, 99, 1, 1 ,1, 99, 1, 2 ,1] ),
                   mem_array_32bit( 80, [ 1, 2, 3 ]),
                   mem_array_32bit(160, [16, 6, 8 ]),
                 )
