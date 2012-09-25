//=========================================================================
// parcv1-jr.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Basic test
        //-----------------------------------------------------------------

test:
        li $29, __LINE__
        li $31, 0
        la $3, target

linkaddr:
        jr $3
        nop
        nop

        j _fail

target:

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_JR_SRC0_BYP( 0, jr )
        TEST_JR_SRC0_BYP( 1, jr )
        TEST_JR_SRC0_BYP( 2, jr )

        // Test that there is no branch delay slot

        li $2, 1
        la $3, 1f
        jr $3
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
    1:  addiu $2, 1
        addiu $2, 1
        TEST_CHECK_EQ( $2, 3 )

        TEST_PARC_END

