#=========================================================================
# ParcProc5stStall_test.py
#=========================================================================
# ParcProc5stStall assembly tests driver

from test_runner import run_stall_proc_test
from new_pymtl   import requires_xcc, requires_vmh

#---------------------------------------------------------------------------
# 1. parcv1-addiu tests
#---------------------------------------------------------------------------

from parcv1_addiu import addiu_no_hazards
from parcv1_addiu import addiu_hazard_W
from parcv1_addiu import addiu_hazard_M
from parcv1_addiu import addiu_hazard_X
from parcv1_addiu import addiu_vmh_delay0
from parcv1_addiu import addiu_vmh_delay5

@requires_xcc
def test_stall_addiu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_no_hazards.vcd",
                       addiu_no_hazards() )

@requires_xcc
def test_stall_addiu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_hazard_W.vcd",
                       addiu_hazard_W() )

@requires_xcc
def test_stall_addiu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_hazard_M.vcd",
                       addiu_hazard_M() )

@requires_xcc
def test_stall_addiu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_hazard_X.vcd",
                       addiu_hazard_X() )

@requires_vmh
def test_stall_addiu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_vmh_delay0.vcd",
                       addiu_vmh_delay0() )

@requires_vmh
def test_stall_addiu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addiu_vmh_delay5.vcd",
                       addiu_vmh_delay5() )

#---------------------------------------------------------------------------
# 2. parcv1-ori tests
#---------------------------------------------------------------------------

from parcv1_ori import ori_no_hazards
from parcv1_ori import ori_hazard_W
from parcv1_ori import ori_hazard_M
from parcv1_ori import ori_hazard_X
from parcv1_ori import ori_vmh_delay0
from parcv1_ori import ori_vmh_delay5

@requires_xcc
def test_stall_ori_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_no_hazards.vcd",
                       ori_no_hazards() )

@requires_xcc
def test_stall_ori_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_hazard_W.vcd",
                       ori_hazard_W() )

@requires_xcc
def test_stall_ori_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_hazard_M.vcd",
                       ori_hazard_M() )

@requires_xcc
def test_stall_ori_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_hazard_X.vcd",
                       ori_hazard_X() )

@requires_vmh
def test_stall_ori_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_vmh_delay0.vcd",
                       ori_vmh_delay0() )

@requires_vmh
def test_stall_ori_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_ori_vmh_delay5.vcd",
                       ori_vmh_delay5() )

#---------------------------------------------------------------------------
# 3. parcv1-lui tests
#---------------------------------------------------------------------------

from parcv1_lui import lui_no_hazards
from parcv1_lui import lui_hazard_W
from parcv1_lui import lui_hazard_M
from parcv1_lui import lui_hazard_X
from parcv1_lui import lui_vmh_delay0
from parcv1_lui import lui_vmh_delay5

@requires_xcc
def test_stall_lui_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_no_hazards.vcd",
                       lui_no_hazards() )

@requires_xcc
def test_stall_lui_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_hazard_W.vcd",
                       lui_hazard_W() )

@requires_xcc
def test_stall_lui_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_hazard_M.vcd",
                       lui_hazard_M() )

@requires_xcc
def test_stall_lui_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_hazard_X.vcd",
                       lui_hazard_X() )

@requires_vmh
def test_stall_lui_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_vmh_delay0.vcd",
                       lui_vmh_delay0() )

@requires_vmh
def test_stall_lui_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lui_vmh_delay5.vcd",
                       lui_vmh_delay5() )

#---------------------------------------------------------------------------
# 4. parcv1-addu tests
#---------------------------------------------------------------------------

from parcv1_addu import addu_no_hazards
from parcv1_addu import addu_hazard_W
from parcv1_addu import addu_hazard_M
from parcv1_addu import addu_hazard_X
from parcv1_addu import addu_vmh_delay0
from parcv1_addu import addu_vmh_delay5

@requires_xcc
def test_stall_addu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_no_hazards.vcd",
                       addu_no_hazards() )

@requires_xcc
def test_stall_addu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_hazard_W.vcd",
                       addu_hazard_W() )

@requires_xcc
def test_stall_addu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_hazard_M.vcd",
                       addu_hazard_M() )

@requires_xcc
def test_stall_addu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_hazard_X.vcd",
                       addu_hazard_X() )

@requires_vmh
def test_stall_addu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_vmh_delay0.vcd",
                       addu_vmh_delay0() )

@requires_vmh
def test_stall_addu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_addu_vmh_delay5.vcd",
                       addu_vmh_delay5() )

#---------------------------------------------------------------------------
# 5. parcv1-lw tests
#---------------------------------------------------------------------------

from parcv1_lw import lw_no_hazards
from parcv1_lw import lw_hazard_W
from parcv1_lw import lw_hazard_M
from parcv1_lw import lw_hazard_X
from parcv1_lw import lw_vmh_delay0
from parcv1_lw import lw_vmh_delay5

@requires_xcc
def test_stall_lw_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_no_hazards.vcd",
                       lw_no_hazards() )

@requires_xcc
def test_stall_lw_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_hazard_W.vcd",
                       lw_hazard_W() )

@requires_xcc
def test_stall_lw_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_hazard_M.vcd",
                       lw_hazard_M() )

@requires_xcc
def test_stall_lw_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_hazard_X.vcd",
                       lw_hazard_X() )

