#=========================================================================
# Tile_test.py
#=========================================================================
# ParcProc5stBypass assembly tests driver

from pymtl        import *
from pclib.test   import TestMemory, TestProcManager, SparseMemoryImage
from pclib.ifaces import mem_msgs

from Tile import Tile

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, ModelType, memreq_params, memresp_params,
                mem_delay, sparse_mem_img, test_verilog ):

    data_nbits = memreq_params.data_nbits
    s.tile     = ModelType( reset_vector   = 0x00000400,
                            mem_data_nbits = data_nbits )
    s.mem      = TestMemory( memreq_params, memresp_params, 2,
                             mem_delay, mem_nbytes=2**24  )
    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )

    if test_verilog:
      s.tile = get_verilated( s.tile )

  def elaborate_logic( s ):

    # Connect Manager Signals

    s.connect( s.proc_mgr.proc_go,     s.tile.go         )
    s.connect( s.proc_mgr.proc_status, s.tile.status     )

    # Memory Request/Response Signals

    s.connect( s.tile.memreq [0], s.mem.reqs [0] )
    s.connect( s.tile.memresp[0], s.mem.resps[0] )
    s.connect( s.tile.memreq [1], s.mem.reqs [1] )
    s.connect( s.tile.memresp[1], s.mem.resps[1] )

  def cleanup( s ):
    del s.mem.mem.mem[:]

  #---------------------------------------------------------------------
  # done
  #---------------------------------------------------------------------
  def done( s ):
    return s.proc_mgr.done

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    return s.proc_mgr.line_trace() + \
           s.tile.line_trace() #+ \
           #s.mem.line_trace()

#-----------------------------------------------------------------------
# run_proc_test
#-----------------------------------------------------------------------
# function to drive the unit tests
def run_proc_test( ModelType, test_verilog, dump_vcd, vcd_file, input_list ):

  # Instantiate and elaborate the model

  #memreq_params  = mem_msgs.MemReqParams( 32, 128 )
  #memresp_params = mem_msgs.MemRespParams( 128 )
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
  while not model.done() and sim.ncycles < 4000:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()
  assert model.tile.status == expected_result

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  model.cleanup()

#-----------------------------------------------------------------------
# run_bypass_proc_test
#-----------------------------------------------------------------------
def run_bypass_proc_test( dump_vcd, test_verilog, vcd_file_name, input_list ):
  run_proc_test( Tile, test_verilog,
                 dump_vcd, vcd_file_name, input_list )

#---------------------------------------------------------------------------
# X. mtc2 tests - matrix vector multiplier specific
#---------------------------------------------------------------------------

test_start = """
  .text;
  .align  4;
  .global _test;
  .ent    _test;
  _test:
"""

test_end   = """
  .end    _test;
"""

def mtc2_1x1():

  asm_str = \
    ( test_start +
  """
      li    $1, 1
      la    $2, matrix
      la    $3, vector
      la    $4, dest
      li    $5, 1
      nop
      nop
      nop
      mtc2  $1, $1
      mtc2  $2, $2
      mtc2  $3, $3
      mtc2  $4, $4
      mtc2  $5, $0
      nop
      nop
      nop
      mfc2  $17, $6
      mtc0  $6, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      matrix:  .word 0x00000004
      vector:  .word 0x00000002
      dest:    .word 0x00000000
  """ )

  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 8

  return [ sparse_mem_img, expected_result ]

@requires_xcc
def test_mtc2_1x1_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_mtc2_1x1.vcd",
                        [0]+mtc2_1x1() )
@requires_xcc
def test_mtc2_1x1_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_mtc2_1x1.vcd",
                        [5]+mtc2_1x1() )

def mtc2_3x3():

  asm_str = \
    ( test_start +
  """
      li    $1, 3
      la    $2, matrix0
      la    $3, vector0
      la    $4, dest0
      li    $5, 1
      mtc2  $1, $1
      mtc2  $2, $2
      mtc2  $3, $3
      mtc2  $4, $4
      mtc2  $5, $0
      la    $2, matrix3
      la    $7, dest1
      mfc2  $16, $16
      mtc2  $2, $2
      mtc2  $7, $4
      mtc2  $5, $0
      la    $2, matrix6
      la    $8, dest2
      mfc2  $17, $17
      mtc2  $2, $2
      mtc2  $8, $4
      mtc2  $5, $0
      mfc2  $18, $18
      addu  $6, $16, $17
      addu  $6, $6, $18
      mtc0  $6, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      matrix0: .word 0x00000005
      matrix1: .word 0x00000001
      matrix2: .word 0x00000003
      matrix3: .word 0x00000001
      matrix4: .word 0x00000001
      matrix5: .word 0x00000001
      matrix6: .word 0x00000001
      matrix7: .word 0x00000002
      matrix8: .word 0x00000001
      vector0: .word 0x00000001
      vector1: .word 0x00000002
      vector2: .word 0x00000003
      dest0:   .word 0x00000000
      dest1:   .word 0x00000000
      dest2:   .word 0x00000000
  """ )

  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 30

  return [ sparse_mem_img, expected_result ]

@requires_xcc
def test_mtc2_3x3_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_mtc2_3x3.vcd",
                        [0]+mtc2_3x3() )
@requires_xcc
def test_mtc2_3x3_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_mtc2_3x3.vcd",
                        [5]+mtc2_3x3() )


def j_after_ld_stall():

  asm_str = \
    ( test_start +
  """
      li    $5, 0
      la    $2, val0
      nop; nop; nop; nop; nop;
      lw    $3, 0($2)
      addiu $4, $4, 1
      j     1f
      nop; nop; nop; nop;
      nop; nop; nop; nop;
   1: addiu $5, $5, 1
      mtc0  $5, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
      mtc0  $4, $1
  """
    + test_end +
  """
   .data
   .align 4
      val0: .word 0x00000005
  """ )

  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 1

  return [ sparse_mem_img, expected_result ]

@requires_xcc
def test_j_after_ld_stall( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_j_after_ld_stall.vcd",
                        [0]+j_after_ld_stall() )

