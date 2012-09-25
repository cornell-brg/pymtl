//========================================================================
// parc-macros.h
//========================================================================

#ifndef PARC_MACROS_H
#define PARC_MACROS_H

//------------------------------------------------------------------------
// TEST_PARC_BEGIN
//------------------------------------------------------------------------
// Create a memory location for the tohost value and an entry point
// where the test should start.

#define TEST_PARC_BEGIN                                                 \
    .text;                                                              \
    .align  4;                                                          \
    .global _test;                                                      \
    .ent    _test;                                                      \
_test:                                                                  \

//------------------------------------------------------------------------
// TEST_PARC_END
//------------------------------------------------------------------------
// Assumes that the result is in register number 29. Also assume that
// the linker script places the _tohost array in the first 2^16 bytes of
// memory so that we can access it with just the %lo() assembler
// builtin. This avoids needing lui to also be implemented. We add a
// bunch of nops after the pass fail sections with the hope that someone
// can implement just addiu and sw and then get that working first. The
// bne won't do anything, and the test harness will hopefully detect the
// update to _tohost soon after changing it.

#define TEST_PARC_END                                                   \
_pass:                                                                  \
    addiu  $29, $0, 1;                                                  \
                                                                        \
_fail:                                                                  \
    li     $2,  1;                                                      \
    mtc0   $29, $21;                                                    \
1:  bne    $0, $2, 1b;                                                  \
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;                   \
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;                   \
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;                   \
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;                   \
                                                                        \
    .end _test                                                          \

//------------------------------------------------------------------------
// TEST_XCPTR_BEGIN
//------------------------------------------------------------------------
// Create special memory location for exception handler code.

#define TEST_XCPT_BEGIN                                                 \
    .section .xcpthandler, "ax";                                        \
    .align 4;                                                           \
    .ent _xcpthandler;                                                  \
    .global _xcpthandler;                                               \
_xcpthandler:                                                           \

//------------------------------------------------------------------------
// TEST_XCPT_END
//------------------------------------------------------------------------

#define TEST_XCPT_END                                                   \
    .end _xcpthandler;                                                  \

//------------------------------------------------------------------------
// TEST_CHECK_EQ
//------------------------------------------------------------------------
// Check if the given register has the given value, and fail if not.
// Saves the line number in register $29 for use by the TEST_END macro.

#define TEST_CHECK_EQ( reg_, value_ )                                   \
    li    $29, __LINE__;                                                \
    bne   reg_, value_, _fail;                                          \

//------------------------------------------------------------------------
// TEST_CHECK_FAIL
//------------------------------------------------------------------------
// Force this test to fail. Saves the line number in register $29 for
// use by the TEST_END macro.

#define TEST_CHECK_FAIL                                                 \
    li    $29, __LINE__;                                                \
    bne   $29, $0, _fail;                                               \

//------------------------------------------------------------------------
// TEST_INESRT_NOPS
//------------------------------------------------------------------------
// Macro which expands to a variable number of nops.

#define TEST_INSERT_NOPS_0
#define TEST_INSERT_NOPS_1  nop; TEST_INSERT_NOPS_0
#define TEST_INSERT_NOPS_2  nop; TEST_INSERT_NOPS_1
#define TEST_INSERT_NOPS_3  nop; TEST_INSERT_NOPS_2
#define TEST_INSERT_NOPS_4  nop; TEST_INSERT_NOPS_3
#define TEST_INSERT_NOPS_5  nop; TEST_INSERT_NOPS_4
#define TEST_INSERT_NOPS_6  nop; TEST_INSERT_NOPS_5
#define TEST_INSERT_NOPS_7  nop; TEST_INSERT_NOPS_6
#define TEST_INSERT_NOPS_8  nop; TEST_INSERT_NOPS_7
#define TEST_INSERT_NOPS_9  nop; TEST_INSERT_NOPS_8
#define TEST_INSERT_NOPS_10 nop; TEST_INSERT_NOPS_9

#define TEST_INSERT_NOPS_H0( nops_ ) \
  TEST_INSERT_NOPS_ ## nops_

#define TEST_INSERT_NOPS( nops_ ) \
  TEST_INSERT_NOPS_H0( nops_ )

//------------------------------------------------------------------------
// TEST_IMM : Helper macros for register-immediate instructions
//------------------------------------------------------------------------

