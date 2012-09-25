//=========================================================================
// parcv1-jal.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Basic test
        //-----------------------------------------------------------------

test:
        li $29, __LINE__
        li $31, 0

linkaddr:
        jal target
        nop
        nop

        j _fail

target:
        la $2, linkaddr
        addiu $2, $2, 4
        bne $2, $31, _fail


        // Test that there is no branch delay slot

        li $2, 1
        jal 1f
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
    1:  addiu $2, 1
        addiu $2, 1
        TEST_CHECK_EQ( $2, 3 )

        TEST_PARC_END