def mul_scoreboard_clear_bug():

  asm_str = \
    ( test_start +
  """
      la    $1, val1
      li    $2, 2
      li    $3, 3
      nop; nop; nop; nop;
      lw   $11,  0($1)
      lw   $11, 16($1)
      mul   $3, $2, $3
      nop; nop; nop; nop;
      nop; nop; nop; nop;
      mul  $12,  $3, $2
      mtc0 $12,  $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
      mtc0  $2, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      val1: .word 0x00000001
      val2: .word 0x00000002
      val3: .word 0x00000003
      val4: .word 0x00000004
      val5: .word 0x00000005
      val6: .word 0x00000006
      val7: .word 0x00000007
      val8: .word 0x00000008
      val9: .word 0x00000009
      valA: .word 0x0000000a
      valB: .word 0x0000000b
      valC: .word 0x0000000c
      valD: .word 0x0000000d
  """ )

  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 12

  return [ sparse_mem_img, expected_result ]

@requires_xcc
def test_mul_scoreboard_clear_bug( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "test_j_after_ld_stall.vcd",
                        [0]+mul_scoreboard_clear_bug() )

#---------------------------------------------------------------------------
# 0. bypass logic direct test
#---------------------------------------------------------------------------

from proc.parc.bypass_direct_test import bypass_from_X

@requires_xcc
def test_bypass_direct_from_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_direct_from_X.vcd",
                       bypass_from_X() )

#---------------------------------------------------------------------------
# 1. parcv1-addiu tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_addiu import addiu_no_hazards
from proc.parc.parcv1_addiu import addiu_hazard_W
from proc.parc.parcv1_addiu import addiu_hazard_M
from proc.parc.parcv1_addiu import addiu_hazard_X
from proc.parc.parcv1_addiu import addiu_vmh_delay0
from proc.parc.parcv1_addiu import addiu_vmh_delay5

@requires_xcc
def test_bypass_addiu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_no_hazards.vcd",
                       addiu_no_hazards() )

@requires_xcc
def test_bypass_addiu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_hazard_W.vcd",
                       addiu_hazard_W() )

@requires_xcc
def test_bypass_addiu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_hazard_M.vcd",
                       addiu_hazard_M() )

@requires_xcc
def test_bypass_addiu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_hazard_X.vcd",
                       addiu_hazard_X() )

@requires_vmh
def test_bypass_addiu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_vmh_delay0.vcd",
                       addiu_vmh_delay0() )

@requires_vmh
def test_bypass_addiu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addiu_vmh_delay5.vcd",
                       addiu_vmh_delay5() )

#---------------------------------------------------------------------------
# 2. parcv1-ori tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_ori import ori_no_hazards
from proc.parc.parcv1_ori import ori_hazard_W
from proc.parc.parcv1_ori import ori_hazard_M
from proc.parc.parcv1_ori import ori_hazard_X
from proc.parc.parcv1_ori import ori_vmh_delay0
from proc.parc.parcv1_ori import ori_vmh_delay5

@requires_xcc
def test_bypass_ori_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_no_hazards.vcd",
                       ori_no_hazards() )

@requires_xcc
def test_bypass_ori_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_hazard_W.vcd",
                       ori_hazard_W() )

@requires_xcc
def test_bypass_ori_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_hazard_M.vcd",
                       ori_hazard_M() )

@requires_xcc
def test_bypass_ori_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_hazard_X.vcd",
                       ori_hazard_X() )

@requires_vmh
def test_bypass_ori_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_vmh_delay0.vcd",
                       ori_vmh_delay0() )

@requires_vmh
def test_bypass_ori_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_ori_vmh_delay5.vcd",
                       ori_vmh_delay5() )

#---------------------------------------------------------------------------
# 3. parcv1-lui tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_lui import lui_no_hazards
from proc.parc.parcv1_lui import lui_hazard_W
from proc.parc.parcv1_lui import lui_hazard_M
from proc.parc.parcv1_lui import lui_hazard_X
from proc.parc.parcv1_lui import lui_vmh_delay0
from proc.parc.parcv1_lui import lui_vmh_delay5

@requires_xcc
def test_bypass_lui_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_no_hazards.vcd",
                       lui_no_hazards() )

@requires_xcc
def test_bypass_lui_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_hazard_W.vcd",
                       lui_hazard_W() )

@requires_xcc
def test_bypass_lui_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_hazard_M.vcd",
                       lui_hazard_M() )

@requires_xcc
def test_bypass_lui_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_hazard_X.vcd",
                       lui_hazard_X() )

@requires_vmh
def test_bypass_lui_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_vmh_delay0.vcd",
                       lui_vmh_delay0() )

@requires_vmh
def test_bypass_lui_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lui_vmh_delay5.vcd",
                       lui_vmh_delay5() )

#---------------------------------------------------------------------------
# 4. parcv1-addu tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_addu import addu_no_hazards
from proc.parc.parcv1_addu import addu_hazard_W
from proc.parc.parcv1_addu import addu_hazard_M
from proc.parc.parcv1_addu import addu_hazard_X
from proc.parc.parcv1_addu import addu_vmh_delay0
from proc.parc.parcv1_addu import addu_vmh_delay5

@requires_xcc
def test_bypass_addu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_no_hazards.vcd",
                       addu_no_hazards() )

@requires_xcc
def test_bypass_addu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_hazard_W.vcd",
                       addu_hazard_W() )

@requires_xcc
def test_bypass_addu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_hazard_M.vcd",
                       addu_hazard_M() )

@requires_xcc
def test_bypass_addu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_hazard_X.vcd",
                       addu_hazard_X() )

@requires_vmh
def test_bypass_addu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_vmh_delay0.vcd",
                       addu_vmh_delay0() )

@requires_vmh
def test_bypass_addu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_addu_vmh_delay5.vcd",
                       addu_vmh_delay5() )

#---------------------------------------------------------------------------
# 5. parcv1-lw tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_lw import lw_no_hazards
from proc.parc.parcv1_lw import lw_hazard_W
from proc.parc.parcv1_lw import lw_hazard_M
from proc.parc.parcv1_lw import lw_hazard_X
from proc.parc.parcv1_lw import lw_vmh_delay0
from proc.parc.parcv1_lw import lw_vmh_delay5

@requires_xcc
def test_bypass_lw_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_no_hazards.vcd",
                       lw_no_hazards() )

@requires_xcc
def test_bypass_lw_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_hazard_W.vcd",
                       lw_hazard_W() )

@requires_xcc
def test_bypass_lw_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_hazard_M.vcd",
                       lw_hazard_M() )

@requires_xcc
def test_bypass_lw_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_hazard_X.vcd",
                       lw_hazard_X() )

