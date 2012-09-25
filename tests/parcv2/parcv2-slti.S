//=========================================================================
// parcv2-slti.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_IMM_OP( slti, 0x00000000, 0x0000, 0 )
        TEST_IMM_OP( slti, 0x00000001, 0x0001, 0 )
        TEST_IMM_OP( slti, 0x00000003, 0x0007, 1 )
        TEST_IMM_OP( slti, 0x00000007, 0x0003, 0 )

        TEST_IMM_OP( slti, 0x00000000, 0x8000, 0 )
        TEST_IMM_OP( slti, 0x80000000, 0x0000, 1 )
        TEST_IMM_OP( slti, 0x80000000, 0x8000, 1 )

        TEST_IMM_OP( slti, 0x00000000, 0x7fff, 1 )
        TEST_IMM_OP( slti, 0x7fffffff, 0x0000, 0 )
        TEST_IMM_OP( slti, 0x7fffffff, 0x7fff, 0 )

        TEST_IMM_OP( slti, 0x80000000, 0x7fff, 1 )
        TEST_IMM_OP( slti, 0x7fffffff, 0x8000, 0 )

        TEST_IMM_OP( slti, 0x00000000, 0xffff, 0 )
        TEST_IMM_OP( slti, 0xffffffff, 0x0001, 1 )
        TEST_IMM_OP( slti, 0xffffffff, 0xffff, 0 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_IMM_SRC0_EQ_DEST( slti, 11, 13, 1 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_IMM_DEST_BYP( 0, slti, 15, 10, 0 )
        TEST_IMM_DEST_BYP( 1, slti, 10, 16, 1 )
        TEST_IMM_DEST_BYP( 2, slti, 16,  9, 0 )

        TEST_IMM_SRC0_BYP( 0, slti, 11, 15, 1 )
        TEST_IMM_SRC0_BYP( 1, slti, 17,  8, 0 )
        TEST_IMM_SRC0_BYP( 2, slti, 12, 14, 1 )

        TEST_PARC_END