#define TEST_IMM_OP( inst_, src0_, imm_, result_ )                      \
    li    $2, src0_;                                                    \
    inst_ $4, $2, imm_;                                                 \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_IMM_SRC0_EQ_DEST( inst_, src0_, imm_, result_ )            \
    li    $2, src0_;                                                    \
    inst_ $2, $2, imm_;                                                 \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_IMM_DEST_BYP( nops_, inst_, src0_, imm_, result_ )         \
    li    $2, src0_;                                                    \
    inst_ $4, $2, imm_;                                                 \
    TEST_INSERT_NOPS( nops_ );                                          \
    addiu $7, $4, 0;                                                    \
    TEST_CHECK_EQ( $7, result_ );                                       \

#define TEST_IMM_SRC0_BYP( nops_, inst_, src0_, imm_, result_ )         \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( nops_ );                                          \
    inst_ $4, $2, imm_;                                                 \
    TEST_CHECK_EQ( $4, result_ );                                       \

//------------------------------------------------------------------------
// TEST_LUI : Helper macros for load upper immediate instruction
//------------------------------------------------------------------------

#define TEST_LUI_OP( inst_, imm_, result_ )                             \
    li    $2, 0;                                                        \
    inst_ $2, imm_;                                                     \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_LUI_DEST_BYP( nops_, inst_, imm_, result_ )                \
    li    $2, 0;                                                        \
    inst_ $2, imm_;                                                     \
    TEST_INSERT_NOPS( nops_ );                                          \
    addiu $3, $2, 0;                                                    \
    TEST_CHECK_EQ( $3, result_ );                                       \

//------------------------------------------------------------------------
// TEST_RR : Helper macros for register-register instructions
//------------------------------------------------------------------------

#define TEST_RR_OP( inst_, src0_, src1_, result_ )                      \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $4, $2, $3;                                                   \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_RR_OP1( inst_, src0_, result_ )                            \
    li    $2, src0_;                                                    \
    inst_ $4, $2;                                                       \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_RR_SRC0_EQ_DEST( inst_, src0_, src1_, result_ )            \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $2, $2, $3;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_RR_SRC1_EQ_DEST( inst_, src0_, src1_, result_ )            \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $3, $2, $3;                                                   \
    TEST_CHECK_EQ( $3, result_ );                                       \

#define TEST_RR_SRC0_EQ_SRC1( inst_, src0_, result_ )                   \
    li    $2, src0_;                                                    \
    inst_ $3, $2, $2;                                                   \
    TEST_CHECK_EQ( $3, result_ );                                       \

#define TEST_RR_SRCS_EQ_DEST( inst_, src0_, result_ )                   \
    li    $2, src0_;                                                    \
    inst_ $2, $2, $2;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_RR_DEST_BYP( nops_, inst_, src0_, src1_, result_ )         \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $4, $2, $3;                                                   \
    TEST_INSERT_NOPS( nops_ );                                          \
    addiu $7, $4, 0;                                                    \
    TEST_CHECK_EQ( $7, result_ );                                       \

#define TEST_RR_SRC01_BYP( src0_nops_, src1_nops_, inst_,               \
                           src0_, src1_, result_ )                      \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    li    $3, src1_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    inst_ $4, $2, $3;                                                   \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_RR_SRC10_BYP( src1_nops_, src0_nops_, inst_,               \
                           src0_, src1_, result_ )                      \
    li    $3, src1_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    inst_ $4, $2, $3;                                                   \
    TEST_CHECK_EQ( $4, result_ );                                       \

//------------------------------------------------------------------------
// TEST_BR1 : Helper macros for branch single-source instructions
//------------------------------------------------------------------------

#define TEST_BR1_OP_TAKEN( inst_, src0_ )                               \
    li    $2, src0_;                                                    \
    inst_ $2, 2f;                                                       \
    TEST_CHECK_FAIL;                                                    \
1:  li    $3, 1;                                                        \
    bne   $0, $3, 3f;                                                   \
2:  inst_ $2, 1b;                                                       \
    TEST_CHECK_FAIL;                                                    \
3:                                                                      \

#define TEST_BR1_OP_NOTTAKEN( inst_, src0_ )                            \
    li    $2, src0_;                                                    \
    inst_ $2, 1f;                                                       \
    li    $3, 1;                                                        \
    bne   $0, $3, 2f;                                                   \
1:  TEST_CHECK_FAIL;                                                    \
2:  inst_ $2, 1b;                                                       \

#define TEST_BR1_SRC0_BYP( nops_, inst_, src0_ )                        \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( nops_ );                                          \
    inst_ $2, 1f;                                                       \
    li    $3, 1;                                                        \
    bne   $0, $3, 2f;                                                   \