@requires_vmh
def test_stall_lw_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_vmh_delay0.vcd",
                       lw_vmh_delay0() )

@requires_vmh
def test_stall_lw_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lw_vmh_delay5.vcd",
                       lw_vmh_delay5() )

#---------------------------------------------------------------------------
# 6. parcv1-sw tests
#---------------------------------------------------------------------------

from parcv1_sw import sw_no_hazards
from parcv1_sw import sw_hazard_W
from parcv1_sw import sw_hazard_M
from parcv1_sw import sw_hazard_X
from parcv1_sw import sw_vmh_delay0
from parcv1_sw import sw_vmh_delay5

@requires_xcc
def test_stall_sw_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_no_hazards.vcd",
                       sw_no_hazards() )

@requires_xcc
def test_stall_sw_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_hazard_W.vcd",
                       sw_hazard_W() )

@requires_xcc
def test_stall_sw_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_hazard_M.vcd",
                       sw_hazard_M() )

@requires_xcc
def test_stall_sw_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_hazard_X.vcd",
                       sw_hazard_X() )

@requires_vmh
def test_stall_sw_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_vmh_delay0.vcd",
                       sw_vmh_delay0() )

@requires_vmh
def test_stall_sw_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sw_vmh_delay5.vcd",
                       sw_vmh_delay5() )

#---------------------------------------------------------------------------
# 7. parcv1-jal tests
#---------------------------------------------------------------------------

from parcv1_jal import jal_asm
from parcv1_jal import jal_vmh_delay0
from parcv1_jal import jal_vmh_delay5

@requires_xcc
def test_stall_jal_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jal.vcd",
                       jal_asm() )

@requires_vmh
def test_stall_jal_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jal_vmh_delay0.vcd",
                       jal_vmh_delay0() )

@requires_vmh
def test_stall_jal_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jal_vmh_delay5.vcd",
                       jal_vmh_delay5() )

#---------------------------------------------------------------------------
# 8. parcv1-jr tests
#---------------------------------------------------------------------------

from parcv1_jr import jr_asm
from parcv1_jr import jr_vmh_delay0
from parcv1_jr import jr_vmh_delay5

@requires_xcc
def test_stall_jr_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jr.vcd",
                       jr_asm() )

@requires_vmh
def test_stall_jr_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jr_vmh_delay0.vcd",
                       jr_vmh_delay0() )

@requires_vmh
def test_stall_jr_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jr_vmh_delay5.vcd",
                       jr_vmh_delay5() )

#---------------------------------------------------------------------------
# 9. parcv1-bne tests
#---------------------------------------------------------------------------

from parcv1_bne import bne_asm
from parcv1_bne import bne_vmh_delay0
from parcv1_bne import bne_vmh_delay5

@requires_xcc
def test_stall_bne_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bne.vcd",
                       bne_asm() )

@requires_vmh
def test_stall_bne_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bne_vmh_delay0.vcd",
                       bne_vmh_delay0() )

@requires_vmh
def test_stall_bne_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bne_vmh_delay5.vcd",
                       bne_vmh_delay5() )

#---------------------------------------------------------------------------
# 10. parcv2-andi tests
#---------------------------------------------------------------------------

from parcv2_andi import andi_no_hazards
from parcv2_andi import andi_hazard_W
from parcv2_andi import andi_hazard_M
from parcv2_andi import andi_hazard_X
from parcv2_andi import andi_vmh_delay0
from parcv2_andi import andi_vmh_delay5

@requires_xcc
def test_stall_andi_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_no_hazards.vcd",
                       andi_no_hazards() )

@requires_xcc
def test_stall_andi_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_hazard_W.vcd",
                       andi_hazard_W() )

@requires_xcc
def test_stall_andi_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_hazard_M.vcd",
                       andi_hazard_M() )

@requires_xcc
def test_stall_andi_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_hazard_X.vcd",
                       andi_hazard_X() )

@requires_vmh
def test_stall_andi_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_vmh_delay0.vcd",
                       andi_vmh_delay0() )

@requires_vmh
def test_stall_andi_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_andi_vmh_delay5.vcd",
                       andi_vmh_delay5() )

#---------------------------------------------------------------------------
# 11. parcv2-xori tests
#---------------------------------------------------------------------------

from parcv2_xori import xori_no_hazards
from parcv2_xori import xori_hazard_W
from parcv2_xori import xori_hazard_M
from parcv2_xori import xori_hazard_X
from parcv2_xori import xori_vmh_delay0
from parcv2_xori import xori_vmh_delay5

@requires_xcc
def test_stall_xori_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_no_hazards.vcd",
                       xori_no_hazards() )

@requires_xcc
def test_stall_xori_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_hazard_W.vcd",
                       xori_hazard_W() )

@requires_xcc
def test_stall_xori_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_hazard_M.vcd",
                       xori_hazard_M() )

@requires_xcc
def test_stall_xori_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_hazard_X.vcd",
                       xori_hazard_X() )

@requires_vmh
def test_stall_xori_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_vmh_delay0.vcd",
                       xori_vmh_delay0() )

@requires_vmh
def test_stall_xori_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xori_vmh_delay5.vcd",
                       xori_vmh_delay5() )

#---------------------------------------------------------------------------
# 12. parcv2-slti tests
#---------------------------------------------------------------------------

