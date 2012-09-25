//=========================================================================
// parcv2-jalr.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Basic test
        //-----------------------------------------------------------------

test_0:
        li $29, __LINE__
        li $31, 0
        la $3, target_0

linkaddr_0:
        jalr $16, $3
        nop
        nop
        TEST_CHECK_FAIL

target_0:
        la $2, linkaddr_0
        addiu $2, $2, 4
        bne $2, $16, _fail

        //-----------------------------------------------------------------
        // Check r0 target and that r31 is not modified
        //-----------------------------------------------------------------

test_1:
        li $29, __LINE__
        li $31, 0
        la $3, target_1

linkaddr_1:
        jalr $0, $3
        nop
        nop
        TEST_CHECK_FAIL

target_1:
        bne $0, $31, _fail

        //-----------------------------------------------------------------
        // Check return addres stored to r31 by default
        //-----------------------------------------------------------------

test_2:
        li $29, __LINE__
        li $31, 0
        la $3, target_2

linkaddr_2:
        jalr $3
        nop
        nop
        TEST_CHECK_FAIL

target_2:
        la $2, linkaddr_2
        addiu $2, $2, 4
        bne $2, $31, _fail

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_JALR_SRC0_BYP( 0, jalr )
        TEST_JALR_SRC0_BYP( 1, jalr )
        TEST_JALR_SRC0_BYP( 2, jalr )

        //-----------------------------------------------------------------
        // Test that there is no branch delay slot
        //-----------------------------------------------------------------

        li    $2, 1
        la    $3, 1f
        jalr  $16, $3
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
    1:  addiu $2, 1
        addiu $2, 1
        TEST_CHECK_EQ( $2, 3 )

        TEST_PARC_END

