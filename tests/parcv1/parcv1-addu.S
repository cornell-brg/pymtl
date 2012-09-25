//=========================================================================
// parcv1-addu.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( addu, 0x00000000, 0x00000000, 0x00000000 )
        TEST_RR_OP( addu, 0x00000001, 0x00000001, 0x00000002 )
        TEST_RR_OP( addu, 0x00000003, 0x00000007, 0x0000000a )

        TEST_RR_OP( addu, 0x00000000, 0xffff8000, 0xffff8000 )
        TEST_RR_OP( addu, 0x80000000, 0x00000000, 0x80000000 )
        TEST_RR_OP( addu, 0x80000000, 0xffff8000, 0x7fff8000 )

        TEST_RR_OP( addu, 0x00000000, 0x00007fff, 0x00007fff )
        TEST_RR_OP( addu, 0x7fffffff, 0x00000000, 0x7fffffff )
        TEST_RR_OP( addu, 0x7fffffff, 0x00007fff, 0x80007ffe )

        TEST_RR_OP( addu, 0x80000000, 0x00007fff, 0x80007fff )
        TEST_RR_OP( addu, 0x7fffffff, 0xffff8000, 0x7fff7fff )

        TEST_RR_OP( addu, 0x00000000, 0xffffffff, 0xffffffff )
        TEST_RR_OP( addu, 0xffffffff, 0x00000001, 0x00000000 )
        TEST_RR_OP( addu, 0xffffffff, 0xffffffff, 0xfffffffe )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( addu, 13, 11, 24 )
        TEST_RR_SRC1_EQ_DEST( addu, 14, 11, 25 )
        TEST_RR_SRC0_EQ_SRC1( addu, 15, 30 )
        TEST_RR_SRCS_EQ_DEST( addu, 16, 32 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, addu, 13, 11, 24 )
        TEST_RR_DEST_BYP( 1, addu, 14, 11, 25 )
        TEST_RR_DEST_BYP( 2, addu, 15, 11, 26 )

        TEST_RR_SRC01_BYP( 0, 0, addu, 13, 11, 24 )
        TEST_RR_SRC01_BYP( 0, 1, addu, 14, 11, 25 )
        TEST_RR_SRC01_BYP( 0, 2, addu, 15, 11, 26 )
        TEST_RR_SRC01_BYP( 1, 0, addu, 13, 11, 24 )
        TEST_RR_SRC01_BYP( 1, 1, addu, 14, 11, 25 )
        TEST_RR_SRC01_BYP( 2, 0, addu, 15, 11, 26 )

        TEST_RR_SRC10_BYP( 0, 0, addu, 13, 11, 24 )
        TEST_RR_SRC10_BYP( 0, 1, addu, 14, 11, 25 )
        TEST_RR_SRC10_BYP( 0, 2, addu, 15, 11, 26 )
        TEST_RR_SRC10_BYP( 1, 0, addu, 13, 11, 24 )
        TEST_RR_SRC10_BYP( 1, 1, addu, 14, 11, 25 )
        TEST_RR_SRC10_BYP( 2, 0, addu, 15, 11, 26 )

        TEST_PARC_END