from parcv2_slti import slti_no_hazards
from parcv2_slti import slti_hazard_W
from parcv2_slti import slti_hazard_M
from parcv2_slti import slti_hazard_X
from parcv2_slti import slti_vmh_delay0
from parcv2_slti import slti_vmh_delay5

@requires_xcc
def test_stall_slti_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_no_hazards.vcd",
                       slti_no_hazards() )

@requires_xcc
def test_stall_slti_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_hazard_W.vcd",
                       slti_hazard_W() )

@requires_xcc
def test_stall_slti_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_hazard_M.vcd",
                       slti_hazard_M() )

@requires_xcc
def test_stall_slti_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_hazard_X.vcd",
                       slti_hazard_X() )

@requires_vmh
def test_stall_slti_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_vmh_delay0.vcd",
                       slti_vmh_delay0() )

@requires_vmh
def test_stall_slti_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slti_vmh_delay5.vcd",
                       slti_vmh_delay5() )

#---------------------------------------------------------------------------
# 13. parcv2-sltiu tests
#---------------------------------------------------------------------------

from parcv2_sltiu import sltiu_no_hazards
from parcv2_sltiu import sltiu_hazard_W
from parcv2_sltiu import sltiu_hazard_M
from parcv2_sltiu import sltiu_hazard_X
from parcv2_sltiu import sltiu_vmh_delay0
from parcv2_sltiu import sltiu_vmh_delay5

@requires_xcc
def test_stall_sltiu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_no_hazards.vcd",
                       sltiu_no_hazards() )

@requires_xcc
def test_stall_sltiu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_hazard_W.vcd",
                       sltiu_hazard_W() )

@requires_xcc
def test_stall_sltiu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_hazard_M.vcd",
                       sltiu_hazard_M() )

@requires_xcc
def test_stall_sltiu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_hazard_X.vcd",
                       sltiu_hazard_X() )

@requires_vmh
def test_stall_sltiu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_vmh_delay0.vcd",
                       sltiu_vmh_delay0() )

@requires_vmh
def test_stall_sltiu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltiu_vmh_delay5.vcd",
                       sltiu_vmh_delay5() )

#---------------------------------------------------------------------------
# 14. parcv2-sll tests
#---------------------------------------------------------------------------

from parcv2_sll import sll_no_hazards
from parcv2_sll import sll_hazard_W
from parcv2_sll import sll_hazard_M
from parcv2_sll import sll_hazard_X
from parcv2_sll import sll_vmh_delay0
from parcv2_sll import sll_vmh_delay5

@requires_xcc
def test_stall_sll_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_no_hazards.vcd",
                       sll_no_hazards() )

@requires_xcc
def test_stall_sll_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_hazard_W.vcd",
                       sll_hazard_W() )

@requires_xcc
def test_stall_sll_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_hazard_M.vcd",
                       sll_hazard_M() )

@requires_xcc
def test_stall_sll_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_hazard_X.vcd",
                       sll_hazard_X() )

@requires_vmh
def test_stall_sll_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_vmh_delay0.vcd",
                       sll_vmh_delay0() )

@requires_vmh
def test_stall_sll_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sll_vmh_delay5.vcd",
                       sll_vmh_delay5() )

#---------------------------------------------------------------------------
# 15. parcv2-srl tests
#---------------------------------------------------------------------------

from parcv2_srl import srl_no_hazards
from parcv2_srl import srl_hazard_W
from parcv2_srl import srl_hazard_M
from parcv2_srl import srl_hazard_X
from parcv2_srl import srl_vmh_delay0
from parcv2_srl import srl_vmh_delay5

@requires_xcc
def test_stall_srl_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_no_hazards.vcd",
                       srl_no_hazards() )

@requires_xcc
def test_stall_srl_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_hazard_W.vcd",
                       srl_hazard_W() )

@requires_xcc
def test_stall_srl_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_hazard_M.vcd",
                       srl_hazard_M() )

@requires_xcc
def test_stall_srl_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_hazard_X.vcd",
                       srl_hazard_X() )

@requires_vmh
def test_stall_srl_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_vmh_delay0.vcd",
                       srl_vmh_delay0() )

@requires_vmh
def test_stall_srl_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srl_vmh_delay5.vcd",
                       srl_vmh_delay5() )

#---------------------------------------------------------------------------
# 16. parcv2-sra tests
#---------------------------------------------------------------------------

from parcv2_sra import sra_no_hazards
from parcv2_sra import sra_hazard_W
from parcv2_sra import sra_hazard_M
from parcv2_sra import sra_hazard_X
from parcv2_sra import sra_vmh_delay0
from parcv2_sra import sra_vmh_delay5

@requires_xcc
def test_stall_sra_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_no_hazards.vcd",
                       sra_no_hazards() )

@requires_xcc
def test_stall_sra_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_hazard_W.vcd",
                       sra_hazard_W() )

@requires_xcc
def test_stall_sra_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_hazard_M.vcd",
                       sra_hazard_M() )

@requires_xcc
def test_stall_sra_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_hazard_X.vcd",
                       sra_hazard_X() )

@requires_vmh
def test_stall_sra_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_vmh_delay0.vcd",
                       sra_vmh_delay0() )

@requires_vmh
def test_stall_sra_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sra_vmh_delay5.vcd",
                       sra_vmh_delay5() )

#---------------------------------------------------------------------------
# 17. parcv2-sllv tests
#---------------------------------------------------------------------------

