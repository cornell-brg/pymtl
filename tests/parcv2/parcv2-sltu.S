//=========================================================================
// parcv2-sltu.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( sltu, 0x00000000, 0x00000000, 0 )
        TEST_RR_OP( sltu, 0x00000001, 0x00000001, 0 )
        TEST_RR_OP( sltu, 0x00000003, 0x00000007, 1 )
        TEST_RR_OP( sltu, 0x00000007, 0x00000003, 0 )

        TEST_RR_OP( sltu, 0x00000000, 0xffff8000, 1 )
        TEST_RR_OP( sltu, 0x80000000, 0x00000000, 0 )
        TEST_RR_OP( sltu, 0x80000000, 0xffff8000, 1 )

        TEST_RR_OP( sltu, 0x00000000, 0x00007fff, 1 )
        TEST_RR_OP( sltu, 0x7fffffff, 0x00000000, 0 )
        TEST_RR_OP( sltu, 0x7fffffff, 0x00007fff, 0 )

        TEST_RR_OP( sltu, 0x80000000, 0x00007fff, 0 )
        TEST_RR_OP( sltu, 0x7fffffff, 0xffff8000, 1 )

        TEST_RR_OP( sltu, 0x00000000, 0xffffffff, 1 )
        TEST_RR_OP( sltu, 0xffffffff, 0x00000001, 0 )
        TEST_RR_OP( sltu, 0xffffffff, 0xffffffff, 0 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( sltu, 14, 13, 0 )
        TEST_RR_SRC1_EQ_DEST( sltu, 11, 13, 1 )
        TEST_RR_SRCS_EQ_DEST( sltu, 13, 0 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, sltu, 11, 13, 1 )
        TEST_RR_DEST_BYP( 1, sltu, 14, 13, 0 )
        TEST_RR_DEST_BYP( 2, sltu, 12, 13, 1 )

        TEST_RR_SRC01_BYP( 0, 0, sltu, 14, 13, 0 )
        TEST_RR_SRC01_BYP( 0, 1, sltu, 11, 13, 1 )
        TEST_RR_SRC01_BYP( 0, 2, sltu, 15, 13, 0 )
        TEST_RR_SRC01_BYP( 1, 0, sltu, 10, 13, 1 )
        TEST_RR_SRC01_BYP( 1, 1, sltu, 16, 13, 0 )
        TEST_RR_SRC01_BYP( 2, 0, sltu,  9, 13, 1 )

        TEST_RR_SRC10_BYP( 0, 0, sltu, 17, 13, 0 )
        TEST_RR_SRC10_BYP( 0, 1, sltu,  8, 13, 1 )
        TEST_RR_SRC10_BYP( 0, 2, sltu, 18, 13, 0 )
        TEST_RR_SRC10_BYP( 1, 0, sltu,  7, 13, 1 )
        TEST_RR_SRC10_BYP( 1, 1, sltu, 19, 13, 0 )
        TEST_RR_SRC10_BYP( 2, 0, sltu,  6, 13, 1 )

        TEST_PARC_END