1:  TEST_CHECK_FAIL;                                                    \
2:                                                                      \

//------------------------------------------------------------------------
// TEST_BR1 : Helper macros for branch two-source instructions
//------------------------------------------------------------------------

#define TEST_BR2_OP_TAKEN( inst_, src0_, src1_ )                        \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $2, $3, 2f;                                                   \
    TEST_CHECK_FAIL;                                                    \
1:  li    $4, 1;                                                        \
    bne   $0, $4, 3f;                                                   \
2:  inst_ $2, $3, 1b;                                                   \
    TEST_CHECK_FAIL;                                                    \
3:                                                                      \

#define TEST_BR2_OP_NOTTAKEN( inst_, src0_, src1_ )                     \
    li    $2, src0_;                                                    \
    li    $3, src1_;                                                    \
    inst_ $2, $3, 1f;                                                   \
    li    $4, 1;                                                        \
    bne   $0, $4, 2f;                                                   \
1:  TEST_CHECK_FAIL;                                                    \
2:  inst_ $2, $3, 1b;                                                   \

#define TEST_BR2_SRC01_BYP( src0_nops_, src1_nops_,                     \
                            inst_, src0_, src1_ )                       \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    li    $3, src1_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    inst_ $2, $3, 1f;                                                   \
    li    $4, 1;                                                        \
    bne   $0, $4, 2f;                                                   \
1:  TEST_CHECK_FAIL;                                                    \
2:                                                                      \

#define TEST_BR2_SRC10_BYP( src1_nops_, src0_nops_,                     \
                            inst_, src0_, src1_ )                       \
    li    $3, src1_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    li    $2, src0_;                                                    \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    inst_ $2, $3, 1f;                                                   \
    li    $4, 1;                                                        \
    bne   $0, $4, 2f;                                                   \
1:  TEST_CHECK_FAIL;                                                    \
2:                                                                      \

//------------------------------------------------------------------------
// TEST_JR : Helper macros for jump register instructions
//------------------------------------------------------------------------

#define TEST_JR_SRC0_BYP( nops_, inst_ )                                \
    la    $2, 1f;                                                       \
    TEST_INSERT_NOPS( nops_ );                                          \
    inst_ $2;                                                           \
    TEST_CHECK_FAIL;                                                    \
1:                                                                      \

//------------------------------------------------------------------------
// TEST_JALR : Helper macros for jump and link register instruction
//------------------------------------------------------------------------

#define TEST_JALR_SRC0_BYP( nops_, inst_ )                              \
    la $2, 1f;                                                          \
    TEST_INSERT_NOPS( nops_ );                                          \
    inst_ $3, $2;                                                       \
    TEST_CHECK_FAIL;                                                    \
1:                                                                      \

//------------------------------------------------------------------------
// TEST_LD : Helper macros for load instructions
//------------------------------------------------------------------------

#define TEST_LD_OP( inst_, offset_, base_, result_ )                    \
    la    $2, base_;                                                    \
    inst_ $4, offset_($2);                                              \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_LD_DEST_BYP( nops_, inst_, offset_, base_, result_ )       \
    la    $2, base_;                                                    \
    inst_ $4, offset_($2);                                              \
    TEST_INSERT_NOPS( nops_ );                                          \
    addiu $7, $4, 0;                                                    \
    TEST_CHECK_EQ( $7, result_ );                                       \

#define TEST_LD_SRC0_BYP( nops_, inst_, offset_, base_, result_ )       \
    la    $2, base_;                                                    \
    TEST_INSERT_NOPS( nops_ );                                          \
    inst_ $4, offset_($2);                                              \
    TEST_CHECK_EQ( $4, result_ );                                       \

//------------------------------------------------------------------------
// TEST_SW : Helper macros for store word instructions
//------------------------------------------------------------------------
// Macros used specifically for the sw instruction in PARCv1, which
// avoids using any instructions from PARCv2.

#define TEST_SW_OP( st_, wdata_, offset_, base_, result_ )              \
    la    $2, base_;                                                    \
    li    $3, wdata_;                                                   \
    st_   $3, offset_($2);                                              \
    lw    $4, offset_($2);                                              \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_SW_SRC01_BYP( src0_nops_, src1_nops_,                      \
                           st_, wdata_, offset_, base_, result_ )       \
    li    $3, wdata_;                                                   \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    la    $2, base_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    st_   $3, offset_($2);                                              \
    lw    $4, offset_($2);                                              \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_SW_SRC10_BYP( src1_nops_, src0_nops_,                      \
                           st_, wdata_, offset_, base_, result_ )       \
    la    $2, base_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    li    $3, wdata_;                                                   \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    st_   $3, offset_($2);                                              \
    lw    $4, offset_($2);                                              \
    TEST_CHECK_EQ( $4, result_ );                                       \