from parcv2_sllv import sllv_no_hazards
from parcv2_sllv import sllv_hazard_W
from parcv2_sllv import sllv_hazard_M
from parcv2_sllv import sllv_hazard_X
from parcv2_sllv import sllv_vmh_delay0
from parcv2_sllv import sllv_vmh_delay5

@requires_xcc
def test_stall_sllv_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_no_hazards.vcd",
                       sllv_no_hazards() )

@requires_xcc
def test_stall_sllv_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_hazard_W.vcd",
                       sllv_hazard_W() )

@requires_xcc
def test_stall_sllv_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_hazard_M.vcd",
                       sllv_hazard_M() )

@requires_xcc
def test_stall_sllv_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_hazard_X.vcd",
                       sllv_hazard_X() )

@requires_vmh
def test_stall_sllv_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_vmh_delay0.vcd",
                       sllv_vmh_delay0() )

@requires_vmh
def test_stall_sllv_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sllv_vmh_delay5.vcd",
                       sllv_vmh_delay5() )

#---------------------------------------------------------------------------
# 18. parcv2-srlv tests
#---------------------------------------------------------------------------

from parcv2_srlv import srlv_no_hazards
from parcv2_srlv import srlv_hazard_W
from parcv2_srlv import srlv_hazard_M
from parcv2_srlv import srlv_hazard_X
from parcv2_srlv import srlv_vmh_delay0
from parcv2_srlv import srlv_vmh_delay5

@requires_xcc
def test_stall_srlv_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_no_hazards.vcd",
                       srlv_no_hazards() )

@requires_xcc
def test_stall_srlv_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_hazard_W.vcd",
                       srlv_hazard_W() )

@requires_xcc
def test_stall_srlv_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_hazard_M.vcd",
                       srlv_hazard_M() )

@requires_xcc
def test_stall_srlv_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_hazard_X.vcd",
                       srlv_hazard_X() )

@requires_vmh
def test_stall_srlv_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_vmh_delay0.vcd",
                       srlv_vmh_delay0() )

@requires_vmh
def test_stall_srlv_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srlv_vmh_delay5.vcd",
                       srlv_vmh_delay5() )

#---------------------------------------------------------------------------
# 19. parcv2-srav tests
#---------------------------------------------------------------------------

from parcv2_srav import srav_no_hazards
from parcv2_srav import srav_hazard_W
from parcv2_srav import srav_hazard_M
from parcv2_srav import srav_hazard_X
from parcv2_srav import srav_vmh_delay0
from parcv2_srav import srav_vmh_delay5

@requires_xcc
def test_stall_srav_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_no_hazards.vcd",
                       srav_no_hazards() )

@requires_xcc
def test_stall_srav_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_hazard_W.vcd",
                       srav_hazard_W() )

@requires_xcc
def test_stall_srav_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_hazard_M.vcd",
                       srav_hazard_M() )

@requires_xcc
def test_stall_srav_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_hazard_X.vcd",
                       srav_hazard_X() )

@requires_vmh
def test_stall_srav_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_vmh_delay0.vcd",
                       srav_vmh_delay0() )

@requires_vmh
def test_stall_srav_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_srav_vmh_delay5.vcd",
                       srav_vmh_delay5() )

#---------------------------------------------------------------------------
# 20. parcv2-subu tests
#---------------------------------------------------------------------------

from parcv2_subu import subu_no_hazards
from parcv2_subu import subu_hazard_W
from parcv2_subu import subu_hazard_M
from parcv2_subu import subu_hazard_X
from parcv2_subu import subu_vmh_delay0
from parcv2_subu import subu_vmh_delay5

@requires_xcc
def test_stall_subu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_no_hazards.vcd",
                       subu_no_hazards() )

@requires_xcc
def test_stall_subu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_hazard_W.vcd",
                       subu_hazard_W() )

@requires_xcc
def test_stall_subu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_hazard_M.vcd",
                       subu_hazard_M() )

@requires_xcc
def test_stall_subu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_hazard_X.vcd",
                       subu_hazard_X() )

@requires_vmh
def test_stall_subu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_vmh_delay0.vcd",
                       subu_vmh_delay0() )

@requires_vmh
def test_stall_subu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_subu_vmh_delay5.vcd",
                       subu_vmh_delay5() )

#---------------------------------------------------------------------------
# 21. parcv2-and tests
#---------------------------------------------------------------------------

from parcv2_and import and_no_hazards
from parcv2_and import and_hazard_W
from parcv2_and import and_hazard_M
from parcv2_and import and_hazard_X
from parcv2_and import and_vmh_delay0
from parcv2_and import and_vmh_delay5

@requires_xcc
def test_stall_and_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_no_hazards.vcd",
                       and_no_hazards() )

@requires_xcc
def test_stall_and_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_hazard_W.vcd",
                       and_hazard_W() )

@requires_xcc
def test_stall_and_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_hazard_M.vcd",
                       and_hazard_M() )

@requires_xcc
def test_stall_and_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_hazard_X.vcd",
                       and_hazard_X() )

@requires_vmh
def test_stall_and_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_vmh_delay0.vcd",
                       and_vmh_delay0() )

@requires_vmh
def test_stall_and_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_and_vmh_delay5.vcd",
                       and_vmh_delay5() )

#---------------------------------------------------------------------------
# 22. parcv2-or tests
#---------------------------------------------------------------------------