@requires_vmh
def test_bypass_lw_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_vmh_delay0.vcd",
                       lw_vmh_delay0() )

@requires_vmh
def test_bypass_lw_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lw_vmh_delay5.vcd",
                       lw_vmh_delay5() )

#---------------------------------------------------------------------------
# 6. parcv1-sw tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_sw import sw_no_hazards
from proc.parc.parcv1_sw import sw_hazard_W
from proc.parc.parcv1_sw import sw_hazard_M
from proc.parc.parcv1_sw import sw_hazard_X
from proc.parc.parcv1_sw import sw_vmh_delay0
from proc.parc.parcv1_sw import sw_vmh_delay5

@requires_xcc
def test_bypass_sw_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_no_hazards.vcd",
                       sw_no_hazards() )

@requires_xcc
def test_bypass_sw_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_hazard_W.vcd",
                       sw_hazard_W() )

@requires_xcc
def test_bypass_sw_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_hazard_M.vcd",
                       sw_hazard_M() )

@requires_xcc
def test_bypass_sw_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_hazard_X.vcd",
                       sw_hazard_X() )

@requires_vmh
def test_bypass_sw_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_vmh_delay0.vcd",
                       sw_vmh_delay0() )

@requires_vmh
def test_bypass_sw_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sw_vmh_delay5.vcd",
                       sw_vmh_delay5() )

#---------------------------------------------------------------------------
# 7. parcv1-jal tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_jal import jal_asm
from proc.parc.parcv1_jal import jal_vmh_delay0
from proc.parc.parcv1_jal import jal_vmh_delay5

@requires_xcc
def test_bypass_jal_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jal.vcd",
                       jal_asm() )

@requires_vmh
def test_bypass_jal_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jal_vmh_delay0.vcd",
                       jal_vmh_delay0() )

@requires_vmh
def test_bypass_jal_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jal_vmh_delay5.vcd",
                       jal_vmh_delay5() )

#---------------------------------------------------------------------------
# 8. parcv1-jr tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_jr import jr_asm
from proc.parc.parcv1_jr import jr_vmh_delay0
from proc.parc.parcv1_jr import jr_vmh_delay5

@requires_xcc
def test_bypass_jr_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jr.vcd",
                       jr_asm() )

@requires_vmh
def test_bypass_jr_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jr_vmh_delay0.vcd",
                       jr_vmh_delay0() )

@requires_vmh
def test_bypass_jr_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jr_vmh_delay5.vcd",
                       jr_vmh_delay5() )

#---------------------------------------------------------------------------
# 9. parcv1-bne tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_bne import bne_asm
from proc.parc.parcv1_bne import bne_vmh_delay0
from proc.parc.parcv1_bne import bne_vmh_delay5

@requires_xcc
def test_bypass_bne_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bne.vcd",
                       bne_asm() )

@requires_vmh
def test_bypass_bne_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bne_vmh_delay0.vcd",
                       bne_vmh_delay0() )

@requires_vmh
def test_bypass_bne_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bne_vmh_delay5.vcd",
                       bne_vmh_delay5() )

#---------------------------------------------------------------------------
# 10. parcv2-andi tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_andi import andi_no_hazards
from proc.parc.parcv2_andi import andi_hazard_W
from proc.parc.parcv2_andi import andi_hazard_M
from proc.parc.parcv2_andi import andi_hazard_X
from proc.parc.parcv2_andi import andi_vmh_delay0
from proc.parc.parcv2_andi import andi_vmh_delay5

@requires_xcc
def test_bypass_andi_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_no_hazards.vcd",
                       andi_no_hazards() )

@requires_xcc
def test_bypass_andi_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_hazard_W.vcd",
                       andi_hazard_W() )

@requires_xcc
def test_bypass_andi_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_hazard_M.vcd",
                       andi_hazard_M() )

@requires_xcc
def test_bypass_andi_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_hazard_X.vcd",
                       andi_hazard_X() )

@requires_vmh
def test_bypass_andi_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_vmh_delay0.vcd",
                       andi_vmh_delay0() )

@requires_vmh
def test_bypass_andi_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_andi_vmh_delay5.vcd",
                       andi_vmh_delay5() )

#---------------------------------------------------------------------------
# 11. parcv2-xori tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_xori import xori_no_hazards
from proc.parc.parcv2_xori import xori_hazard_W
from proc.parc.parcv2_xori import xori_hazard_M
from proc.parc.parcv2_xori import xori_hazard_X
from proc.parc.parcv2_xori import xori_vmh_delay0
from proc.parc.parcv2_xori import xori_vmh_delay5

@requires_xcc
def test_bypass_xori_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_no_hazards.vcd",
                       xori_no_hazards() )

@requires_xcc
def test_bypass_xori_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_hazard_W.vcd",
                       xori_hazard_W() )

@requires_xcc
def test_bypass_xori_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_hazard_M.vcd",
                       xori_hazard_M() )

@requires_xcc
def test_bypass_xori_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_hazard_X.vcd",
                       xori_hazard_X() )

@requires_vmh
def test_bypass_xori_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_vmh_delay0.vcd",
                       xori_vmh_delay0() )

@requires_vmh
def test_bypass_xori_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xori_vmh_delay5.vcd",
                       xori_vmh_delay5() )

#---------------------------------------------------------------------------
# 12. parcv2-slti tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_slti import slti_no_hazards
from proc.parc.parcv2_slti import slti_hazard_W
from proc.parc.parcv2_slti import slti_hazard_M
from proc.parc.parcv2_slti import slti_hazard_X
from proc.parc.parcv2_slti import slti_vmh_delay0
from proc.parc.parcv2_slti import slti_vmh_delay5

@requires_xcc
def test_bypass_slti_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_no_hazards.vcd",
                       slti_no_hazards() )

@requires_xcc
def test_bypass_slti_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_hazard_W.vcd",
                       slti_hazard_W() )

@requires_xcc
def test_bypass_slti_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_hazard_M.vcd",
                       slti_hazard_M() )

@requires_xcc
def test_bypass_slti_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_hazard_X.vcd",
                       slti_hazard_X() )

@requires_vmh
def test_bypass_slti_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_vmh_delay0.vcd",
                       slti_vmh_delay0() )

@requires_vmh
def test_bypass_slti_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slti_vmh_delay5.vcd",
                       slti_vmh_delay5() )

