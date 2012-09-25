//========================================================================
// parcv2-lb.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic tests
        //--------------------------------------------------------------------

        TEST_LD_OP( lb, 0, tdata_0, 0xffffffef )
        TEST_LD_OP( lb, 1, tdata_0, 0xffffffbe )
        TEST_LD_OP( lb, 2, tdata_0, 0xffffffad )
        TEST_LD_OP( lb, 3, tdata_0, 0xffffffde )

        TEST_LD_OP( lb, 4, tdata_0, 0x00000001 )
        TEST_LD_OP( lb, 5, tdata_0, 0xffffffef )
        TEST_LD_OP( lb, 6, tdata_0, 0xffffffcd )
        TEST_LD_OP( lb, 7, tdata_0, 0xffffffab )

        TEST_LD_OP( lb, 8, tdata_0, 0xfffffff0 )
        TEST_LD_OP( lb, 9, tdata_0, 0x0000000f )
        TEST_LD_OP( lb,10, tdata_0, 0xfffffff0 )
        TEST_LD_OP( lb,11, tdata_0, 0x0000000f )


        TEST_LD_OP( lb, -8, tdata_2, 0xffffffef )
        TEST_LD_OP( lb, -7, tdata_2, 0xffffffbe )
        TEST_LD_OP( lb, -6, tdata_2, 0xffffffad )
        TEST_LD_OP( lb, -5, tdata_2, 0xffffffde )

        TEST_LD_OP( lb, -4, tdata_2, 0x00000001 )
        TEST_LD_OP( lb, -3, tdata_2, 0xffffffef )
        TEST_LD_OP( lb, -2, tdata_2, 0xffffffcd )
        TEST_LD_OP( lb, -1, tdata_2, 0xffffffab )

        TEST_LD_OP( lb,  0, tdata_2, 0xfffffff0 )
        TEST_LD_OP( lb,  1, tdata_2, 0x0000000f )
        TEST_LD_OP( lb,  2, tdata_2, 0xfffffff0 )
        TEST_LD_OP( lb,  3, tdata_2, 0x0000000f )

        // Test with a negative base

        la    $2, tdata_0
        addiu $2, $2, -32
        lb    $4, 33($2)
        TEST_CHECK_EQ( $4, 0xffffffbe )

        // Test with unaligned base

        la    $2, tdata_0
        addiu $2, $2, -3
        lb    $4, 6($2)
        TEST_CHECK_EQ( $4, 0xffffffde )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_LD_DEST_BYP( 0, lb, 0, tdata_0, 0xffffffef )
        TEST_LD_DEST_BYP( 1, lb, 0, tdata_2, 0xfffffff0 )
        TEST_LD_DEST_BYP( 2, lb, 1, tdata_2, 0x0000000f )
        TEST_LD_DEST_BYP( 3, lb, 2, tdata_2, 0xfffffff0 )
        TEST_LD_DEST_BYP( 4, lb, 3, tdata_2, 0x0000000f )

        TEST_LD_SRC0_BYP( 0, lb, 0, tdata_0, 0xffffffef )
        TEST_LD_SRC0_BYP( 1, lb, 0, tdata_2, 0xfffffff0 )
        TEST_LD_SRC0_BYP( 2, lb, 1, tdata_2, 0x0000000f )
        TEST_LD_SRC0_BYP( 3, lb, 2, tdata_2, 0xfffffff0 )
        TEST_LD_SRC0_BYP( 4, lb, 3, tdata_2, 0x0000000f )

        // WAW

        la $4, tdata_0
        lb $3, 1($4)
        li $3, 2
        TEST_CHECK_EQ( $3, 2 )

        // RAW

        la    $5, tdata_0
        lb    $6, 1($5)
        addiu $7, $6, 1
        TEST_CHECK_EQ( $7, 0xffffffbf )

        TEST_PARC_END

        //--------------------------------------------------------------------
        // Test data
        //--------------------------------------------------------------------

        .data
        .align 4

tdata_0: .word 0xdeadbeef
tdata_1: .word 0xabcdef01
tdata_2: .word 0x0ff00ff0