from parcv2_or import or_no_hazards
from parcv2_or import or_hazard_W
from parcv2_or import or_hazard_M
from parcv2_or import or_hazard_X
from parcv2_or import or_vmh_delay0
from parcv2_or import or_vmh_delay5

@requires_xcc
def test_stall_or_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_no_hazards.vcd",
                       or_no_hazards() )

@requires_xcc
def test_stall_or_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_hazard_W.vcd",
                       or_hazard_W() )

@requires_xcc
def test_stall_or_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_hazard_M.vcd",
                       or_hazard_M() )

@requires_xcc
def test_stall_or_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_hazard_X.vcd",
                       or_hazard_X() )

@requires_vmh
def test_stall_or_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_vmh_delay0.vcd",
                       or_vmh_delay0() )

@requires_vmh
def test_stall_or_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_or_vmh_delay5.vcd",
                       or_vmh_delay5() )

#---------------------------------------------------------------------------
# 23. parcv2-xor tests
#---------------------------------------------------------------------------

from parcv2_xor import xor_no_hazards
from parcv2_xor import xor_hazard_W
from parcv2_xor import xor_hazard_M
from parcv2_xor import xor_hazard_X
from parcv2_xor import xor_vmh_delay0
from parcv2_xor import xor_vmh_delay5

@requires_xcc
def test_stall_xor_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_no_hazards.vcd",
                       xor_no_hazards() )

@requires_xcc
def test_stall_xor_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_hazard_W.vcd",
                       xor_hazard_W() )

@requires_xcc
def test_stall_xor_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_hazard_M.vcd",
                       xor_hazard_M() )

@requires_xcc
def test_stall_xor_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_hazard_X.vcd",
                       xor_hazard_X() )

@requires_vmh
def test_stall_xor_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_vmh_delay0.vcd",
                       xor_vmh_delay0() )

@requires_vmh
def test_stall_xor_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_xor_vmh_delay5.vcd",
                       xor_vmh_delay5() )

#---------------------------------------------------------------------------
# 24. parcv2-nor tests
#---------------------------------------------------------------------------

from parcv2_nor import nor_no_hazards
from parcv2_nor import nor_hazard_W
from parcv2_nor import nor_hazard_M
from parcv2_nor import nor_hazard_X
from parcv2_nor import nor_vmh_delay0
from parcv2_nor import nor_vmh_delay5

@requires_xcc
def test_stall_nor_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_no_hazards.vcd",
                       nor_no_hazards() )

@requires_xcc
def test_stall_nor_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_hazard_W.vcd",
                       nor_hazard_W() )

@requires_xcc
def test_stall_nor_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_hazard_M.vcd",
                       nor_hazard_M() )

@requires_xcc
def test_stall_nor_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_hazard_X.vcd",
                       nor_hazard_X() )

@requires_vmh
def test_stall_nor_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_vmh_delay0.vcd",
                       nor_vmh_delay0() )

@requires_vmh
def test_stall_nor_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_nor_vmh_delay5.vcd",
                       nor_vmh_delay5() )

#---------------------------------------------------------------------------
# 25. parcv2-slt tests
#---------------------------------------------------------------------------

from parcv2_slt import slt_no_hazards
from parcv2_slt import slt_hazard_W
from parcv2_slt import slt_hazard_M
from parcv2_slt import slt_hazard_X
from parcv2_slt import slt_vmh_delay0
from parcv2_slt import slt_vmh_delay5

@requires_xcc
def test_stall_slt_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_no_hazards.vcd",
                       slt_no_hazards() )

@requires_xcc
def test_stall_slt_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_hazard_W.vcd",
                       slt_hazard_W() )

@requires_xcc
def test_stall_slt_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_hazard_M.vcd",
                       slt_hazard_M() )

@requires_xcc
def test_stall_slt_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_hazard_X.vcd",
                       slt_hazard_X() )

@requires_vmh
def test_stall_slt_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_vmh_delay0.vcd",
                       slt_vmh_delay0() )

@requires_vmh
def test_stall_slt_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_slt_vmh_delay5.vcd",
                       slt_vmh_delay5() )

#---------------------------------------------------------------------------
# 26. parcv2-sltu tests
#---------------------------------------------------------------------------

from parcv2_sltu import sltu_no_hazards
from parcv2_sltu import sltu_hazard_W
from parcv2_sltu import sltu_hazard_M
from parcv2_sltu import sltu_hazard_X
from parcv2_sltu import sltu_vmh_delay0
from parcv2_sltu import sltu_vmh_delay5

@requires_xcc
def test_stall_sltu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_no_hazards.vcd",
                       sltu_no_hazards() )

@requires_xcc
def test_stall_sltu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_hazard_W.vcd",
                       sltu_hazard_W() )

@requires_xcc
def test_stall_sltu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_hazard_M.vcd",
                       sltu_hazard_M() )

@requires_xcc
def test_stall_sltu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_hazard_X.vcd",
                       sltu_hazard_X() )

@requires_vmh
def test_stall_sltu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_vmh_delay0.vcd",
                       sltu_vmh_delay0() )

@requires_vmh
def test_stall_sltu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sltu_vmh_delay5.vcd",
                       sltu_vmh_delay5() )

#---------------------------------------------------------------------------
# 27. parcv2-mul tests
#---------------------------------------------------------------------------