#---------------------------------------------------------------------------
# 13. parcv2-sltiu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sltiu import sltiu_no_hazards
from proc.parc.parcv2_sltiu import sltiu_hazard_W
from proc.parc.parcv2_sltiu import sltiu_hazard_M
from proc.parc.parcv2_sltiu import sltiu_hazard_X
from proc.parc.parcv2_sltiu import sltiu_vmh_delay0
from proc.parc.parcv2_sltiu import sltiu_vmh_delay5

@requires_xcc
def test_bypass_sltiu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_no_hazards.vcd",
                       sltiu_no_hazards() )

@requires_xcc
def test_bypass_sltiu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_hazard_W.vcd",
                       sltiu_hazard_W() )

@requires_xcc
def test_bypass_sltiu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_hazard_M.vcd",
                       sltiu_hazard_M() )

@requires_xcc
def test_bypass_sltiu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_hazard_X.vcd",
                       sltiu_hazard_X() )

@requires_vmh
def test_bypass_sltiu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_vmh_delay0.vcd",
                       sltiu_vmh_delay0() )

@requires_vmh
def test_bypass_sltiu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltiu_vmh_delay5.vcd",
                       sltiu_vmh_delay5() )

#---------------------------------------------------------------------------
# 14. parcv2-sll tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sll import sll_no_hazards
from proc.parc.parcv2_sll import sll_hazard_W
from proc.parc.parcv2_sll import sll_hazard_M
from proc.parc.parcv2_sll import sll_hazard_X
from proc.parc.parcv2_sll import sll_vmh_delay0
from proc.parc.parcv2_sll import sll_vmh_delay5

@requires_xcc
def test_bypass_sll_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_no_hazards.vcd",
                       sll_no_hazards() )

@requires_xcc
def test_bypass_sll_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_hazard_W.vcd",
                       sll_hazard_W() )

@requires_xcc
def test_bypass_sll_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_hazard_M.vcd",
                       sll_hazard_M() )

@requires_xcc
def test_bypass_sll_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_hazard_X.vcd",
                       sll_hazard_X() )

@requires_vmh
def test_bypass_sll_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_vmh_delay0.vcd",
                       sll_vmh_delay0() )

@requires_vmh
def test_bypass_sll_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sll_vmh_delay5.vcd",
                       sll_vmh_delay5() )

#---------------------------------------------------------------------------
# 15. parcv2-srl tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srl import srl_no_hazards
from proc.parc.parcv2_srl import srl_hazard_W
from proc.parc.parcv2_srl import srl_hazard_M
from proc.parc.parcv2_srl import srl_hazard_X
from proc.parc.parcv2_srl import srl_vmh_delay0
from proc.parc.parcv2_srl import srl_vmh_delay5

@requires_xcc
def test_bypass_srl_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_no_hazards.vcd",
                       srl_no_hazards() )

@requires_xcc
def test_bypass_srl_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_hazard_W.vcd",
                       srl_hazard_W() )

@requires_xcc
def test_bypass_srl_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_hazard_M.vcd",
                       srl_hazard_M() )

@requires_xcc
def test_bypass_srl_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_hazard_X.vcd",
                       srl_hazard_X() )

@requires_vmh
def test_bypass_srl_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_vmh_delay0.vcd",
                       srl_vmh_delay0() )

@requires_vmh
def test_bypass_srl_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srl_vmh_delay5.vcd",
                       srl_vmh_delay5() )

#---------------------------------------------------------------------------
# 16. parcv2-sra tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sra import sra_no_hazards
from proc.parc.parcv2_sra import sra_hazard_W
from proc.parc.parcv2_sra import sra_hazard_M
from proc.parc.parcv2_sra import sra_hazard_X
from proc.parc.parcv2_sra import sra_vmh_delay0
from proc.parc.parcv2_sra import sra_vmh_delay5

@requires_xcc
def test_bypass_sra_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_no_hazards.vcd",
                       sra_no_hazards() )

@requires_xcc
def test_bypass_sra_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_hazard_W.vcd",
                       sra_hazard_W() )

@requires_xcc
def test_bypass_sra_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_hazard_M.vcd",
                       sra_hazard_M() )

@requires_xcc
def test_bypass_sra_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_hazard_X.vcd",
                       sra_hazard_X() )

@requires_vmh
def test_bypass_sra_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_vmh_delay0.vcd",
                       sra_vmh_delay0() )

@requires_vmh
def test_bypass_sra_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sra_vmh_delay5.vcd",
                       sra_vmh_delay5() )

#---------------------------------------------------------------------------
# 17. parcv2-sllv tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sllv import sllv_no_hazards
from proc.parc.parcv2_sllv import sllv_hazard_W
from proc.parc.parcv2_sllv import sllv_hazard_M
from proc.parc.parcv2_sllv import sllv_hazard_X
from proc.parc.parcv2_sllv import sllv_vmh_delay0
from proc.parc.parcv2_sllv import sllv_vmh_delay5

@requires_xcc
def test_bypass_sllv_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_no_hazards.vcd",
                       sllv_no_hazards() )

@requires_xcc
def test_bypass_sllv_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_hazard_W.vcd",
                       sllv_hazard_W() )

@requires_xcc
def test_bypass_sllv_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_hazard_M.vcd",
                       sllv_hazard_M() )

@requires_xcc
def test_bypass_sllv_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_hazard_X.vcd",
                       sllv_hazard_X() )

@requires_vmh
def test_bypass_sllv_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_vmh_delay0.vcd",
                       sllv_vmh_delay0() )

@requires_vmh
def test_bypass_sllv_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sllv_vmh_delay5.vcd",
                       sllv_vmh_delay5() )

#---------------------------------------------------------------------------
# 18. parcv2-srlv tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srlv import srlv_no_hazards
from proc.parc.parcv2_srlv import srlv_hazard_W
from proc.parc.parcv2_srlv import srlv_hazard_M
from proc.parc.parcv2_srlv import srlv_hazard_X
from proc.parc.parcv2_srlv import srlv_vmh_delay0
from proc.parc.parcv2_srlv import srlv_vmh_delay5

@requires_xcc
def test_bypass_srlv_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_no_hazards.vcd",
                       srlv_no_hazards() )

@requires_xcc
def test_bypass_srlv_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_hazard_W.vcd",
                       srlv_hazard_W() )

@requires_xcc
def test_bypass_srlv_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_hazard_M.vcd",
                       srlv_hazard_M() )

