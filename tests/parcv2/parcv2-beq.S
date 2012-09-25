//=========================================================================
// parcv2-beq.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Branch tests
        //-----------------------------------------------------------------

        TEST_BR2_OP_TAKEN( beq,  0,  0 )
        TEST_BR2_OP_TAKEN( beq,  1,  1 )
        TEST_BR2_OP_TAKEN( beq, -1, -1 )

        TEST_BR2_OP_NOTTAKEN( beq,  0,  1 )
        TEST_BR2_OP_NOTTAKEN( beq,  1,  0 )
        TEST_BR2_OP_NOTTAKEN( beq, -1,  1 )
        TEST_BR2_OP_NOTTAKEN( beq,  1, -1 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_BR2_SRC01_BYP( 0, 0, beq, 0, -1 )
        TEST_BR2_SRC01_BYP( 0, 1, beq, 0, -1 )
        TEST_BR2_SRC01_BYP( 0, 2, beq, 0, -1 )
        TEST_BR2_SRC01_BYP( 1, 0, beq, 0, -1 )
        TEST_BR2_SRC01_BYP( 1, 1, beq, 0, -1 )
        TEST_BR2_SRC01_BYP( 2, 0, beq, 0, -1 )

        TEST_BR2_SRC10_BYP( 0, 0, beq, 0, -1 )
        TEST_BR2_SRC10_BYP( 0, 1, beq, 0, -1 )
        TEST_BR2_SRC10_BYP( 0, 2, beq, 0, -1 )
        TEST_BR2_SRC10_BYP( 1, 0, beq, 0, -1 )
        TEST_BR2_SRC10_BYP( 1, 1, beq, 0, -1 )
        TEST_BR2_SRC10_BYP( 2, 0, beq, 0, -1 )

        // Test that there is no branch delay slot

        li    $2, 1
        beq   $0, $0, 1f
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
    1:  addiu $2, 1
        addiu $2, 1
        TEST_CHECK_EQ( $2, 3 )

        TEST_PARC_END

