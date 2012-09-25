//=========================================================================
// parcv1-lw.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //----------------------------------------------------------------
        // Basic tests
        //----------------------------------------------------------------

        TEST_LD_OP( lw,   0, tdata_0, 0x000000ff )
        TEST_LD_OP( lw,   4, tdata_0, 0x00007f00 )
        TEST_LD_OP( lw,   8, tdata_0, 0x00000ff0 )
        TEST_LD_OP( lw,  12, tdata_0, 0x0000700f )
        TEST_LD_OP( lw, -12, tdata_3, 0x000000ff )
        TEST_LD_OP( lw,  -8, tdata_3, 0x00007f00 )
        TEST_LD_OP( lw,  -4, tdata_3, 0x00000ff0 )
        TEST_LD_OP( lw,   0, tdata_3, 0x0000700f )

        // Test with a negative base

        la    $2, tdata_0
        addiu $2, $2, -32
        lw    $4, 32($2)
        TEST_CHECK_EQ( $4, 0x000000ff )

        // Test with unaligned base

        la    $2, tdata_0
        addiu $2, $2, -3
        lw    $4, 7($2)
        TEST_CHECK_EQ( $4, 0x00007f00 )

        //----------------------------------------------------------------
        // Bypassing tests
        //----------------------------------------------------------------

        TEST_LD_DEST_BYP( 0, lw, 0, tdata_0, 0x000000ff )
        TEST_LD_DEST_BYP( 1, lw, 4, tdata_0, 0x00007f00 )
        TEST_LD_DEST_BYP( 2, lw, 0, tdata_1, 0x00007f00 )
        TEST_LD_DEST_BYP( 3, lw, 4, tdata_1, 0x00000ff0 )
        TEST_LD_DEST_BYP( 4, lw, 0, tdata_3, 0x0000700f )

        TEST_LD_SRC0_BYP( 0, lw, 0, tdata_0, 0x000000ff )
        TEST_LD_SRC0_BYP( 1, lw, 4, tdata_0, 0x00007f00 )
        TEST_LD_SRC0_BYP( 2, lw, 0, tdata_1, 0x00007f00 )
        TEST_LD_SRC0_BYP( 3, lw, 4, tdata_1, 0x00000ff0 )
        TEST_LD_SRC0_BYP( 4, lw, 0, tdata_3, 0x0000700f )

        // WAW

        la $4, tdata_0
        lw $3, 4($4)
        li $3, 2
        TEST_CHECK_EQ( $3, 2 )

        // RAW

        la $5, tdata_0
        lw $6, 4($5)
        addiu $7, $6, 1
        TEST_CHECK_EQ( $7, 0x00007f01 )

        TEST_PARC_END

        //-----------------------------------------------------------------
        // Test data
        //-----------------------------------------------------------------

        .data
        .align 4

tdata_0:  .word 0x000000ff
tdata_1:  .word 0x00007f00
tdata_2:  .word 0x00000ff0
tdata_3:  .word 0x0000700f

