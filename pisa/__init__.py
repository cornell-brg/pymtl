#=========================================================================
# Modular Python Build System __init__ file
#=========================================================================

# List of collection modules

import elf
import pisa_inst_test_utils

# List of single-class modules

from IsaImpl            import IsaImpl
from PisaInst           import PisaInst
from PisaSemantics      import PisaSemantics
from PisaSim            import PisaSim
from SparseMemoryImage  import SparseMemoryImage

# Test Cases: Basic instructions

# import pisa_inst_mfc0_test
# import pisa_inst_mtc0_test
# import pisa_inst_nop_test

# Test Cases: Reg-reg arithmetic, logical, and comparison instructions

# import pisa_inst_addu_test
# import pisa_inst_subu_test
# import pisa_inst_and_test
# import pisa_inst_or_test
# import pisa_inst_xor_test
# import pisa_inst_nor_test
# import pisa_inst_slt_test
# import pisa_inst_sltu_test

# Test Cases: Reg-imm arithmetic, logical, and comparison instructions

# import pisa_inst_addiu_test
# import pisa_inst_andi_test
# import pisa_inst_ori_test
# import pisa_inst_xori_test
# import pisa_inst_slti_test
# import pisa_inst_sltiu_test

# Test Cases: Shift instructions

# import pisa_inst_sll_test
# import pisa_inst_srl_test
# import pisa_inst_sra_test
# import pisa_inst_sllv_test
# import pisa_inst_srlv_test
# import pisa_inst_srav_test

# Test Cases: Other instructions

# import pisa_inst_lui_test

# Test Cases: Multiply/divide instructions

# import pisa_inst_mul_test
# import pisa_inst_div_test
# import pisa_inst_divu_test
# import pisa_inst_rem_test
# import pisa_inst_remu_test

# Test Cases: Load instructions

# import pisa_inst_lw_test
# import pisa_inst_lh_test
# import pisa_inst_lhu_test
# import pisa_inst_lb_test
# import pisa_inst_lbu_test

# Test Cases: Store instructions

# import pisa_inst_sw_test
# import pisa_inst_sh_test
# import pisa_inst_sb_test

# Test Cases: Unconditional jump instructions

# import pisa_inst_j_test
# import pisa_inst_jal_test
# import pisa_inst_jr_test
# import pisa_inst_jalr_test

# Test Cases: Conditional branch instructions

# import pisa_inst_beq_test
# import pisa_inst_bne_test
# import pisa_inst_blez_test
# import pisa_inst_bgtz_test
# import pisa_inst_bltz_test
# import pisa_inst_bgez_test