@requires_xcc
def test_bypass_srlv_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_hazard_X.vcd",
                       srlv_hazard_X() )

@requires_vmh
def test_bypass_srlv_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_vmh_delay0.vcd",
                       srlv_vmh_delay0() )

@requires_vmh
def test_bypass_srlv_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srlv_vmh_delay5.vcd",
                       srlv_vmh_delay5() )

#---------------------------------------------------------------------------
# 19. parcv2-srav tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srav import srav_no_hazards
from proc.parc.parcv2_srav import srav_hazard_W
from proc.parc.parcv2_srav import srav_hazard_M
from proc.parc.parcv2_srav import srav_hazard_X
from proc.parc.parcv2_srav import srav_vmh_delay0
from proc.parc.parcv2_srav import srav_vmh_delay5

@requires_xcc
def test_bypass_srav_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_no_hazards.vcd",
                       srav_no_hazards() )

@requires_xcc
def test_bypass_srav_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_hazard_W.vcd",
                       srav_hazard_W() )

@requires_xcc
def test_bypass_srav_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_hazard_M.vcd",
                       srav_hazard_M() )

@requires_xcc
def test_bypass_srav_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_hazard_X.vcd",
                       srav_hazard_X() )

@requires_vmh
def test_bypass_srav_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_vmh_delay0.vcd",
                       srav_vmh_delay0() )

@requires_vmh
def test_bypass_srav_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_srav_vmh_delay5.vcd",
                       srav_vmh_delay5() )

#---------------------------------------------------------------------------
# 20. parcv2-subu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_subu import subu_no_hazards
from proc.parc.parcv2_subu import subu_hazard_W
from proc.parc.parcv2_subu import subu_hazard_M
from proc.parc.parcv2_subu import subu_hazard_X
from proc.parc.parcv2_subu import subu_vmh_delay0
from proc.parc.parcv2_subu import subu_vmh_delay5

@requires_xcc
def test_bypass_subu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_no_hazards.vcd",
                       subu_no_hazards() )

@requires_xcc
def test_bypass_subu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_hazard_W.vcd",
                       subu_hazard_W() )

@requires_xcc
def test_bypass_subu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_hazard_M.vcd",
                       subu_hazard_M() )

@requires_xcc
def test_bypass_subu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_hazard_X.vcd",
                       subu_hazard_X() )

@requires_vmh
def test_bypass_subu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_vmh_delay0.vcd",
                       subu_vmh_delay0() )

@requires_vmh
def test_bypass_subu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_subu_vmh_delay5.vcd",
                       subu_vmh_delay5() )

#---------------------------------------------------------------------------
# 21. parcv2-and tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_and import and_no_hazards
from proc.parc.parcv2_and import and_hazard_W
from proc.parc.parcv2_and import and_hazard_M
from proc.parc.parcv2_and import and_hazard_X
from proc.parc.parcv2_and import and_vmh_delay0
from proc.parc.parcv2_and import and_vmh_delay5

@requires_xcc
def test_bypass_and_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_no_hazards.vcd",
                       and_no_hazards() )

@requires_xcc
def test_bypass_and_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_hazard_W.vcd",
                       and_hazard_W() )

@requires_xcc
def test_bypass_and_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_hazard_M.vcd",
                       and_hazard_M() )

@requires_xcc
def test_bypass_and_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_hazard_X.vcd",
                       and_hazard_X() )

@requires_vmh
def test_bypass_and_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_vmh_delay0.vcd",
                       and_vmh_delay0() )

@requires_vmh
def test_bypass_and_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_and_vmh_delay5.vcd",
                       and_vmh_delay5() )

#---------------------------------------------------------------------------
# 22. parcv2-or tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_or import or_no_hazards
from proc.parc.parcv2_or import or_hazard_W
from proc.parc.parcv2_or import or_hazard_M
from proc.parc.parcv2_or import or_hazard_X
from proc.parc.parcv2_or import or_vmh_delay0
from proc.parc.parcv2_or import or_vmh_delay5

@requires_xcc
def test_bypass_or_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_no_hazards.vcd",
                       or_no_hazards() )

@requires_xcc
def test_bypass_or_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_hazard_W.vcd",
                       or_hazard_W() )

@requires_xcc
def test_bypass_or_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_hazard_M.vcd",
                       or_hazard_M() )

@requires_xcc
def test_bypass_or_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_hazard_X.vcd",
                       or_hazard_X() )

@requires_vmh
def test_bypass_or_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_vmh_delay0.vcd",
                       or_vmh_delay0() )

@requires_vmh
def test_bypass_or_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_or_vmh_delay5.vcd",
                       or_vmh_delay5() )

#---------------------------------------------------------------------------
# 23. parcv2-xor tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_xor import xor_no_hazards
from proc.parc.parcv2_xor import xor_hazard_W
from proc.parc.parcv2_xor import xor_hazard_M
from proc.parc.parcv2_xor import xor_hazard_X
from proc.parc.parcv2_xor import xor_vmh_delay0
from proc.parc.parcv2_xor import xor_vmh_delay5

@requires_xcc
def test_bypass_xor_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_no_hazards.vcd",
                       xor_no_hazards() )

@requires_xcc
def test_bypass_xor_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_hazard_W.vcd",
                       xor_hazard_W() )

@requires_xcc
def test_bypass_xor_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_hazard_M.vcd",
                       xor_hazard_M() )

@requires_xcc
def test_bypass_xor_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_hazard_X.vcd",
                       xor_hazard_X() )

@requires_vmh
def test_bypass_xor_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_vmh_delay0.vcd",
                       xor_vmh_delay0() )

@requires_vmh
def test_bypass_xor_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_xor_vmh_delay5.vcd",
                       xor_vmh_delay5() )

#---------------------------------------------------------------------------
# 24. parcv2-nor tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_nor import nor_no_hazards
from proc.parc.parcv2_nor import nor_hazard_W
from proc.parc.parcv2_nor import nor_hazard_M
from proc.parc.parcv2_nor import nor_hazard_X
from proc.parc.parcv2_nor import nor_vmh_delay0
from proc.parc.parcv2_nor import nor_vmh_delay5

@requires_xcc
def test_bypass_nor_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_no_hazards.vcd",
                       nor_no_hazards() )

@requires_xcc
def test_bypass_nor_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_hazard_W.vcd",
                       nor_hazard_W() )

