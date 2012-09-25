//========================================================================
// parcv2-lh.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic tests
        //--------------------------------------------------------------------

        TEST_LD_OP( lh, 0, tdata_0, 0xffffbeef )
        TEST_LD_OP( lh, 2, tdata_0, 0xffffdead )
        TEST_LD_OP( lh, 4, tdata_0, 0x000000ff )
        TEST_LD_OP( lh, 6, tdata_0, 0xffffff00 )

        TEST_LD_OP( lh, -8, tdata_2, 0xffffbeef )
        TEST_LD_OP( lh, -6, tdata_2, 0xffffdead )
        TEST_LD_OP( lh, -4, tdata_2, 0x000000ff )
        TEST_LD_OP( lh, -2, tdata_2, 0xffffff00 )
        TEST_LD_OP( lh,  0, tdata_2, 0xffffff00 )
        TEST_LD_OP( lh,  2, tdata_2, 0x000000ff )

        // Test with a negative base

        la    $2, tdata_0
        addiu $2, $2, -32
        lh    $4, 34($2)
        TEST_CHECK_EQ( $4, 0xffffdead )

        // Test with unaligned base

        la    $2, tdata_0
        addiu $2, $2, -3
        lh    $4, 5($2)
        TEST_CHECK_EQ( $4, 0xffffdead )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_LD_DEST_BYP( 0, lh, 0, tdata_0, 0xffffbeef )
        TEST_LD_DEST_BYP( 1, lh, 2, tdata_0, 0xffffdead )
        TEST_LD_DEST_BYP( 2, lh, 0, tdata_1, 0x000000ff )
        TEST_LD_DEST_BYP( 3, lh, 2, tdata_1, 0xffffff00 )
        TEST_LD_DEST_BYP( 4, lh, 0, tdata_2, 0xffffff00 )
     
        TEST_LD_SRC0_BYP( 0, lh, 0, tdata_0, 0xffffbeef )
        TEST_LD_SRC0_BYP( 1, lh, 2, tdata_0, 0xffffdead )
        TEST_LD_SRC0_BYP( 2, lh, 0, tdata_1, 0x000000ff )
        TEST_LD_SRC0_BYP( 3, lh, 2, tdata_1, 0xffffff00 )
        TEST_LD_SRC0_BYP( 4, lh, 0, tdata_2, 0xffffff00 )

        // WAW

        la $4, tdata_0
        lh $3, 2($4)
        li $3, 2
        TEST_CHECK_EQ( $3, 2 )

        // RAW

        la    $5, tdata_0
        lh    $6, 2($5)
        addiu $7, $6, 1
        TEST_CHECK_EQ( $7, 0xffffdeae )

        TEST_PARC_END

        //--------------------------------------------------------------------
        // Test data
        //--------------------------------------------------------------------

        .data
        .align 4

tdata_0: .word 0xdeadbeef
tdata_1: .word 0xff0000ff
tdata_2: .word 0x00ffff00