//------------------------------------------------------------------------
// TEST_ST : Helper macros for subword store instructions
//------------------------------------------------------------------------
// These macros always use a lw to bring back in the stored data to
// verify the store. The lw address is formed by simply masking off the
// lower two bits of the store address. The result_ needs to be
// specified accordingly. This helps make sure that the store doesn't
// store more data then it is supposed to.

#define TEST_ST_OP( st_, wdata_, offset_, base_, result_ )              \
    la    $2, base_;                                                    \
    li    $3, wdata_;                                                   \
    st_   $3, offset_($2);                                              \
    li    $5, 0xfffffffc;                                               \
    addiu $2, $2, offset_;                                              \
    and   $2, $2, $5;                                                   \
    lw    $4, ($2);                                                     \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_ST_SRC01_BYP( src0_nops_, src1_nops_,                      \
                           st_, wdata_, offset_, base_, result_ )       \
    li    $3, wdata_;                                                   \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    la    $2, base_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    st_   $3, offset_($2);                                              \
    li    $5, 0xfffffffc;                                               \
    addiu $2, $2, offset_;                                              \
    and   $2, $2, $5;                                                   \
    lw    $4, ($2);                                                     \
    TEST_CHECK_EQ( $4, result_ );                                       \

#define TEST_ST_SRC10_BYP( src1_nops_, src0_nops_,                      \
                           st_, wdata_, offset_, base_, result_ )       \
    la    $2, base_;                                                    \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    li    $3, wdata_;                                                   \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    st_   $3, offset_($2);                                              \
    li    $5, 0xfffffffc;                                               \
    addiu $2, $2, offset_;                                              \
    and   $2, $2, $5;                                                   \
    lw    $4, ($2);                                                     \
    TEST_CHECK_EQ( $4, result_ );                                       \

//------------------------------------------------------------------------
// TEST_CMOV : Helper macros for conditional move instructions
//------------------------------------------------------------------------

#define TEST_CMOV_OP( inst_, dest_, src_, sel_, result_ )               \
    li    $2, dest_;                                                    \
    li    $3, src_;                                                     \
    li    $4, sel_;                                                     \
    inst_ $2, $3, $4;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_CMOV_SRC0_EQ_DEST( inst_, dest_src_, sel_, result_ )       \
    li    $2, dest_src_;                                                \
    li    $3, sel_;                                                     \
    inst_ $2, $2, $3;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_CMOV_SRC1_EQ_DEST( inst_, src_, dest_sel_, result_ )       \
    li    $2, src_;                                                     \
    li    $3, dest_sel_;                                                \
    inst_ $3, $2, $3;                                                   \
    TEST_CHECK_EQ( $3, result_ );                                       \

#define TEST_CMOV_SRCS_EQ_DEST( inst_, dest_src_sel_, result_ )         \
    li    $2, dest_src_sel_;                                            \
    inst_ $2, $2, $2;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_CMOV_DEST_BYP( nops_, inst_, dest_, src_, sel_, result_ )  \
    li    $2, dest_;                                                    \
    li    $3, src_;                                                     \
    li    $4, sel_;                                                     \
    inst_ $2, $3, $4;                                                   \
    TEST_INSERT_NOPS( nops_ );                                          \
    addiu $7, $2, 0;                                                    \
    TEST_CHECK_EQ( $7, result_ );                                       \

#define TEST_CMOV_SRC01_BYP( src0_nops_, src1_nops_, inst_,             \
                             dest_, src_, sel_, result_ )               \
    li    $2, dest_;                                                    \
    li    $3, src_;                                                     \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    li    $4, sel_;                                                     \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    inst_ $2, $3, $4;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#define TEST_CMOV_SRC10_BYP( src1_nops_, src0_nops_, inst_,             \
                             dest_, src_, sel_, result_ )               \
    li    $2, dest_;                                                    \
    li    $4, sel_;                                                     \
    TEST_INSERT_NOPS( src1_nops_ );                                     \
    li    $3, src_;                                                     \
    TEST_INSERT_NOPS( src0_nops_ );                                     \
    inst_ $2, $3, $4;                                                   \
    TEST_CHECK_EQ( $2, result_ );                                       \

#endif /* PARC_MACROS_H */

