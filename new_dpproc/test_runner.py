#=======================================================================
# test_runner.py
#=======================================================================

from new_pymtl import *
from new_pmlib import SparseMemoryImage
from new_pmlib import TestMemory
from new_pmlib import mem_msgs

from new_pmlib.TestProcManager import TestProcManager
from ParcProc5stStall          import ParcProc5stStall
from ParcProc5stBypass         import ParcProc5stBypass

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, ModelType, memreq_params, memresp_params,
                mem_delay, sparse_mem_img, test_verilog ):

    s.proc     = ModelType( reset_vector=0x00000400 )
    s.mem      = TestMemory( memreq_params, memresp_params, 2,
                             mem_delay, mem_nbytes=2**24  )
    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )

    if test_verilog:
      s.proc = get_verilated( s.proc )

  def elaborate_logic( s ):

    # Connect Manager Signals

    s.connect( s.proc_mgr.proc_go,     s.proc.go         )
    s.connect( s.proc_mgr.proc_status, s.proc.status     )

    # Instruction Memory Request/Response Signals

    s.connect( s.proc.imemreq,  s.mem.reqs[0]  )
    s.connect( s.proc.imemresp, s.mem.resps[0] )

    # Data Memory Request/Response Signals

    s.connect( s.proc.dmemreq,  s.mem.reqs[1]  )
    s.connect( s.proc.dmemresp, s.mem.resps[1] )

  #---------------------------------------------------------------------
  # done
  #---------------------------------------------------------------------
  def done( s ):
    return s.proc_mgr.done.value

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    return s.proc_mgr.line_trace() + \
           s.proc.line_trace() + \
           s.mem.line_trace()

#-----------------------------------------------------------------------
# run_proc_test
#-----------------------------------------------------------------------
# function to drive the unit tests
def run_proc_test( ModelType, test_verilog, dump_vcd, vcd_file, input_list ):

  # Instantiate and elaborate the model

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  # input_list parameters

  mem_delay       = input_list[0]
  sparse_mem_img  = input_list[1]
  expected_result = input_list[2]

  # Instantiate and elaborate test harness model

  model = TestHarness( ModelType, memreq_params, memresp_params,
                       mem_delay, sparse_mem_img, test_verilog )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 3000:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()
  assert model.proc.status.value.uint() == expected_result

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-----------------------------------------------------------------------
# run_stall_proc_test
#-----------------------------------------------------------------------
def run_stall_proc_test( dump_vcd, test_verilog, vcd_file_name, input_list ):
  run_proc_test( ParcProc5stStall, test_verilog,
                 dump_vcd, vcd_file_name, input_list )

#-----------------------------------------------------------------------
# run_bypass_proc_test
#-----------------------------------------------------------------------
def run_bypass_proc_test( dump_vcd, test_verilog, vcd_file_name, input_list ):
  run_proc_test( ParcProc5stBypass, test_verilog,
                 dump_vcd, vcd_file_name, input_list )
