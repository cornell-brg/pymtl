#=========================================================================
# Tile_test.py
#=========================================================================
# ParcProc5stBypass assembly tests driver

import pytest

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
  def __init__( s, xcel_type, memreq_params, memresp_params,
                   mem_delay, sparse_mem_img, test_verilog ):

    data_nbits = memreq_params.data_nbits
    s.tile     = Tile( reset_vector   = 0x00000400,
                       mem_data_nbits = data_nbits,
                       xcel_type      = xcel_type )
    s.mem      = TestMemory( memreq_params, memresp_params, 2,
                             mem_delay, mem_nbytes=2**24  )
    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )

    if test_verilog:
      pytest.xfail(
      """Verilog translation currently fails for DotProduct because:
         - True/False keywords to not translate
         - Type inference from BitStructs currently fail
      """)

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
def run_proc_test( xcel_type, test_verilog, dump_vcd, vcd_file, input_list ):

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

  model = TestHarness( xcel_type, memreq_params, memresp_params,
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

def mtc2_1x1_delay0():
  return [0]+mtc2_1x1()

def mtc2_1x1_delay5():
  return [5]+mtc2_1x1()

def mtc2_3x3_delay0():
  return [0]+mtc2_3x3()

def mtc2_3x3_delay5():
  return [5]+mtc2_3x3()

#---------------------------------------------------------------------------
# j_after_ld_stall
#---------------------------------------------------------------------------
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

  return [ 0, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# mul_scoreboard_clear_bug
#---------------------------------------------------------------------------
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

  return [ 0, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# 0. bypass logic direct test
#---------------------------------------------------------------------------

from proc.parc.bypass_direct_test import bypass_from_X

#---------------------------------------------------------------------------
# 1. parcv1-addiu tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_addiu import addiu_no_hazards
from proc.parc.parcv1_addiu import addiu_hazard_W
from proc.parc.parcv1_addiu import addiu_hazard_M
from proc.parc.parcv1_addiu import addiu_hazard_X
from proc.parc.parcv1_addiu import addiu_vmh_delay0
from proc.parc.parcv1_addiu import addiu_vmh_delay5

#---------------------------------------------------------------------------
# 2. parcv1-ori tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_ori import ori_no_hazards
from proc.parc.parcv1_ori import ori_hazard_W
from proc.parc.parcv1_ori import ori_hazard_M
from proc.parc.parcv1_ori import ori_hazard_X
from proc.parc.parcv1_ori import ori_vmh_delay0
from proc.parc.parcv1_ori import ori_vmh_delay5

#---------------------------------------------------------------------------
# 3. parcv1-lui tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_lui import lui_no_hazards
from proc.parc.parcv1_lui import lui_hazard_W
from proc.parc.parcv1_lui import lui_hazard_M
from proc.parc.parcv1_lui import lui_hazard_X
from proc.parc.parcv1_lui import lui_vmh_delay0
from proc.parc.parcv1_lui import lui_vmh_delay5

#---------------------------------------------------------------------------
# 4. parcv1-addu tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_addu import addu_no_hazards
from proc.parc.parcv1_addu import addu_hazard_W
from proc.parc.parcv1_addu import addu_hazard_M
from proc.parc.parcv1_addu import addu_hazard_X
from proc.parc.parcv1_addu import addu_vmh_delay0
from proc.parc.parcv1_addu import addu_vmh_delay5

#---------------------------------------------------------------------------
# 5. parcv1-lw tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_lw import lw_no_hazards
from proc.parc.parcv1_lw import lw_hazard_W
from proc.parc.parcv1_lw import lw_hazard_M
from proc.parc.parcv1_lw import lw_hazard_X
from proc.parc.parcv1_lw import lw_vmh_delay0
from proc.parc.parcv1_lw import lw_vmh_delay5

#---------------------------------------------------------------------------
# 6. parcv1-sw tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_sw import sw_no_hazards
from proc.parc.parcv1_sw import sw_hazard_W
from proc.parc.parcv1_sw import sw_hazard_M
from proc.parc.parcv1_sw import sw_hazard_X
from proc.parc.parcv1_sw import sw_vmh_delay0
from proc.parc.parcv1_sw import sw_vmh_delay5

#---------------------------------------------------------------------------
# 7. parcv1-jal tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_jal import jal_asm
from proc.parc.parcv1_jal import jal_vmh_delay0
from proc.parc.parcv1_jal import jal_vmh_delay5

#---------------------------------------------------------------------------
# 8. parcv1-jr tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_jr import jr_asm
from proc.parc.parcv1_jr import jr_vmh_delay0
from proc.parc.parcv1_jr import jr_vmh_delay5

#---------------------------------------------------------------------------
# 9. parcv1-bne tests
#---------------------------------------------------------------------------

from proc.parc.parcv1_bne import bne_asm
from proc.parc.parcv1_bne import bne_vmh_delay0
from proc.parc.parcv1_bne import bne_vmh_delay5

#---------------------------------------------------------------------------
# 10. parcv2-andi tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_andi import andi_no_hazards
from proc.parc.parcv2_andi import andi_hazard_W
from proc.parc.parcv2_andi import andi_hazard_M
from proc.parc.parcv2_andi import andi_hazard_X
from proc.parc.parcv2_andi import andi_vmh_delay0
from proc.parc.parcv2_andi import andi_vmh_delay5

#---------------------------------------------------------------------------
# 11. parcv2-xori tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_xori import xori_no_hazards
from proc.parc.parcv2_xori import xori_hazard_W
from proc.parc.parcv2_xori import xori_hazard_M
from proc.parc.parcv2_xori import xori_hazard_X
from proc.parc.parcv2_xori import xori_vmh_delay0
from proc.parc.parcv2_xori import xori_vmh_delay5

#---------------------------------------------------------------------------
# 12. parcv2-slti tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_slti import slti_no_hazards
from proc.parc.parcv2_slti import slti_hazard_W
from proc.parc.parcv2_slti import slti_hazard_M
from proc.parc.parcv2_slti import slti_hazard_X
from proc.parc.parcv2_slti import slti_vmh_delay0
from proc.parc.parcv2_slti import slti_vmh_delay5

#---------------------------------------------------------------------------
# 13. parcv2-sltiu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sltiu import sltiu_no_hazards
from proc.parc.parcv2_sltiu import sltiu_hazard_W
from proc.parc.parcv2_sltiu import sltiu_hazard_M
from proc.parc.parcv2_sltiu import sltiu_hazard_X
from proc.parc.parcv2_sltiu import sltiu_vmh_delay0
from proc.parc.parcv2_sltiu import sltiu_vmh_delay5

#---------------------------------------------------------------------------
# 14. parcv2-sll tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sll import sll_no_hazards
from proc.parc.parcv2_sll import sll_hazard_W
from proc.parc.parcv2_sll import sll_hazard_M
from proc.parc.parcv2_sll import sll_hazard_X
from proc.parc.parcv2_sll import sll_vmh_delay0
from proc.parc.parcv2_sll import sll_vmh_delay5

#---------------------------------------------------------------------------
# 15. parcv2-srl tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srl import srl_no_hazards
from proc.parc.parcv2_srl import srl_hazard_W
from proc.parc.parcv2_srl import srl_hazard_M
from proc.parc.parcv2_srl import srl_hazard_X
from proc.parc.parcv2_srl import srl_vmh_delay0
from proc.parc.parcv2_srl import srl_vmh_delay5

#---------------------------------------------------------------------------
# 16. parcv2-sra tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sra import sra_no_hazards
from proc.parc.parcv2_sra import sra_hazard_W
from proc.parc.parcv2_sra import sra_hazard_M
from proc.parc.parcv2_sra import sra_hazard_X
from proc.parc.parcv2_sra import sra_vmh_delay0
from proc.parc.parcv2_sra import sra_vmh_delay5

#---------------------------------------------------------------------------
# 17. parcv2-sllv tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sllv import sllv_no_hazards
from proc.parc.parcv2_sllv import sllv_hazard_W
from proc.parc.parcv2_sllv import sllv_hazard_M
from proc.parc.parcv2_sllv import sllv_hazard_X
from proc.parc.parcv2_sllv import sllv_vmh_delay0
from proc.parc.parcv2_sllv import sllv_vmh_delay5

#---------------------------------------------------------------------------
# 18. parcv2-srlv tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srlv import srlv_no_hazards
from proc.parc.parcv2_srlv import srlv_hazard_W
from proc.parc.parcv2_srlv import srlv_hazard_M
from proc.parc.parcv2_srlv import srlv_hazard_X
from proc.parc.parcv2_srlv import srlv_vmh_delay0
from proc.parc.parcv2_srlv import srlv_vmh_delay5

#---------------------------------------------------------------------------
# 19. parcv2-srav tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_srav import srav_no_hazards
from proc.parc.parcv2_srav import srav_hazard_W
from proc.parc.parcv2_srav import srav_hazard_M
from proc.parc.parcv2_srav import srav_hazard_X
from proc.parc.parcv2_srav import srav_vmh_delay0
from proc.parc.parcv2_srav import srav_vmh_delay5

#---------------------------------------------------------------------------
# 20. parcv2-subu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_subu import subu_no_hazards
from proc.parc.parcv2_subu import subu_hazard_W
from proc.parc.parcv2_subu import subu_hazard_M
from proc.parc.parcv2_subu import subu_hazard_X
from proc.parc.parcv2_subu import subu_vmh_delay0
from proc.parc.parcv2_subu import subu_vmh_delay5

#---------------------------------------------------------------------------
# 21. parcv2-and tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_and import and_no_hazards
from proc.parc.parcv2_and import and_hazard_W
from proc.parc.parcv2_and import and_hazard_M
from proc.parc.parcv2_and import and_hazard_X
from proc.parc.parcv2_and import and_vmh_delay0
from proc.parc.parcv2_and import and_vmh_delay5

#---------------------------------------------------------------------------
# 22. parcv2-or tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_or import or_no_hazards
from proc.parc.parcv2_or import or_hazard_W
from proc.parc.parcv2_or import or_hazard_M
from proc.parc.parcv2_or import or_hazard_X
from proc.parc.parcv2_or import or_vmh_delay0
from proc.parc.parcv2_or import or_vmh_delay5

#---------------------------------------------------------------------------
# 23. parcv2-xor tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_xor import xor_no_hazards
from proc.parc.parcv2_xor import xor_hazard_W
from proc.parc.parcv2_xor import xor_hazard_M
from proc.parc.parcv2_xor import xor_hazard_X
from proc.parc.parcv2_xor import xor_vmh_delay0
from proc.parc.parcv2_xor import xor_vmh_delay5

#---------------------------------------------------------------------------
# 24. parcv2-nor tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_nor import nor_no_hazards
from proc.parc.parcv2_nor import nor_hazard_W
from proc.parc.parcv2_nor import nor_hazard_M
from proc.parc.parcv2_nor import nor_hazard_X
from proc.parc.parcv2_nor import nor_vmh_delay0
from proc.parc.parcv2_nor import nor_vmh_delay5

#---------------------------------------------------------------------------
# 25. parcv2-slt tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_slt import slt_no_hazards
from proc.parc.parcv2_slt import slt_hazard_W
from proc.parc.parcv2_slt import slt_hazard_M
from proc.parc.parcv2_slt import slt_hazard_X
from proc.parc.parcv2_slt import slt_vmh_delay0
from proc.parc.parcv2_slt import slt_vmh_delay5

#---------------------------------------------------------------------------
# 26. parcv2-sltu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sltu import sltu_no_hazards
from proc.parc.parcv2_sltu import sltu_hazard_W
from proc.parc.parcv2_sltu import sltu_hazard_M
from proc.parc.parcv2_sltu import sltu_hazard_X
from proc.parc.parcv2_sltu import sltu_vmh_delay0
from proc.parc.parcv2_sltu import sltu_vmh_delay5

#---------------------------------------------------------------------------
# 27. parcv2-mul tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_mul import mul_no_hazards
from proc.parc.parcv2_mul import mul_hazard_W
from proc.parc.parcv2_mul import mul_hazard_M
from proc.parc.parcv2_mul import mul_hazard_X
from proc.parc.parcv2_mul import mul_vmh_delay0
from proc.parc.parcv2_mul import mul_vmh_delay5

#---------------------------------------------------------------------------
# 28. parcv2-div tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_div import div_no_hazards
from proc.parc.parcv2_div import div_hazard_W
from proc.parc.parcv2_div import div_hazard_M
from proc.parc.parcv2_div import div_hazard_X
from proc.parc.parcv2_div import div_vmh_delay0
from proc.parc.parcv2_div import div_vmh_delay5

#---------------------------------------------------------------------------
# 29. parcv2-divu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_divu import divu_no_hazards
from proc.parc.parcv2_divu import divu_hazard_W
from proc.parc.parcv2_divu import divu_hazard_M
from proc.parc.parcv2_divu import divu_hazard_X
from proc.parc.parcv2_divu import divu_vmh_delay0
from proc.parc.parcv2_divu import divu_vmh_delay5

#---------------------------------------------------------------------------
# 30. parcv2-rem tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_rem import rem_no_hazards
from proc.parc.parcv2_rem import rem_hazard_W
from proc.parc.parcv2_rem import rem_hazard_M
from proc.parc.parcv2_rem import rem_hazard_X
from proc.parc.parcv2_rem import rem_vmh_delay0
from proc.parc.parcv2_rem import rem_vmh_delay5

#---------------------------------------------------------------------------
# 31. parcv2-remu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_remu import remu_no_hazards
from proc.parc.parcv2_remu import remu_hazard_W
from proc.parc.parcv2_remu import remu_hazard_M
from proc.parc.parcv2_remu import remu_hazard_X
from proc.parc.parcv2_remu import remu_vmh_delay0
from proc.parc.parcv2_remu import remu_vmh_delay5

#---------------------------------------------------------------------------
# 32. parcv2-lb tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lb import lb_no_hazards
from proc.parc.parcv2_lb import lb_hazard_W
from proc.parc.parcv2_lb import lb_hazard_M
from proc.parc.parcv2_lb import lb_hazard_X
from proc.parc.parcv2_lb import lb_vmh_delay0
from proc.parc.parcv2_lb import lb_vmh_delay5

#---------------------------------------------------------------------------
# 33. parcv2-lbu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lbu import lbu_no_hazards
from proc.parc.parcv2_lbu import lbu_hazard_W
from proc.parc.parcv2_lbu import lbu_hazard_M
from proc.parc.parcv2_lbu import lbu_hazard_X
from proc.parc.parcv2_lbu import lbu_vmh_delay0
from proc.parc.parcv2_lbu import lbu_vmh_delay5

#---------------------------------------------------------------------------
# 34. parcv2-lh tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lh import lh_no_hazards
from proc.parc.parcv2_lh import lh_hazard_W
from proc.parc.parcv2_lh import lh_hazard_M
from proc.parc.parcv2_lh import lh_hazard_X
from proc.parc.parcv2_lh import lh_vmh_delay0
from proc.parc.parcv2_lh import lh_vmh_delay5

#---------------------------------------------------------------------------
# 35. parcv2-lhu tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_lhu import lhu_no_hazards
from proc.parc.parcv2_lhu import lhu_hazard_W
from proc.parc.parcv2_lhu import lhu_hazard_M
from proc.parc.parcv2_lhu import lhu_hazard_X
from proc.parc.parcv2_lhu import lhu_vmh_delay0
from proc.parc.parcv2_lhu import lhu_vmh_delay5

#---------------------------------------------------------------------------
# 36. parcv2-sb tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sb import sb_no_hazards
from proc.parc.parcv2_sb import sb_hazard_W
from proc.parc.parcv2_sb import sb_hazard_M
from proc.parc.parcv2_sb import sb_hazard_X
from proc.parc.parcv2_sb import sb_vmh_delay0
from proc.parc.parcv2_sb import sb_vmh_delay5

#---------------------------------------------------------------------------
# 37. parcv2-sh tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_sh import sh_no_hazards
from proc.parc.parcv2_sh import sh_hazard_W
from proc.parc.parcv2_sh import sh_hazard_M
from proc.parc.parcv2_sh import sh_hazard_X
from proc.parc.parcv2_sh import sh_vmh_delay0
from proc.parc.parcv2_sh import sh_vmh_delay5

#---------------------------------------------------------------------------
# 38. parcv2-j tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_j import j_asm
from proc.parc.parcv2_j import j_vmh_delay0
from proc.parc.parcv2_j import j_vmh_delay5

#---------------------------------------------------------------------------
# 39. parcv2-jalr tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_jalr import jalr_asm
from proc.parc.parcv2_jalr import jalr_vmh_delay0
from proc.parc.parcv2_jalr import jalr_vmh_delay5

#---------------------------------------------------------------------------
# 40. parcv2-beq tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_beq import beq_asm
from proc.parc.parcv2_beq import beq_vmh_delay0
from proc.parc.parcv2_beq import beq_vmh_delay5

#---------------------------------------------------------------------------
# 41. parcv2-blez tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_blez import blez_asm
from proc.parc.parcv2_blez import blez_vmh_delay0
from proc.parc.parcv2_blez import blez_vmh_delay5

#---------------------------------------------------------------------------
# 42. parcv2-bgtz tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bgtz import bgtz_asm
from proc.parc.parcv2_bgtz import bgtz_vmh_delay0
from proc.parc.parcv2_bgtz import bgtz_vmh_delay5

#---------------------------------------------------------------------------
# 43. parcv2-bltz tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bltz import bltz_asm
from proc.parc.parcv2_bltz import bltz_vmh_delay0
from proc.parc.parcv2_bltz import bltz_vmh_delay5

#---------------------------------------------------------------------------
# 44. parcv2-bgez tests
#---------------------------------------------------------------------------

from proc.parc.parcv2_bgez import bgez_asm
from proc.parc.parcv2_bgez import bgez_vmh_delay0
from proc.parc.parcv2_bgez import bgez_vmh_delay5

#---------------------------------------------------------------------------
# tests
#---------------------------------------------------------------------------
tests = [
  mtc2_1x1_delay0,
  mtc2_1x1_delay5,
  mtc2_3x3_delay0,
  mtc2_3x3_delay5,
  j_after_ld_stall,
  mul_scoreboard_clear_bug,
  bypass_from_X,
  addiu_no_hazards,
  addiu_hazard_W,
  addiu_hazard_M,
  addiu_hazard_X,
  addiu_vmh_delay0,
  addiu_vmh_delay5,
  ori_no_hazards,
  ori_hazard_W,
  ori_hazard_M,
  ori_hazard_X,
  ori_vmh_delay0,
  ori_vmh_delay5,
  lui_no_hazards,
  lui_hazard_W,
  lui_hazard_M,
  lui_hazard_X,
  lui_vmh_delay0,
  lui_vmh_delay5,
  addu_no_hazards,
  addu_hazard_W,
  addu_hazard_M,
  addu_hazard_X,
  addu_vmh_delay0,
  addu_vmh_delay5,
  lw_no_hazards,
  lw_hazard_W,
  lw_hazard_M,
  lw_hazard_X,
  lw_vmh_delay0,
  lw_vmh_delay5,
  sw_no_hazards,
  sw_hazard_W,
  sw_hazard_M,
  sw_hazard_X,
  sw_vmh_delay0,
  sw_vmh_delay5,
  jal_asm,
  jal_vmh_delay0,
  jal_vmh_delay5,
  jr_asm,
  jr_vmh_delay0,
  jr_vmh_delay5,
  bne_asm,
  bne_vmh_delay0,
  bne_vmh_delay5,
  andi_no_hazards,
  andi_hazard_W,
  andi_hazard_M,
  andi_hazard_X,
  andi_vmh_delay0,
  andi_vmh_delay5,
  xori_no_hazards,
  xori_hazard_W,
  xori_hazard_M,
  xori_hazard_X,
  xori_vmh_delay0,
  xori_vmh_delay5,
  slti_no_hazards,
  slti_hazard_W,
  slti_hazard_M,
  slti_hazard_X,
  slti_vmh_delay0,
  slti_vmh_delay5,
  sltiu_no_hazards,
  sltiu_hazard_W,
  sltiu_hazard_M,
  sltiu_hazard_X,
  sltiu_vmh_delay0,
  sltiu_vmh_delay5,
  sll_no_hazards,
  sll_hazard_W,
  sll_hazard_M,
  sll_hazard_X,
  sll_vmh_delay0,
  sll_vmh_delay5,
  srl_no_hazards,
  srl_hazard_W,
  srl_hazard_M,
  srl_hazard_X,
  srl_vmh_delay0,
  srl_vmh_delay5,
  sra_no_hazards,
  sra_hazard_W,
  sra_hazard_M,
  sra_hazard_X,
  sra_vmh_delay0,
  sra_vmh_delay5,
  sllv_no_hazards,
  sllv_hazard_W,
  sllv_hazard_M,
  sllv_hazard_X,
  sllv_vmh_delay0,
  sllv_vmh_delay5,
  srlv_no_hazards,
  srlv_hazard_W,
  srlv_hazard_M,
  srlv_hazard_X,
  srlv_vmh_delay0,
  srlv_vmh_delay5,
  srav_no_hazards,
  srav_hazard_W,
  srav_hazard_M,
  srav_hazard_X,
  srav_vmh_delay0,
  srav_vmh_delay5,
  subu_no_hazards,
  subu_hazard_W,
  subu_hazard_M,
  subu_hazard_X,
  subu_vmh_delay0,
  subu_vmh_delay5,
  and_no_hazards,
  and_hazard_W,
  and_hazard_M,
  and_hazard_X,
  and_vmh_delay0,
  and_vmh_delay5,
  or_no_hazards,
  or_hazard_W,
  or_hazard_M,
  or_hazard_X,
  or_vmh_delay0,
  or_vmh_delay5,
  xor_no_hazards,
  xor_hazard_W,
  xor_hazard_M,
  xor_hazard_X,
  xor_vmh_delay0,
  xor_vmh_delay5,
  nor_no_hazards,
  nor_hazard_W,
  nor_hazard_M,
  nor_hazard_X,
  nor_vmh_delay0,
  nor_vmh_delay5,
  slt_no_hazards,
  slt_hazard_W,
  slt_hazard_M,
  slt_hazard_X,
  slt_vmh_delay0,
  slt_vmh_delay5,
  sltu_no_hazards,
  sltu_hazard_W,
  sltu_hazard_M,
  sltu_hazard_X,
  sltu_vmh_delay0,
  sltu_vmh_delay5,
  mul_no_hazards,
  mul_hazard_W,
  mul_hazard_M,
  mul_hazard_X,
  mul_vmh_delay0,
  mul_vmh_delay5,
  div_no_hazards,
  div_hazard_W,
  div_hazard_M,
  div_hazard_X,
  div_vmh_delay0,
  div_vmh_delay5,
  divu_no_hazards,
  divu_hazard_W,
  divu_hazard_M,
  divu_hazard_X,
  divu_vmh_delay0,
  divu_vmh_delay5,
  rem_no_hazards,
  rem_hazard_W,
  rem_hazard_M,
  rem_hazard_X,
  rem_vmh_delay0,
  rem_vmh_delay5,
  remu_no_hazards,
  remu_hazard_W,
  remu_hazard_M,
  remu_hazard_X,
  remu_vmh_delay0,
  remu_vmh_delay5,
  lb_no_hazards,
  lb_hazard_W,
  lb_hazard_M,
  lb_hazard_X,
  lb_vmh_delay0,
  lb_vmh_delay5,
  lbu_no_hazards,
  lbu_hazard_W,
  lbu_hazard_M,
  lbu_hazard_X,
  lbu_vmh_delay0,
  lbu_vmh_delay5,
  lh_no_hazards,
  lh_hazard_W,
  lh_hazard_M,
  lh_hazard_X,
  lh_vmh_delay0,
  lh_vmh_delay5,
  lhu_no_hazards,
  lhu_hazard_W,
  lhu_hazard_M,
  lhu_hazard_X,
  lhu_vmh_delay0,
  lhu_vmh_delay5,
  sb_no_hazards,
  sb_hazard_W,
  sb_hazard_M,
  sb_hazard_X,
  sb_vmh_delay0,
  sb_vmh_delay5,
  sh_no_hazards,
  sh_hazard_W,
  sh_hazard_M,
  sh_hazard_X,
  sh_vmh_delay0,
  sh_vmh_delay5,
  j_asm,
  j_vmh_delay0,
  j_vmh_delay5,
  jalr_asm,
  jalr_vmh_delay0,
  jalr_vmh_delay5,
  beq_asm,
  beq_vmh_delay0,
  beq_vmh_delay5,
  blez_asm,
  blez_vmh_delay0,
  blez_vmh_delay5,
  bgtz_asm,
  bgtz_vmh_delay0,
  bgtz_vmh_delay5,
  bltz_asm,
  bltz_vmh_delay0,
  bltz_vmh_delay5,
  bgez_asm,
  bgez_vmh_delay0,
  bgez_vmh_delay5,
]

#===========================================================================
# pytest fixtures
#===========================================================================

def pytest_generate_tests( metafunc ):

  if 'xcel_type' in metafunc.fixturenames:

    # Only use tests with RTL dotprod when the test_verilog flag is true!
    if metafunc.config.option.test_verilog:
      configurations = ['rtl']
    # Perform tests on both FL and RTL dotprod impls otherwise
    else:
      configurations = ['fl', 'rtl']

    metafunc.parametrize('xcel_type', configurations, indirect=False )

@pytest.fixture
def xcel_type( request ):
  return request.param

#---------------------------------------------------------------------------
# config_test
#---------------------------------------------------------------------------
# Create nice names for tests and decorate with requires_vmh/requires_xcc
# depending on the function name.
def config_test( func ):
  name = func.func_name
  mark = requires_vmh if 'vmh' in name else requires_xcc
  return mark((name, func))

#---------------------------------------------------------------------------
# test_tile
#---------------------------------------------------------------------------
@pytest.mark.parametrize( 'name,asm_test',
  [ config_test( t ) for t in tests ]
)
def test_tile( dump_vcd, test_verilog, xcel_type, name, asm_test ):
  vcd_file_name = '{}.vcd'.format( name ),
  run_proc_test( xcel_type, test_verilog, dump_vcd, vcd_file_name, asm_test() )

