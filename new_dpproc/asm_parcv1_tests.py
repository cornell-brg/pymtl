#=========================================================================
# ParcV1 Assembly Tests
#=========================================================================

from asm_macros import *

#-------------------------------------------------------------------------
# ori
#-------------------------------------------------------------------------

ori_str = [ genasm_test_imm_op( "ori", 0xff00ff00, 0x0f0f, 0xff00ff0f ),
            genasm_test_imm_op( "ori", 0x0ff00ff0, 0xf0f0, 0x0ff0fff0 ),
            genasm_test_imm_op( "ori", 0x00ff00ff, 0x0f0f, 0x00ff0fff ),
            genasm_test_imm_op( "ori", 0xf00ff00f, 0xf0f0, 0xf00ff0ff ),
          ]

#-------------------------------------------------------------------------
# addiu
#-------------------------------------------------------------------------

addiu_str = [ genasm_test_imm_op( "addiu", 0x00000000, 0x0000, 0x00000000 ),
              genasm_test_imm_op( "addiu", 0x00000001, 0x0001, 0x00000002 ),
              genasm_test_imm_op( "addiu", 0x00000003, 0x0007, 0x0000000a ),
              genasm_test_imm_op( "addiu", 0x00000000, 0x8000, 0xffff8000 ),
              genasm_test_imm_op( "addiu", 0x80000000, 0x0000, 0x80000000 ),
              genasm_test_imm_op( "addiu", 0x80000000, 0x8000, 0x7fff8000 ),
              genasm_test_imm_op( "addiu", 0x00000000, 0x7fff, 0x00007fff ),
              genasm_test_imm_op( "addiu", 0x7fffffff, 0x0000, 0x7fffffff ),
              genasm_test_imm_op( "addiu", 0x7fffffff, 0x7fff, 0x80007ffe ),
              genasm_test_imm_op( "addiu", 0x80000000, 0x7fff, 0x80007fff ),
              genasm_test_imm_op( "addiu", 0x7fffffff, 0x8000, 0x7fff7fff ),
              genasm_test_imm_op( "addiu", 0x00000000, 0xffff, 0xffffffff ),
              genasm_test_imm_op( "addiu", 0xffffffff, 0x0001, 0x00000000 ),
              genasm_test_imm_op( "addiu", 0xffffffff, 0xffff, 0xfffffffe ),
            ]

#-------------------------------------------------------------------------
# lui
#-------------------------------------------------------------------------

lui_str = [ genasm_test_lui_op( "lui", 0x0000, 0x00000000 ),
            genasm_test_lui_op( "lui", 0xffff, 0xffff0000 ),
            genasm_test_lui_op( "lui", 0x7fff, 0x7fff0000 ),
            genasm_test_lui_op( "lui", 0x8000, 0x80000000 ),
          ]

#-------------------------------------------------------------------------
# addu
#-------------------------------------------------------------------------

addu_str = [ genasm_test_rr_op( "addu", 0x00000000, 0x00000000, 0x00000000 ),
             genasm_test_rr_op( "addu", 0x00000001, 0x00000001, 0x00000002 ),
             genasm_test_rr_op( "addu", 0x00000003, 0x00000007, 0x0000000a ),
             genasm_test_rr_op( "addu", 0x00000000, 0xffff8000, 0xffff8000 ),
             genasm_test_rr_op( "addu", 0x80000000, 0x00000000, 0x80000000 ),
             genasm_test_rr_op( "addu", 0x80000000, 0xffff8000, 0x7fff8000 ),
             genasm_test_rr_op( "addu", 0x00000000, 0x00007fff, 0x00007fff ),
             genasm_test_rr_op( "addu", 0x7fffffff, 0x00000000, 0x7fffffff ),
             genasm_test_rr_op( "addu", 0x7fffffff, 0x00007fff, 0x80007ffe ),
             genasm_test_rr_op( "addu", 0x80000000, 0x00007fff, 0x80007fff ),
             genasm_test_rr_op( "addu", 0x7fffffff, 0xffff8000, 0x7fff7fff ),
             genasm_test_rr_op( "addu", 0x00000000, 0xffffffff, 0xffffffff ),
             genasm_test_rr_op( "addu", 0xffffffff, 0x00000001, 0x00000000 ),
             genasm_test_rr_op( "addu", 0xffffffff, 0xffffffff, 0xfffffffe ),
           ]

