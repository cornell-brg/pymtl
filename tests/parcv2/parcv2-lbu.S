//========================================================================
// parcv2-lbu.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic tests
        //--------------------------------------------------------------------

        TEST_LD_OP( lbu, 0, tdata_0, 0x000000ef )
        TEST_LD_OP( lbu, 1, tdata_0, 0x000000be )
        TEST_LD_OP( lbu, 2, tdata_0, 0x000000ad )
        TEST_LD_OP( lbu, 3, tdata_0, 0x000000de )

        TEST_LD_OP( lbu, 4, tdata_0, 0x00000001 )
        TEST_LD_OP( lbu, 5, tdata_0, 0x000000ef )
        TEST_LD_OP( lbu, 6, tdata_0, 0x000000cd )
        TEST_LD_OP( lbu, 7, tdata_0, 0x000000ab )

        TEST_LD_OP( lbu, 8, tdata_0, 0x000000f0 )
        TEST_LD_OP( lbu, 9, tdata_0, 0x0000000f )
        TEST_LD_OP( lbu,10, tdata_0, 0x000000f0 )
        TEST_LD_OP( lbu,11, tdata_0, 0x0000000f )


        TEST_LD_OP( lbu, -8, tdata_2, 0x000000ef )
        TEST_LD_OP( lbu, -7, tdata_2, 0x000000be )
        TEST_LD_OP( lbu, -6, tdata_2, 0x000000ad )
        TEST_LD_OP( lbu, -5, tdata_2, 0x000000de )

        TEST_LD_OP( lbu, -4, tdata_2, 0x00000001 )
        TEST_LD_OP( lbu, -3, tdata_2, 0x000000ef )
        TEST_LD_OP( lbu, -2, tdata_2, 0x000000cd )
        TEST_LD_OP( lbu, -1, tdata_2, 0x000000ab )

        TEST_LD_OP( lbu,  0, tdata_2, 0x000000f0 )
        TEST_LD_OP( lbu,  1, tdata_2, 0x0000000f )
        TEST_LD_OP( lbu,  2, tdata_2, 0x000000f0 )
        TEST_LD_OP( lbu,  3, tdata_2, 0x0000000f )

        // Test with a negative base

        la    $2, tdata_0
        addiu $2, $2, -32
        lbu   $4, 33($2)
        TEST_CHECK_EQ( $4, 0x000000be )

        // Test with unaligned base

        la     $2, tdata_0
        addiu  $2, $2, -3
        lbu    $4, 6($2)
        TEST_CHECK_EQ( $4, 0x000000de )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_LD_DEST_BYP( 0, lbu, 0, tdata_0, 0x000000ef )
        TEST_LD_DEST_BYP( 1, lbu, 0, tdata_2, 0x000000f0 )
        TEST_LD_DEST_BYP( 2, lbu, 1, tdata_2, 0x0000000f )
        TEST_LD_DEST_BYP( 3, lbu, 2, tdata_2, 0x000000f0 )
        TEST_LD_DEST_BYP( 4, lbu, 3, tdata_2, 0x0000000f )

        TEST_LD_SRC0_BYP( 0, lbu, 0, tdata_0, 0x000000ef )
        TEST_LD_SRC0_BYP( 1, lbu, 0, tdata_2, 0x000000f0 )
        TEST_LD_SRC0_BYP( 2, lbu, 1, tdata_2, 0x0000000f )
        TEST_LD_SRC0_BYP( 3, lbu, 2, tdata_2, 0x000000f0 )
        TEST_LD_SRC0_BYP( 4, lbu, 3, tdata_2, 0x0000000f )

        // WAW

        la  $4, tdata_0
        lbu $3, 1($4)
        li  $3, 2
        TEST_CHECK_EQ( $3, 2 )

        // RAW

        la    $5, tdata_0
        lbu   $6, 1($5)
        addiu $7, $6, 1
        TEST_CHECK_EQ( $7, 0x000000bf )

        TEST_PARC_END

        //--------------------------------------------------------------------
        // Test data
        //--------------------------------------------------------------------

        .data
        .align 4

tdata_0: .word 0xdeadbeef
tdata_1: .word 0xabcdef01
tdata_2: .word 0x0ff00ff0
