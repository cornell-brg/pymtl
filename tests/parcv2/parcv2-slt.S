//=========================================================================
// parcv2-slt.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( slt, 0x00000000, 0x00000000, 0 )
        TEST_RR_OP( slt, 0x00000001, 0x00000001, 0 )
        TEST_RR_OP( slt, 0x00000003, 0x00000007, 1 )
        TEST_RR_OP( slt, 0x00000007, 0x00000003, 0 )

        TEST_RR_OP( slt, 0x00000000, 0xffff8000, 0 )
        TEST_RR_OP( slt, 0x80000000, 0x00000000, 1 )
        TEST_RR_OP( slt, 0x80000000, 0xffff8000, 1 )

        TEST_RR_OP( slt, 0x00000000, 0x00007fff, 1 )
        TEST_RR_OP( slt, 0x7fffffff, 0x00000000, 0 )
        TEST_RR_OP( slt, 0x7fffffff, 0x00007fff, 0 )

        TEST_RR_OP( slt, 0x80000000, 0x00007fff, 1 )
        TEST_RR_OP( slt, 0x7fffffff, 0xffff8000, 0 )

        TEST_RR_OP( slt, 0x00000000, 0xffffffff, 0 )
        TEST_RR_OP( slt, 0xffffffff, 0x00000001, 1 )
        TEST_RR_OP( slt, 0xffffffff, 0xffffffff, 0 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( slt, 14, 13, 0 )
        TEST_RR_SRC1_EQ_DEST( slt, 11, 13, 1 )
        TEST_RR_SRCS_EQ_DEST( slt, 13, 0 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, slt, 11, 13, 1 )
        TEST_RR_DEST_BYP( 1, slt, 14, 13, 0 )
        TEST_RR_DEST_BYP( 2, slt, 12, 13, 1 )

        TEST_RR_SRC01_BYP( 0, 0, slt, 14, 13, 0 )
        TEST_RR_SRC01_BYP( 0, 1, slt, 11, 13, 1 )
        TEST_RR_SRC01_BYP( 0, 2, slt, 15, 13, 0 )
        TEST_RR_SRC01_BYP( 1, 0, slt, 10, 13, 1 )
        TEST_RR_SRC01_BYP( 1, 1, slt, 16, 13, 0 )
        TEST_RR_SRC01_BYP( 2, 0, slt,  9, 13, 1 )

        TEST_RR_SRC10_BYP( 0, 0, slt, 17, 13, 0 )
        TEST_RR_SRC10_BYP( 0, 1, slt,  8, 13, 1 )
        TEST_RR_SRC10_BYP( 0, 2, slt, 18, 13, 0 )
        TEST_RR_SRC10_BYP( 1, 0, slt,  7, 13, 1 )
        TEST_RR_SRC10_BYP( 1, 1, slt, 19, 13, 0 )
        TEST_RR_SRC10_BYP( 2, 0, slt,  6, 13, 1 )

        TEST_PARC_END