@requires_xcc
def test_bypass_nor_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_hazard_M.vcd",
                       nor_hazard_M() )

@requires_xcc
def test_bypass_nor_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_hazard_X.vcd",
                       nor_hazard_X() )

@requires_vmh
def test_bypass_nor_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_vmh_delay0.vcd",
                       nor_vmh_delay0() )

@requires_vmh
def test_bypass_nor_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_nor_vmh_delay5.vcd",
                       nor_vmh_delay5() )

#---------------------------------------------------------------------------
# 25. parcv2-slt tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_slt import slt_no_hazards
from proc.parc.parcv2_slt import slt_hazard_W
from proc.parc.parcv2_slt import slt_hazard_M
from proc.parc.parcv2_slt import slt_hazard_X
from proc.parc.parcv2_slt import slt_vmh_delay0
from proc.parc.parcv2_slt import slt_vmh_delay5

@requires_xcc
def test_bypass_slt_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_no_hazards.vcd",
                       slt_no_hazards() )

@requires_xcc
def test_bypass_slt_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_hazard_W.vcd",
                       slt_hazard_W() )

@requires_xcc
def test_bypass_slt_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_hazard_M.vcd",
                       slt_hazard_M() )

@requires_xcc
def test_bypass_slt_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_hazard_X.vcd",
                       slt_hazard_X() )

@requires_vmh
def test_bypass_slt_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_vmh_delay0.vcd",
                       slt_vmh_delay0() )

@requires_vmh
def test_bypass_slt_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_slt_vmh_delay5.vcd",
                       slt_vmh_delay5() )

#---------------------------------------------------------------------------
# 26. parcv2-sltu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sltu import sltu_no_hazards
from proc.parc.parcv2_sltu import sltu_hazard_W
from proc.parc.parcv2_sltu import sltu_hazard_M
from proc.parc.parcv2_sltu import sltu_hazard_X
from proc.parc.parcv2_sltu import sltu_vmh_delay0
from proc.parc.parcv2_sltu import sltu_vmh_delay5

@requires_xcc
def test_bypass_sltu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_no_hazards.vcd",
                       sltu_no_hazards() )

@requires_xcc
def test_bypass_sltu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_hazard_W.vcd",
                       sltu_hazard_W() )

@requires_xcc
def test_bypass_sltu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_hazard_M.vcd",
                       sltu_hazard_M() )

@requires_xcc
def test_bypass_sltu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_hazard_X.vcd",
                       sltu_hazard_X() )

@requires_vmh
def test_bypass_sltu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_vmh_delay0.vcd",
                       sltu_vmh_delay0() )

@requires_vmh
def test_bypass_sltu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sltu_vmh_delay5.vcd",
                       sltu_vmh_delay5() )

#---------------------------------------------------------------------------
# 27. parcv2-mul tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_mul import mul_no_hazards
from proc.parc.parcv2_mul import mul_hazard_W
from proc.parc.parcv2_mul import mul_hazard_M
from proc.parc.parcv2_mul import mul_hazard_X
from proc.parc.parcv2_mul import mul_vmh_delay0
from proc.parc.parcv2_mul import mul_vmh_delay5

@requires_xcc
def test_bypass_mul_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_no_hazards.vcd",
                       mul_no_hazards() )

@requires_xcc
def test_bypass_mul_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_hazard_W.vcd",
                       mul_hazard_W() )

@requires_xcc
def test_bypass_mul_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_hazard_M.vcd",
                       mul_hazard_M() )

@requires_xcc
def test_bypass_mul_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_hazard_X.vcd",
                       mul_hazard_X() )

@requires_vmh
def test_bypass_mul_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_vmh_delay0.vcd",
                       mul_vmh_delay0() )

@requires_vmh
def test_bypass_mul_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_mul_vmh_delay5.vcd",
                       mul_vmh_delay5() )

#---------------------------------------------------------------------------
# 28. parcv2-div tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_div import div_no_hazards
from proc.parc.parcv2_div import div_hazard_W
from proc.parc.parcv2_div import div_hazard_M
from proc.parc.parcv2_div import div_hazard_X
from proc.parc.parcv2_div import div_vmh_delay0
from proc.parc.parcv2_div import div_vmh_delay5

@requires_xcc
def test_bypass_div_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_no_hazards.vcd",
                       div_no_hazards() )

@requires_xcc
def test_bypass_div_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_hazard_W.vcd",
                       div_hazard_W() )

@requires_xcc
def test_bypass_div_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_hazard_M.vcd",
                       div_hazard_M() )

@requires_xcc
def test_bypass_div_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_hazard_X.vcd",
                       div_hazard_X() )

@requires_vmh
def test_bypass_div_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_vmh_delay0.vcd",
                       div_vmh_delay0() )

@requires_vmh
def test_bypass_div_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_div_vmh_delay5.vcd",
                       div_vmh_delay5() )

#---------------------------------------------------------------------------
# 29. parcv2-divu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_divu import divu_no_hazards
from proc.parc.parcv2_divu import divu_hazard_W
from proc.parc.parcv2_divu import divu_hazard_M
from proc.parc.parcv2_divu import divu_hazard_X
from proc.parc.parcv2_divu import divu_vmh_delay0
from proc.parc.parcv2_divu import divu_vmh_delay5

@requires_xcc
def test_bypass_divu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_no_hazards.vcd",
                       divu_no_hazards() )

@requires_xcc
def test_bypass_divu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_hazard_W.vcd",
                       divu_hazard_W() )

@requires_xcc
def test_bypass_divu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_hazard_M.vcd",
                       divu_hazard_M() )

@requires_xcc
def test_bypass_divu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_hazard_X.vcd",
                       divu_hazard_X() )

@requires_vmh
def test_bypass_divu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_vmh_delay0.vcd",
                       divu_vmh_delay0() )

@requires_vmh
def test_bypass_divu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_divu_vmh_delay5.vcd",
                       divu_vmh_delay5() )

#---------------------------------------------------------------------------
# 30. parcv2-rem tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_rem import rem_no_hazards
from proc.parc.parcv2_rem import rem_hazard_W
from proc.parc.parcv2_rem import rem_hazard_M
from proc.parc.parcv2_rem import rem_hazard_X
from proc.parc.parcv2_rem import rem_vmh_delay0
from proc.parc.parcv2_rem import rem_vmh_delay5

@requires_xcc
def test_bypass_rem_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_no_hazards.vcd",
                       rem_no_hazards() )

