//========================================================================
// parcv2-sb.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic tests
        //--------------------------------------------------------------------

        TEST_ST_OP( sb, 0x000000ab,  0, tdata_0, 0xdeadbeab )
        TEST_ST_OP( sb, 0x000000cd,  1, tdata_0, 0xdeadcdab )
        TEST_ST_OP( sb, 0x000000ef,  2, tdata_0, 0xdeefcdab )
        TEST_ST_OP( sb, 0x00000011,  3, tdata_0, 0x11efcdab )
        TEST_ST_OP( sb, 0x000000ab,  4, tdata_0, 0xdeadbeab )
        TEST_ST_OP( sb, 0x000000cd,  5, tdata_0, 0xdeadcdab )
        TEST_ST_OP( sb, 0x000000ef,  6, tdata_0, 0xdeefcdab )
        TEST_ST_OP( sb, 0x00000011,  7, tdata_0, 0x11efcdab )
        TEST_ST_OP( sb, 0x000000ab,  8, tdata_0, 0xdeadbeab )
        TEST_ST_OP( sb, 0x000000cd,  9, tdata_0, 0xdeadcdab )
        TEST_ST_OP( sb, 0x000000ef,  10, tdata_0, 0xdeefcdab )
        TEST_ST_OP( sb, 0x00000011,  11, tdata_0, 0x11efcdab )

        TEST_ST_OP( sb, 0x00000012,  -8, tdata_5, 0xdeadbe12 )
        TEST_ST_OP( sb, 0x00000034,  -7, tdata_5, 0xdead3412 )
        TEST_ST_OP( sb, 0x00000056,  -6, tdata_5, 0xde563412 )
        TEST_ST_OP( sb, 0x00000078,  -5, tdata_5, 0x78563412 )
        TEST_ST_OP( sb, 0x0000009a,  -4, tdata_5, 0xdeadbe9a )
        TEST_ST_OP( sb, 0x000000bc,  -3, tdata_5, 0xdeadbc9a )
        TEST_ST_OP( sb, 0x000000de,  -2, tdata_5, 0xdedebc9a )
        TEST_ST_OP( sb, 0x000000f0,  -1, tdata_5, 0xf0debc9a )
        TEST_ST_OP( sb, 0x00000012,   0, tdata_5, 0xdeadbe12 )
        TEST_ST_OP( sb, 0x00000034,   1, tdata_5, 0xdead3412 )
        TEST_ST_OP( sb, 0x00000056,   2, tdata_5, 0xde563412 )
        TEST_ST_OP( sb, 0x00000078,   3, tdata_5, 0x78563412 )

        // Test with a negative base

        la    $2, tdata_6
        li    $3, 0x000000ff
        addiu $5, $2, -32
        sb    $3, 33($5)
        lw    $4, 0($2)
        TEST_CHECK_EQ( $4, 0xdeadffef )

        // Test with unaligned base

        la    $2, tdata_7
        li    $3, 0x000000ff
        addiu $2, $2, -3
        sb    $3, 10($2)
        la    $5, tdata_8
        lw    $4, 0($5)
        TEST_CHECK_EQ( $4, 0xffadbeef )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_ST_SRC01_BYP( 0, 0, sb, 0x000000aa,  0,  tdata_9, 0xdeadbeaa )
        TEST_ST_SRC01_BYP( 0, 1, sb, 0x000000bb,  0,  tdata_9, 0xdeadbebb )
        TEST_ST_SRC01_BYP( 0, 2, sb, 0x000000cc,  1,  tdata_9, 0xdeadccbb )
        TEST_ST_SRC01_BYP( 0, 3, sb, 0x000000dd,  2,  tdata_9, 0xdeddccbb )
        TEST_ST_SRC01_BYP( 0, 4, sb, 0x000000ee,  3,  tdata_9, 0xeeddccbb )

        TEST_ST_SRC01_BYP( 1, 0, sb, 0x000000ff,  0, tdata_10, 0xdeadbeff )
        TEST_ST_SRC01_BYP( 1, 1, sb, 0x00000000,  1, tdata_10, 0xdead00ff )

        TEST_ST_SRC10_BYP( 0, 0, sb, 0x00000012,  0,  tdata_9, 0xeeddcc12 )
        TEST_ST_SRC10_BYP( 0, 1, sb, 0x00000034,  0,  tdata_9, 0xeeddcc34 )
        TEST_ST_SRC10_BYP( 0, 2, sb, 0x00000056,  1,  tdata_9, 0xeedd5634 )
        TEST_ST_SRC10_BYP( 0, 3, sb, 0x00000078,  2,  tdata_9, 0xee785634 )
        TEST_ST_SRC10_BYP( 0, 4, sb, 0x0000009a,  3,  tdata_9, 0x9a785634 )

        TEST_ST_SRC10_BYP( 1, 0, sb, 0x000000ff,  2, tdata_10, 0xdeff00ff )
        TEST_ST_SRC10_BYP( 1, 1, sb, 0x00000000,  3, tdata_10, 0x00ff00ff )

        TEST_PARC_END

        //--------------------------------------------------------------------
        // Test data
        //--------------------------------------------------------------------

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