from parcv2_mul import mul_no_hazards
from parcv2_mul import mul_hazard_W
from parcv2_mul import mul_hazard_M
from parcv2_mul import mul_hazard_X
from parcv2_mul import mul_vmh_delay0
from parcv2_mul import mul_vmh_delay5

@requires_xcc
def test_stall_mul_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_no_hazards.vcd",
                       mul_no_hazards() )

@requires_xcc
def test_stall_mul_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_hazard_W.vcd",
                       mul_hazard_W() )

@requires_xcc
def test_stall_mul_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_hazard_M.vcd",
                       mul_hazard_M() )

@requires_xcc
def test_stall_mul_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_hazard_X.vcd",
                       mul_hazard_X() )

@requires_vmh
def test_stall_mul_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_vmh_delay0.vcd",
                       mul_vmh_delay0() )

@requires_vmh
def test_stall_mul_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_mul_vmh_delay5.vcd",
                       mul_vmh_delay5() )

#---------------------------------------------------------------------------
# 28. parcv2-div tests
#---------------------------------------------------------------------------

from parcv2_div import div_no_hazards
from parcv2_div import div_hazard_W
from parcv2_div import div_hazard_M
from parcv2_div import div_hazard_X
from parcv2_div import div_vmh_delay0
from parcv2_div import div_vmh_delay5

@requires_xcc
def test_stall_div_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_no_hazards.vcd",
                       div_no_hazards() )

@requires_xcc
def test_stall_div_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_hazard_W.vcd",
                       div_hazard_W() )

@requires_xcc
def test_stall_div_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_hazard_M.vcd",
                       div_hazard_M() )

@requires_xcc
def test_stall_div_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_hazard_X.vcd",
                       div_hazard_X() )

@requires_vmh
def test_stall_div_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_vmh_delay0.vcd",
                       div_vmh_delay0() )

@requires_vmh
def test_stall_div_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_div_vmh_delay5.vcd",
                       div_vmh_delay5() )

#---------------------------------------------------------------------------
# 29. parcv2-divu tests
#---------------------------------------------------------------------------

from parcv2_divu import divu_no_hazards
from parcv2_divu import divu_hazard_W
from parcv2_divu import divu_hazard_M
from parcv2_divu import divu_hazard_X
from parcv2_divu import divu_vmh_delay0
from parcv2_divu import divu_vmh_delay5

@requires_xcc
def test_stall_divu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_no_hazards.vcd",
                       divu_no_hazards() )

@requires_xcc
def test_stall_divu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_hazard_W.vcd",
                       divu_hazard_W() )

@requires_xcc
def test_stall_divu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_hazard_M.vcd",
                       divu_hazard_M() )

@requires_xcc
def test_stall_divu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_hazard_X.vcd",
                       divu_hazard_X() )

@requires_vmh
def test_stall_divu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_vmh_delay0.vcd",
                       divu_vmh_delay0() )

@requires_vmh
def test_stall_divu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_divu_vmh_delay5.vcd",
                       divu_vmh_delay5() )

#---------------------------------------------------------------------------
# 30. parcv2-rem tests
#---------------------------------------------------------------------------

from parcv2_rem import rem_no_hazards
from parcv2_rem import rem_hazard_W
from parcv2_rem import rem_hazard_M
from parcv2_rem import rem_hazard_X
from parcv2_rem import rem_vmh_delay0
from parcv2_rem import rem_vmh_delay5

@requires_xcc
def test_stall_rem_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_no_hazards.vcd",
                       rem_no_hazards() )

@requires_xcc
def test_stall_rem_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_hazard_W.vcd",
                       rem_hazard_W() )

@requires_xcc
def test_stall_rem_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_hazard_M.vcd",
                       rem_hazard_M() )

@requires_xcc
def test_stall_rem_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_hazard_X.vcd",
                       rem_hazard_X() )

@requires_vmh
def test_stall_rem_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_vmh_delay0.vcd",
                       rem_vmh_delay0() )

@requires_vmh
def test_stall_rem_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_rem_vmh_delay5.vcd",
                       rem_vmh_delay5() )

#---------------------------------------------------------------------------
# 31. parcv2-remu tests
#---------------------------------------------------------------------------

from parcv2_remu import remu_no_hazards
from parcv2_remu import remu_hazard_W
from parcv2_remu import remu_hazard_M
from parcv2_remu import remu_hazard_X
from parcv2_remu import remu_vmh_delay0
from parcv2_remu import remu_vmh_delay5

@requires_xcc
def test_stall_remu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_no_hazards.vcd",
                       remu_no_hazards() )

@requires_xcc
def test_stall_remu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_hazard_W.vcd",
                       remu_hazard_W() )

@requires_xcc
def test_stall_remu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_hazard_M.vcd",
                       remu_hazard_M() )

@requires_xcc
def test_stall_remu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_hazard_X.vcd",
                       remu_hazard_X() )

@requires_vmh
def test_stall_remu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_vmh_delay0.vcd",
                       remu_vmh_delay0() )

@requires_vmh
def test_stall_remu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_remu_vmh_delay5.vcd",
                       remu_vmh_delay5() )

#---------------------------------------------------------------------------
# 32. parcv2-lb tests
#---------------------------------------------------------------------------

from parcv2_lb import lb_no_hazards
from parcv2_lb import lb_hazard_W
from parcv2_lb import lb_hazard_M
from parcv2_lb import lb_hazard_X
from parcv2_lb import lb_vmh_delay0
from parcv2_lb import lb_vmh_delay5