@requires_xcc
def test_bypass_rem_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_hazard_W.vcd",
                       rem_hazard_W() )

@requires_xcc
def test_bypass_rem_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_hazard_M.vcd",
                       rem_hazard_M() )

@requires_xcc
def test_bypass_rem_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_hazard_X.vcd",
                       rem_hazard_X() )

@requires_vmh
def test_bypass_rem_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_vmh_delay0.vcd",
                       rem_vmh_delay0() )

@requires_vmh
def test_bypass_rem_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_rem_vmh_delay5.vcd",
                       rem_vmh_delay5() )

#---------------------------------------------------------------------------
# 31. parcv2-remu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_remu import remu_no_hazards
from proc.parc.parcv2_remu import remu_hazard_W
from proc.parc.parcv2_remu import remu_hazard_M
from proc.parc.parcv2_remu import remu_hazard_X
from proc.parc.parcv2_remu import remu_vmh_delay0
from proc.parc.parcv2_remu import remu_vmh_delay5

@requires_xcc
def test_bypass_remu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_no_hazards.vcd",
                       remu_no_hazards() )

@requires_xcc
def test_bypass_remu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_hazard_W.vcd",
                       remu_hazard_W() )

@requires_xcc
def test_bypass_remu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_hazard_M.vcd",
                       remu_hazard_M() )

@requires_xcc
def test_bypass_remu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_hazard_X.vcd",
                       remu_hazard_X() )

@requires_vmh
def test_bypass_remu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_vmh_delay0.vcd",
                       remu_vmh_delay0() )

@requires_vmh
def test_bypass_remu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_remu_vmh_delay5.vcd",
                       remu_vmh_delay5() )

#---------------------------------------------------------------------------
# 32. parcv2-lb tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lb import lb_no_hazards
from proc.parc.parcv2_lb import lb_hazard_W
from proc.parc.parcv2_lb import lb_hazard_M
from proc.parc.parcv2_lb import lb_hazard_X
from proc.parc.parcv2_lb import lb_vmh_delay0
from proc.parc.parcv2_lb import lb_vmh_delay5

@requires_xcc
def test_bypass_lb_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_no_hazards.vcd",
                       lb_no_hazards() )

@requires_xcc
def test_bypass_lb_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_hazard_W.vcd",
                       lb_hazard_W() )

@requires_xcc
def test_bypass_lb_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_hazard_M.vcd",
                       lb_hazard_M() )

@requires_xcc
def test_bypass_lb_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_hazard_X.vcd",
                       lb_hazard_X() )

@requires_vmh
def test_bypass_lb_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_vmh_delay0.vcd",
                       lb_vmh_delay0() )

@requires_vmh
def test_bypass_lb_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lb_vmh_delay5.vcd",
                       lb_vmh_delay5() )

#---------------------------------------------------------------------------
# 33. parcv2-lbu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lbu import lbu_no_hazards
from proc.parc.parcv2_lbu import lbu_hazard_W
from proc.parc.parcv2_lbu import lbu_hazard_M
from proc.parc.parcv2_lbu import lbu_hazard_X
from proc.parc.parcv2_lbu import lbu_vmh_delay0
from proc.parc.parcv2_lbu import lbu_vmh_delay5

@requires_xcc
def test_bypass_lbu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_no_hazards.vcd",
                       lbu_no_hazards() )

@requires_xcc
def test_bypass_lbu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_hazard_W.vcd",
                       lbu_hazard_W() )

@requires_xcc
def test_bypass_lbu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_hazard_M.vcd",
                       lbu_hazard_M() )

@requires_xcc
def test_bypass_lbu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_hazard_X.vcd",
                       lbu_hazard_X() )

@requires_vmh
def test_bypass_lbu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_vmh_delay0.vcd",
                       lbu_vmh_delay0() )

@requires_vmh
def test_bypass_lbu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lbu_vmh_delay5.vcd",
                       lbu_vmh_delay5() )

#---------------------------------------------------------------------------
# 34. parcv2-lh tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lh import lh_no_hazards
from proc.parc.parcv2_lh import lh_hazard_W
from proc.parc.parcv2_lh import lh_hazard_M
from proc.parc.parcv2_lh import lh_hazard_X
from proc.parc.parcv2_lh import lh_vmh_delay0
from proc.parc.parcv2_lh import lh_vmh_delay5

@requires_xcc
def test_bypass_lh_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_no_hazards.vcd",
                       lh_no_hazards() )

@requires_xcc
def test_bypass_lh_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_hazard_W.vcd",
                       lh_hazard_W() )

@requires_xcc
def test_bypass_lh_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_hazard_M.vcd",
                       lh_hazard_M() )

@requires_xcc
def test_bypass_lh_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_hazard_X.vcd",
                       lh_hazard_X() )

@requires_vmh
def test_bypass_lh_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_vmh_delay0.vcd",
                       lh_vmh_delay0() )

@requires_vmh
def test_bypass_lh_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lh_vmh_delay5.vcd",
                       lh_vmh_delay5() )

#---------------------------------------------------------------------------
# 35. parcv2-lhu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lhu import lhu_no_hazards
from proc.parc.parcv2_lhu import lhu_hazard_W
from proc.parc.parcv2_lhu import lhu_hazard_M
from proc.parc.parcv2_lhu import lhu_hazard_X
from proc.parc.parcv2_lhu import lhu_vmh_delay0
from proc.parc.parcv2_lhu import lhu_vmh_delay5

@requires_xcc
def test_bypass_lhu_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_no_hazards.vcd",
                       lhu_no_hazards() )

@requires_xcc
def test_bypass_lhu_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_hazard_W.vcd",
                       lhu_hazard_W() )

@requires_xcc
def test_bypass_lhu_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_hazard_M.vcd",
                       lhu_hazard_M() )

@requires_xcc
def test_bypass_lhu_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_hazard_X.vcd",
                       lhu_hazard_X() )

@requires_vmh
def test_bypass_lhu_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_vmh_delay0.vcd",
                       lhu_vmh_delay0() )

@requires_vmh
def test_bypass_lhu_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_lhu_vmh_delay5.vcd",
                       lhu_vmh_delay5() )