#-------------------------------------------------------------------------
# lw
#-------------------------------------------------------------------------

lw_str = [ genasm_test_ld_op( "lw",   0, 'tdata_0', 0x000000ff ),
           genasm_test_ld_op( "lw",   4, 'tdata_0', 0x00007f00 ),
           genasm_test_ld_op( "lw",   8, 'tdata_0', 0x00000ff0 ),
           genasm_test_ld_op( "lw",  12, 'tdata_0', 0x0000700f ),
           genasm_test_ld_op( "lw", -12, 'tdata_3', 0x000000ff ),
           genasm_test_ld_op( "lw",  -8, 'tdata_3', 0x00007f00 ),
           genasm_test_ld_op( "lw",  -4, 'tdata_3', 0x00000ff0 ),
           genasm_test_ld_op( "lw",   0, 'tdata_3', 0x0000700f ),
         ]

lw_data_sec = """
           .data
           .align 4

           tdata_0:  .word 0x000000ff
           tdata_1:  .word 0x00007f00
           tdata_2:  .word 0x00000ff0
           tdata_3:  .word 0x0000700f
           """

#-------------------------------------------------------------------------
# sw
#-------------------------------------------------------------------------

sw_str = [ genasm_test_sw_op( "sw", 0x000000ff,   0, 'tdata_0', 0x000000ff ),
           genasm_test_sw_op( "sw", 0x00007f00,   4, 'tdata_0', 0x00007f00 ),
           genasm_test_sw_op( "sw", 0x00000ff0,   8, 'tdata_0', 0x00000ff0 ),
           genasm_test_sw_op( "sw", 0x0000700f,  12, 'tdata_0', 0x0000700f ),
           genasm_test_sw_op( "sw", 0xdeadbeef, -12, 'tdata_3', 0xdeadbeef ),
           genasm_test_sw_op( "sw", 0xdeadbeef,  -8, 'tdata_3', 0xdeadbeef ),
           genasm_test_sw_op( "sw", 0xdeadbeef,  -4, 'tdata_3', 0xdeadbeef ),
           genasm_test_sw_op( "sw", 0xdeadbeef,   0, 'tdata_3', 0xdeadbeef ),
         ]

sw_data_sec = """
           .data
           .align 4

           tdata_0:  .word 0xdeadbeef
           tdata_1:  .word 0xdeadbeef
           tdata_2:  .word 0xdeadbeef
           tdata_3:  .word 0xdeadbeef
           tdata_4:  .word 0xdeadbeef
           tdata_5:  .word 0xdeadbeef
           tdata_6:  .word 0xdeadbeef
           tdata_7:  .word 0xdeadbeef
           tdata_8:  .word 0xdeadbeef
           tdata_9:  .word 0xdeadbeef
           tdata_10: .word 0xdeadbeef
           tdata_11: .word 0xdeadbeef
           """
#-------------------------------------------------------------------------
# bne
#-------------------------------------------------------------------------

bne_str = [ genasm_test_br2_op( "bne",  0,  1, taken=True  ),
            genasm_test_br2_op( "bne",  1,  0, taken=True  ),
            genasm_test_br2_op( "bne", -1,  1, taken=True  ),
            genasm_test_br2_op( "bne",  1, -1, taken=True  ),
            genasm_test_br2_op( "bne",  0,  0, taken=False ),
            genasm_test_br2_op( "bne",  1,  1, taken=False ),
            genasm_test_br2_op( "bne", -1, -1, taken=False ),
          ]

#-------------------------------------------------------------------------
# jal
#-------------------------------------------------------------------------

jal_str = """
test:
        li $29, 1111;
        li $31, 0

linkaddr:
        jal target
        nop
        nop

        j _fail

target:
        la $2, linkaddr
        addiu $2, $2, 4
        bne $2, $31, _fail
"""

#-------------------------------------------------------------------------
# jr
#-------------------------------------------------------------------------

jr_str = """
test:
        li $29, 1111
        li $31, 0
        la $3, target

linkaddr:
        jr $3
        nop
        nop

        j _fail

target:
"""