@requires_xcc
def test_stall_lb_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_no_hazards.vcd",
                       lb_no_hazards() )

@requires_xcc
def test_stall_lb_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_hazard_W.vcd",
                       lb_hazard_W() )

@requires_xcc
def test_stall_lb_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_hazard_M.vcd",
                       lb_hazard_M() )

@requires_xcc
def test_stall_lb_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_hazard_X.vcd",
                       lb_hazard_X() )

@requires_vmh
def test_stall_lb_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_vmh_delay0.vcd",
                       lb_vmh_delay0() )

@requires_vmh
def test_stall_lb_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lb_vmh_delay5.vcd",
                       lb_vmh_delay5() )

#---------------------------------------------------------------------------
# 33. parcv2-lbu tests
#---------------------------------------------------------------------------

from parcv2_lbu import lbu_no_hazards
from parcv2_lbu import lbu_hazard_W
from parcv2_lbu import lbu_hazard_M
from parcv2_lbu import lbu_hazard_X
from parcv2_lbu import lbu_vmh_delay0
from parcv2_lbu import lbu_vmh_delay5

@requires_xcc
def test_stall_lbu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_no_hazards.vcd",
                       lbu_no_hazards() )

@requires_xcc
def test_stall_lbu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_hazard_W.vcd",
                       lbu_hazard_W() )

@requires_xcc
def test_stall_lbu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_hazard_M.vcd",
                       lbu_hazard_M() )

@requires_xcc
def test_stall_lbu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_hazard_X.vcd",
                       lbu_hazard_X() )

@requires_vmh
def test_stall_lbu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_vmh_delay0.vcd",
                       lbu_vmh_delay0() )

@requires_vmh
def test_stall_lbu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lbu_vmh_delay5.vcd",
                       lbu_vmh_delay5() )

#---------------------------------------------------------------------------
# 34. parcv2-lh tests
#---------------------------------------------------------------------------

from parcv2_lh import lh_no_hazards
from parcv2_lh import lh_hazard_W
from parcv2_lh import lh_hazard_M
from parcv2_lh import lh_hazard_X
from parcv2_lh import lh_vmh_delay0
from parcv2_lh import lh_vmh_delay5

@requires_xcc
def test_stall_lh_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_no_hazards.vcd",
                       lh_no_hazards() )

@requires_xcc
def test_stall_lh_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_hazard_W.vcd",
                       lh_hazard_W() )

@requires_xcc
def test_stall_lh_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_hazard_M.vcd",
                       lh_hazard_M() )

@requires_xcc
def test_stall_lh_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_hazard_X.vcd",
                       lh_hazard_X() )

@requires_vmh
def test_stall_lh_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_vmh_delay0.vcd",
                       lh_vmh_delay0() )

@requires_vmh
def test_stall_lh_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lh_vmh_delay5.vcd",
                       lh_vmh_delay5() )

#---------------------------------------------------------------------------
# 35. parcv2-lhu tests
#---------------------------------------------------------------------------

from parcv2_lhu import lhu_no_hazards
from parcv2_lhu import lhu_hazard_W
from parcv2_lhu import lhu_hazard_M
from parcv2_lhu import lhu_hazard_X
from parcv2_lhu import lhu_vmh_delay0
from parcv2_lhu import lhu_vmh_delay5

@requires_xcc
def test_stall_lhu_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_no_hazards.vcd",
                       lhu_no_hazards() )

@requires_xcc
def test_stall_lhu_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_hazard_W.vcd",
                       lhu_hazard_W() )

@requires_xcc
def test_stall_lhu_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_hazard_M.vcd",
                       lhu_hazard_M() )

@requires_xcc
def test_stall_lhu_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_hazard_X.vcd",
                       lhu_hazard_X() )

@requires_vmh
def test_stall_lhu_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_vmh_delay0.vcd",
                       lhu_vmh_delay0() )

@requires_vmh
def test_stall_lhu_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_lhu_vmh_delay5.vcd",
                       lhu_vmh_delay5() )

#---------------------------------------------------------------------------
# 36. parcv2-sb tests
#---------------------------------------------------------------------------

from parcv2_sb import sb_no_hazards
from parcv2_sb import sb_hazard_W
from parcv2_sb import sb_hazard_M
from parcv2_sb import sb_hazard_X
from parcv2_sb import sb_vmh_delay0
from parcv2_sb import sb_vmh_delay5

@requires_xcc
def test_stall_sb_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_no_hazards.vcd",
                       sb_no_hazards() )

@requires_xcc
def test_stall_sb_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_hazard_W.vcd",
                       sb_hazard_W() )

@requires_xcc
def test_stall_sb_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_hazard_M.vcd",
                       sb_hazard_M() )

@requires_xcc
def test_stall_sb_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_hazard_X.vcd",
                       sb_hazard_X() )

@requires_vmh
def test_stall_sb_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_vmh_delay0.vcd",
                       sb_vmh_delay0() )

@requires_vmh
def test_stall_sb_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sb_vmh_delay5.vcd",
                       sb_vmh_delay5() )

#---------------------------------------------------------------------------
# 37. parcv2-sh tests
#---------------------------------------------------------------------------