#---------------------------------------------------------------------------
# 36. parcv2-sb tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sb import sb_no_hazards
from proc.parc.parcv2_sb import sb_hazard_W
from proc.parc.parcv2_sb import sb_hazard_M
from proc.parc.parcv2_sb import sb_hazard_X
from proc.parc.parcv2_sb import sb_vmh_delay0
from proc.parc.parcv2_sb import sb_vmh_delay5

@requires_xcc
def test_bypass_sb_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_no_hazards.vcd",
                       sb_no_hazards() )

@requires_xcc
def test_bypass_sb_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_hazard_W.vcd",
                       sb_hazard_W() )

@requires_xcc
def test_bypass_sb_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_hazard_M.vcd",
                       sb_hazard_M() )

@requires_xcc
def test_bypass_sb_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_hazard_X.vcd",
                       sb_hazard_X() )

@requires_vmh
def test_bypass_sb_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_vmh_delay0.vcd",
                       sb_vmh_delay0() )

@requires_vmh
def test_bypass_sb_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sb_vmh_delay5.vcd",
                       sb_vmh_delay5() )

#---------------------------------------------------------------------------
# 37. parcv2-sh tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sh import sh_no_hazards
from proc.parc.parcv2_sh import sh_hazard_W
from proc.parc.parcv2_sh import sh_hazard_M
from proc.parc.parcv2_sh import sh_hazard_X
from proc.parc.parcv2_sh import sh_vmh_delay0
from proc.parc.parcv2_sh import sh_vmh_delay5

@requires_xcc
def test_bypass_sh_no_hazards( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_no_hazards.vcd",
                       sh_no_hazards() )

@requires_xcc
def test_bypass_sh_hazard_W( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_hazard_W.vcd",
                       sh_hazard_W() )

@requires_xcc
def test_bypass_sh_hazard_M( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_hazard_M.vcd",
                       sh_hazard_M() )

@requires_xcc
def test_bypass_sh_hazard_X( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_hazard_X.vcd",
                       sh_hazard_X() )

@requires_vmh
def test_bypass_sh_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_vmh_delay0.vcd",
                       sh_vmh_delay0() )

@requires_vmh
def test_bypass_sh_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_sh_vmh_delay5.vcd",
                       sh_vmh_delay5() )

#---------------------------------------------------------------------------
# 38. parcv2-j tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_j import j_asm
from proc.parc.parcv2_j import j_vmh_delay0
from proc.parc.parcv2_j import j_vmh_delay5

@requires_xcc
def test_bypass_j_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_j.vcd",
                       j_asm() )

@requires_vmh
@requires_xcc
def test_bypass_j_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_j_vmh_delay0.vcd",
                       j_vmh_delay0() )

@requires_vmh
@requires_xcc
def test_bypass_j_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_j_vmh_delay5.vcd",
                       j_vmh_delay5() )

#---------------------------------------------------------------------------
# 39. parcv2-jalr tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_jalr import jalr_asm
from proc.parc.parcv2_jalr import jalr_vmh_delay0
from proc.parc.parcv2_jalr import jalr_vmh_delay5

@requires_xcc
def test_bypass_jalr_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jalr.vcd",
                       jalr_asm() )

@requires_vmh
def test_bypass_jalr_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jalr_vmh_delay0.vcd",
                       jalr_vmh_delay0() )

@requires_vmh
def test_bypass_jalr_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_jalr_vmh_delay5.vcd",
                       jalr_vmh_delay5() )

#---------------------------------------------------------------------------
# 40. parcv2-beq tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_beq import beq_asm
from proc.parc.parcv2_beq import beq_vmh_delay0
from proc.parc.parcv2_beq import beq_vmh_delay5

@requires_xcc
def test_bypass_beq_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_beq.vcd",
                       beq_asm() )

@requires_vmh
def test_bypass_beq_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_beq_vmh_delay0.vcd",
                       beq_vmh_delay0() )

@requires_vmh
def test_bypass_beq_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_beq_vmh_delay5.vcd",
                       beq_vmh_delay5() )

#---------------------------------------------------------------------------
# 41. parcv2-blez tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_blez import blez_asm
from proc.parc.parcv2_blez import blez_vmh_delay0
from proc.parc.parcv2_blez import blez_vmh_delay5

@requires_xcc
def test_bypass_blez_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_blez.vcd",
                       blez_asm() )

@requires_vmh
def test_bypass_blez_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_blez_vmh_delay0.vcd",
                       blez_vmh_delay0() )

@requires_vmh
def test_bypass_blez_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_blez_vmh_delay5.vcd",
                       blez_vmh_delay5() )

#---------------------------------------------------------------------------
# 42. parcv2-bgtz tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bgtz import bgtz_asm
from proc.parc.parcv2_bgtz import bgtz_vmh_delay0
from proc.parc.parcv2_bgtz import bgtz_vmh_delay5

@requires_xcc
def test_bypass_bgtz_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgtz.vcd",
                       bgtz_asm() )

@requires_vmh
def test_bypass_bgtz_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgtz_vmh_delay0.vcd",
                       bgtz_vmh_delay0() )

@requires_vmh
def test_bypass_bgtz_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgtz_vmh_delay5.vcd",
                       bgtz_vmh_delay5() )

#---------------------------------------------------------------------------
# 43. parcv2-bltz tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bltz import bltz_asm
from proc.parc.parcv2_bltz import bltz_vmh_delay0
from proc.parc.parcv2_bltz import bltz_vmh_delay5

@requires_xcc
def test_bypass_bltz_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bltz.vcd",
                       bltz_asm() )

@requires_vmh
def test_bypass_bltz_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bltz_vmh_delay0.vcd",
                       bltz_vmh_delay0() )

@requires_vmh
def test_bypass_bltz_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bltz_vmh_delay5.vcd",
                       bltz_vmh_delay5() )

#---------------------------------------------------------------------------
# 44. parcv2-bgez tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bgez import bgez_asm
from proc.parc.parcv2_bgez import bgez_vmh_delay0
from proc.parc.parcv2_bgez import bgez_vmh_delay5

@requires_xcc
def test_bypass_bgez_asm( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgez.vcd",
                       bgez_asm() )

@requires_vmh
def test_bypass_bgez_vmh_delay0( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgez_vmh_delay0.vcd",
                       bgez_vmh_delay0() )

@requires_vmh
def test_bypass_bgez_vmh_delay5( dump_vcd, test_verilog ):
  run_bypass_proc_test( dump_vcd, test_verilog, "bypass_bgez_vmh_delay5.vcd",
                       bgez_vmh_delay5() )

