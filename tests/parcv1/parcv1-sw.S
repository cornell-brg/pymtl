//=========================================================================
// parcv1-sw.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //----------------------------------------------------------------
        // Basic tests
        //----------------------------------------------------------------

        TEST_SW_OP( sw, 0x000000ff,   0, tdata_0, 0x000000ff )
        TEST_SW_OP( sw, 0x00007f00,   4, tdata_0, 0x00007f00 )
        TEST_SW_OP( sw, 0x00000ff0,   8, tdata_0, 0x00000ff0 )
        TEST_SW_OP( sw, 0x0000700f,  12, tdata_0, 0x0000700f )
        TEST_SW_OP( sw, 0xdeadbeef, -12, tdata_3, 0xdeadbeef )
        TEST_SW_OP( sw, 0xdeadbeef,  -8, tdata_3, 0xdeadbeef )
        TEST_SW_OP( sw, 0xdeadbeef,  -4, tdata_3, 0xdeadbeef )
        TEST_SW_OP( sw, 0xdeadbeef,   0, tdata_3, 0xdeadbeef )

        // Test with a negative base

        la    $2, tdata_5
        li    $3, 0xbeefdead
        addiu $5, $2, -32
        sw    $3, 32($5)
        lw    $4, 0($2)
        TEST_CHECK_EQ( $4, 0xbeefdead )

        // Test with unaligned base

        la    $2, tdata_6
        li    $3, 0xabcdef01
        addiu $5, $2, -3
        sw    $3, 7($5)
        la    $5, tdata_7
        lw    $4, 0($5)
        TEST_CHECK_EQ( $4, 0xabcdef01 )

        //----------------------------------------------------------------
        // Bypassing tests
        //----------------------------------------------------------------

        TEST_SW_SRC01_BYP( 0, 0, sw, 0xaabbccdd,  0,  tdata_8, 0xaabbccdd )
        TEST_SW_SRC01_BYP( 0, 1, sw, 0xeeff0011,  4,  tdata_8, 0xeeff0011 )
        TEST_SW_SRC01_BYP( 0, 2, sw, 0xbeefdead,  0,  tdata_9, 0xbeefdead )
        TEST_SW_SRC01_BYP( 0, 3, sw, 0xaabbeeff,  4,  tdata_9, 0xaabbeeff )
        TEST_SW_SRC01_BYP( 0, 4, sw, 0xccdd1234,  0, tdata_10, 0xccdd1234 )
        TEST_SW_SRC01_BYP( 0, 3, sw, 0xeeffccdd,  4, tdata_10, 0xeeffccdd )

        TEST_SW_SRC01_BYP( 1, 0, sw, 0xffffffff,  0, tdata_11, 0xffffffff )
        TEST_SW_SRC01_BYP( 1, 1, sw, 0x00000000,  0, tdata_11, 0x00000000 )

        TEST_SW_SRC10_BYP( 0, 0, sw, 0xdeadbeef,  0,  tdata_8, 0xdeadbeef )
        TEST_SW_SRC10_BYP( 0, 1, sw, 0xdeadbeef,  4,  tdata_8, 0xdeadbeef )
        TEST_SW_SRC10_BYP( 0, 2, sw, 0xbeefdead,  0,  tdata_9, 0xbeefdead )
        TEST_SW_SRC10_BYP( 0, 3, sw, 0xdeadbeef,  4,  tdata_9, 0xdeadbeef )
        TEST_SW_SRC10_BYP( 0, 4, sw, 0xbeefdead,  0, tdata_10, 0xbeefdead )
        TEST_SW_SRC10_BYP( 0, 3, sw, 0xdeadbeef,  4, tdata_10, 0xdeadbeef )

        TEST_SW_SRC10_BYP( 1, 0, sw, 0xbeefdead,  0, tdata_11, 0xbeefdead )
        TEST_SW_SRC10_BYP( 1, 1, sw, 0xdeadbeef,  4, tdata_11, 0xdeadbeef )

        TEST_PARC_END

        //-----------------------------------------------------------------
        // Test data
        //-----------------------------------------------------------------

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

