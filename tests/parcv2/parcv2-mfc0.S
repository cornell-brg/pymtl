//========================================================================
// parcv2-mfc0.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic test
        //--------------------------------------------------------------------

        li   $2, 0
        mfc0 $2, $20
        TEST_CHECK_EQ( $2, 0xab )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        li   $2, 0
        mfc0 $2, $20
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0xab )

        li   $2, 0
        mfc0 $2, $20
        TEST_INSERT_NOPS( 1 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0xab )

        li   $2, 0
        mfc0 $2, $20
        TEST_INSERT_NOPS( 2 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0xab )

        li   $2, 0
        mfc0 $2, $20
        TEST_INSERT_NOPS( 3 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0xab )

        li   $2, 0
        mfc0 $2, $20
        TEST_INSERT_NOPS( 4 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0xab )

        TEST_PARC_END
