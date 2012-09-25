//========================================================================
// parcv2-lhu.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic tests
        //--------------------------------------------------------------------

        TEST_LD_OP( lhu, 0, tdata_0, 0x0000beef )
        TEST_LD_OP( lhu, 2, tdata_0, 0x0000dead )
        TEST_LD_OP( lhu, 4, tdata_0, 0x000000ff )
        TEST_LD_OP( lhu, 6, tdata_0, 0x0000ff00 )

        TEST_LD_OP( lhu, -8, tdata_2, 0x0000beef )
        TEST_LD_OP( lhu, -6, tdata_2, 0x0000dead )
        TEST_LD_OP( lhu, -4, tdata_2, 0x000000ff )
        TEST_LD_OP( lhu, -2, tdata_2, 0x0000ff00 )
        TEST_LD_OP( lhu,  0, tdata_2, 0x0000ff00 )
        TEST_LD_OP( lhu,  2, tdata_2, 0x000000ff )

        // Test with a negative base

        la    $2, tdata_0
        addiu $2, $2, -32
        lhu   $4, 34($2)
        TEST_CHECK_EQ( $4, 0x0000dead )

        // Test with unaligned base

        la    $2, tdata_0
        addiu $2, $2, -3
        lhu   $4, 5($2)
        TEST_CHECK_EQ( $4, 0x0000dead )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_LD_DEST_BYP( 0, lhu, 0, tdata_0, 0x0000beef )
        TEST_LD_DEST_BYP( 1, lhu, 2, tdata_0, 0x0000dead )
        TEST_LD_DEST_BYP( 2, lhu, 0, tdata_1, 0x000000ff )
        TEST_LD_DEST_BYP( 3, lhu, 2, tdata_1, 0x0000ff00 )
        TEST_LD_DEST_BYP( 4, lhu, 0, tdata_2, 0x0000ff00 )

        TEST_LD_SRC0_BYP( 0, lhu, 0, tdata_0, 0x0000beef )
        TEST_LD_SRC0_BYP( 1, lhu, 2, tdata_0, 0x0000dead )
        TEST_LD_SRC0_BYP( 2, lhu, 0, tdata_1, 0x000000ff )
        TEST_LD_SRC0_BYP( 3, lhu, 2, tdata_1, 0x0000ff00 )
        TEST_LD_SRC0_BYP( 4, lhu, 0, tdata_2, 0x0000ff00 )

        // WAW

        la  $4, tdata_0
        lhu $3, 2($4)
        li  $3, 2
        TEST_CHECK_EQ( $3, 2 )

        // RAW

        la    $5, tdata_0
        lhu   $6, 2($5)
        addiu $7, $6, 1
        TEST_CHECK_EQ( $7, 0x0000deae )

        TEST_PARC_END

        //--------------------------------------------------------------------
        // Test data
        //--------------------------------------------------------------------

        .data
        .align 4

tdata_0: .word 0xdeadbeef
tdata_1: .word 0xff0000ff
tdata_2: .word 0x00ffff00