from parcv2_sh import sh_no_hazards
from parcv2_sh import sh_hazard_W
from parcv2_sh import sh_hazard_M
from parcv2_sh import sh_hazard_X
from parcv2_sh import sh_vmh_delay0
from parcv2_sh import sh_vmh_delay5

@requires_xcc
def test_stall_sh_no_hazards( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_no_hazards.vcd",
                       sh_no_hazards() )

@requires_xcc
def test_stall_sh_hazard_W( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_hazard_W.vcd",
                       sh_hazard_W() )

@requires_xcc
def test_stall_sh_hazard_M( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_hazard_M.vcd",
                       sh_hazard_M() )

@requires_xcc
def test_stall_sh_hazard_X( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_hazard_X.vcd",
                       sh_hazard_X() )

@requires_vmh
def test_stall_sh_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_vmh_delay0.vcd",
                       sh_vmh_delay0() )

@requires_vmh
def test_stall_sh_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_sh_vmh_delay5.vcd",
                       sh_vmh_delay5() )

#---------------------------------------------------------------------------
# 38. parcv2-j tests
#---------------------------------------------------------------------------

from parcv2_j import j_asm
from parcv2_j import j_vmh_delay0
from parcv2_j import j_vmh_delay5

@requires_xcc
def test_stall_j_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_j.vcd",
                       j_asm() )

@requires_vmh
def test_stall_j_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_j_vmh_delay0.vcd",
                       j_vmh_delay0() )

@requires_vmh
def test_stall_j_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_j_vmh_delay5.vcd",
                       j_vmh_delay5() )

#---------------------------------------------------------------------------
# 39. parcv2-jalr tests
#---------------------------------------------------------------------------

from parcv2_jalr import jalr_asm
from parcv2_jalr import jalr_vmh_delay0
from parcv2_jalr import jalr_vmh_delay5

@requires_xcc
def test_stall_jalr_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jalr.vcd",
                       jalr_asm() )

@requires_vmh
def test_stall_jalr_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jalr_vmh_delay0.vcd",
                       jalr_vmh_delay0() )

@requires_vmh
def test_stall_jalr_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_jalr_vmh_delay5.vcd",
                       jalr_vmh_delay5() )

#---------------------------------------------------------------------------
# 40. parcv2-beq tests
#---------------------------------------------------------------------------

from parcv2_beq import beq_asm
from parcv2_beq import beq_vmh_delay0
from parcv2_beq import beq_vmh_delay5

@requires_xcc
def test_stall_beq_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_beq.vcd",
                       beq_asm() )

@requires_vmh
def test_stall_beq_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_beq_vmh_delay0.vcd",
                       beq_vmh_delay0() )

@requires_vmh
def test_stall_beq_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_beq_vmh_delay5.vcd",
                       beq_vmh_delay5() )

#---------------------------------------------------------------------------
# 41. parcv2-blez tests
#---------------------------------------------------------------------------

from parcv2_blez import blez_asm
from parcv2_blez import blez_vmh_delay0
from parcv2_blez import blez_vmh_delay5

@requires_xcc
def test_stall_blez_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_blez.vcd",
                       blez_asm() )

@requires_vmh
def test_stall_blez_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_blez_vmh_delay0.vcd",
                       blez_vmh_delay0() )

@requires_vmh
def test_stall_blez_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_blez_vmh_delay5.vcd",
                       blez_vmh_delay5() )

#---------------------------------------------------------------------------
# 42. parcv2-bgtz tests
#---------------------------------------------------------------------------

from parcv2_bgtz import bgtz_asm
from parcv2_bgtz import bgtz_vmh_delay0
from parcv2_bgtz import bgtz_vmh_delay5

@requires_xcc
def test_stall_bgtz_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgtz.vcd",
                       bgtz_asm() )

@requires_vmh
def test_stall_bgtz_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgtz_vmh_delay0.vcd",
                       bgtz_vmh_delay0() )

@requires_vmh
def test_stall_bgtz_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgtz_vmh_delay5.vcd",
                       bgtz_vmh_delay5() )

#---------------------------------------------------------------------------
# 43. parcv2-bltz tests
#---------------------------------------------------------------------------

from parcv2_bltz import bltz_asm
from parcv2_bltz import bltz_vmh_delay0
from parcv2_bltz import bltz_vmh_delay5

@requires_xcc
def test_stall_bltz_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bltz.vcd",
                       bltz_asm() )

@requires_vmh
def test_stall_bltz_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bltz_vmh_delay0.vcd",
                       bltz_vmh_delay0() )

@requires_vmh
def test_stall_bltz_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bltz_vmh_delay5.vcd",
                       bltz_vmh_delay5() )

#---------------------------------------------------------------------------
# 44. parcv2-bgez tests
#---------------------------------------------------------------------------

from parcv2_bgez import bgez_asm
from parcv2_bgez import bgez_vmh_delay0
from parcv2_bgez import bgez_vmh_delay5

@requires_xcc
def test_stall_bgez_asm( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgez.vcd",
                       bgez_asm() )

@requires_vmh
def test_stall_bgez_vmh_delay0( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgez_vmh_delay0.vcd",
                       bgez_vmh_delay0() )

@requires_vmh
def test_stall_bgez_vmh_delay5( dump_vcd, test_verilog ):
  run_stall_proc_test( dump_vcd, test_verilog, "stall_bgez_vmh_delay5.vcd",
                       bgez_vmh_delay5() )

