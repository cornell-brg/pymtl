#=======================================================================
# DummyCOP_test.py
#=======================================================================

from pymtl import *
from new_pmlib import TestVectorSimulator
from DummyCOP  import DummyCOPCL
from new_pmlib import mem_msgs, TestMemory, TestProcManager
from new_pmlib import SparseMemoryImage
from new_proc  import ParcProc5stBypass

#-----------------------------------------------------------------------
# test_DummyCOP_directed
#-----------------------------------------------------------------------
def test_DummyCOP_directed( dump_vcd ):

  # Select and elaborate the model under test

  model = DummyCOPCL()
  model.elaborate()

  data_nbits = 32

  # Define test input and output functions

  def tv_in( model, test_vector ):
    model.from_cpu.val     .value = test_vector[0]
    model.from_cpu.msg[32:].value = test_vector[1]
    model.from_cpu.msg[:32].value = test_vector[2]

  def tv_out( model, test_vector ):
    assert model.from_cpu.rdy == test_vector[3]
    assert model.to_cpu       == test_vector[4]
    assert model.result       == test_vector[5]

  # Define the test vectors
  test_vectors = [
    # Inputs--------  Outputs------------------------------------
    # val addr data   rdy done result
    [ 0,  1,   99,    1,  0,   0 ],
    [ 0,  0,   99,    1,  0,   0 ],
    [ 1,  1,    7,    1,  0,   0 ],
    [ 1,  1,    6,    1,  0,   0 ],
    [ 1,  2,    2,    1,  0,   0 ],
    [ 1,  0,    1,    1,  0,   0 ],
    [ 0,  0,   99,    0,  0,   0 ],
    [ 0,  0,   99,    0,  1,   8 ],
    [ 0,  0,   99,    1,  0,   8 ],
    [ 1,  2,   10,    1,  0,   8 ],
    [ 0,  0,   99,    1,  0,   8 ],
    [ 1,  0,    1,    1,  0,   8 ],
    [ 1,  0,    2,    0,  0,   8 ],
    [ 0,  0,   99,    0,  1,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
  ]

  # Create the simulator and configure it
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "LaneManagerOneLane.vcd" )

  # Run the simulator
  sim.run_test()

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, ModelType, memreq_params, memresp_params,
                   mem_delay, sparse_mem_img, test_verilog ):

    s.proc     = ParcProc5stBypass( reset_vector=0x00000400 )
    s.cp2      = DummyCOPCL()
    s.mem      = TestMemory( memreq_params, memresp_params, 2,
                             mem_delay, mem_nbytes=2**24  )
    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )


  def elaborate_logic( s ):

    # Connect Manager Signals

    s.connect( s.proc_mgr.proc_go,     s.proc.go         )
    s.connect( s.proc_mgr.proc_status, s.proc.status     )

    # Memory Request/Response Signals

    s.connect( s.proc.imemreq , s.mem.reqs [0] )
    s.connect( s.proc.imemresp, s.mem.resps[0] )
    s.connect( s.proc.dmemreq , s.mem.reqs [1] )
    s.connect( s.proc.dmemresp, s.mem.resps[1] )

    # Accelerator Signals
    s.connect( s.proc.to_cp2,   s.cp2.from_cpu )
    s.connect( s.proc.from_cp2, s.cp2.to_cpu  )

  #---------------------------------------------------------------------
  # done
  #---------------------------------------------------------------------
  def done( s ):
    return s.proc_mgr.done

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    #return s.proc.line_trace() + s.mem.line_trace()
    return s.proc.line_trace() + s.cp2.line_trace()

#-----------------------------------------------------------------------
# run_proc_test
#-----------------------------------------------------------------------
# function to drive the unit tests
def run_proc_test( dump_vcd, test_verilog, vcd_file, input_list ):

  # Instantiate and elaborate the model

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  # input_list parameters

  mem_delay       = input_list[0]
  sparse_mem_img  = input_list[1]
  expected_status = input_list[2]
  expected_result = input_list[3]

  # Instantiate and elaborate test harness model

  model = TestHarness( None, memreq_params, memresp_params,
                       mem_delay, sparse_mem_img, test_verilog )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 300:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()
  assert model.proc.status == expected_status
  assert model.cp2 .result == expected_result

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-----------------------------------------------------------------------
# test_dummy_addiu_no_hazards
#-----------------------------------------------------------------------
from new_proc.parcv1_addiu import addiu_no_hazards
@requires_xcc
def test_dummy_addiu_no_hazards( dump_vcd, test_verilog ):
  run_proc_test( dump_vcd, test_verilog, "bypass_addiu_no_hazards.vcd",
                 addiu_no_hazards()+[0] )

#-----------------------------------------------------------------------
# mtc2 assembly
#-----------------------------------------------------------------------
def mtc2_no_hazards():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      li    $6, 4
      li    $1, 1
      nop
      nop
      nop
      mtc2  $6, $1
      mtc2  $6, $2
      mtc2  $1, $0
      mtc0  $1, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_status = 1
  expected_result = 8

  return [ mem_delay, sparse_mem_img, expected_status, expected_result ]

#-----------------------------------------------------------------------
# run mtc2 tests
#-----------------------------------------------------------------------
@requires_xcc
def test_dummy_mtc2_no_hazards( dump_vcd, test_verilog ):
  run_proc_test( dump_vcd, test_verilog, "mtc2_no_hazards.vcd",
                 mtc2_no_hazards() )

