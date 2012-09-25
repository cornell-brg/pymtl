//=========================================================================
// parcv1-bne.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Branch tests
        //-----------------------------------------------------------------

        TEST_BR2_OP_TAKEN( bne,  0,  1 )
        TEST_BR2_OP_TAKEN( bne,  1,  0 )
        TEST_BR2_OP_TAKEN( bne, -1,  1 )
        TEST_BR2_OP_TAKEN( bne,  1, -1 )

        TEST_BR2_OP_NOTTAKEN( bne,  0,  0 )
        TEST_BR2_OP_NOTTAKEN( bne,  1,  1 )
        TEST_BR2_OP_NOTTAKEN( bne, -1, -1 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_BR2_SRC01_BYP( 0, 0, bne, 0, 0 )
        TEST_BR2_SRC01_BYP( 0, 1, bne, 0, 0 )
        TEST_BR2_SRC01_BYP( 0, 2, bne, 0, 0 )
        TEST_BR2_SRC01_BYP( 1, 0, bne, 0, 0 )
        TEST_BR2_SRC01_BYP( 1, 1, bne, 0, 0 )
        TEST_BR2_SRC01_BYP( 2, 0, bne, 0, 0 )

        TEST_BR2_SRC10_BYP( 0, 0, bne, 0, 0 )
        TEST_BR2_SRC10_BYP( 0, 1, bne, 0, 0 )
        TEST_BR2_SRC10_BYP( 0, 2, bne, 0, 0 )
        TEST_BR2_SRC10_BYP( 1, 0, bne, 0, 0 )
        TEST_BR2_SRC10_BYP( 1, 1, bne, 0, 0 )
        TEST_BR2_SRC10_BYP( 2, 0, bne, 0, 0 )

        // Test that there is no branch delay slot

        li $2, 1
        bne $2, $0, 1f
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
        addiu $2, 1
    1:  addiu $2, 1
        addiu $2, 1
        TEST_CHECK_EQ( $2, 3 )

        TEST_PARC_END

