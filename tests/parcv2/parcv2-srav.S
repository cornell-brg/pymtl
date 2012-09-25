//=========================================================================
// parcv2-srav.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( srav, 0x80000000,  0, 0x80000000 )
        TEST_RR_OP( srav, 0x80000000,  1, 0xc0000000 )
        TEST_RR_OP( srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_OP( srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_OP( srav, 0x80000001, 31, 0xffffffff )

        TEST_RR_OP( srav, 0x7fffffff,  0, 0x7fffffff )
        TEST_RR_OP( srav, 0x7fffffff,  1, 0x3fffffff )
        TEST_RR_OP( srav, 0x7fffffff,  7, 0x00ffffff )
        TEST_RR_OP( srav, 0x7fffffff, 14, 0x0001ffff )
        TEST_RR_OP( srav, 0x7fffffff, 31, 0x00000000 )

        TEST_RR_OP( srav, 0x81818181,  0, 0x81818181 )
        TEST_RR_OP( srav, 0x81818181,  1, 0xc0c0c0c0 )
        TEST_RR_OP( srav, 0x81818181,  7, 0xff030303 )
        TEST_RR_OP( srav, 0x81818181, 14, 0xfffe0606 )
        TEST_RR_OP( srav, 0x81818181, 31, 0xffffffff )

        // Verify that shifts only use bottom five bits

        TEST_RR_OP( srav, 0x81818181, 0xffffffe0, 0x81818181 )
        TEST_RR_OP( srav, 0x81818181, 0xffffffe1, 0xc0c0c0c0 )
        TEST_RR_OP( srav, 0x81818181, 0xffffffe7, 0xff030303 )
        TEST_RR_OP( srav, 0x81818181, 0xffffffee, 0xfffe0606 )
        TEST_RR_OP( srav, 0x81818181, 0xffffffff, 0xffffffff )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_SRC1_EQ_DEST( srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_SRCS_EQ_DEST( srav, 7, 0 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_DEST_BYP( 1, srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_DEST_BYP( 2, srav, 0x80000000, 31, 0xffffffff )

        TEST_RR_SRC01_BYP( 0, 0, srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_SRC01_BYP( 0, 1, srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_SRC01_BYP( 0, 2, srav, 0x80000000, 31, 0xffffffff )
        TEST_RR_SRC01_BYP( 1, 0, srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_SRC01_BYP( 1, 1, srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_SRC01_BYP( 2, 0, srav, 0x80000000, 31, 0xffffffff )

        TEST_RR_SRC10_BYP( 0, 0, srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_SRC10_BYP( 0, 1, srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_SRC10_BYP( 0, 2, srav, 0x80000000, 31, 0xffffffff )
        TEST_RR_SRC10_BYP( 1, 0, srav, 0x80000000,  7, 0xff000000 )
        TEST_RR_SRC10_BYP( 1, 1, srav, 0x80000000, 14, 0xfffe0000 )
        TEST_RR_SRC10_BYP( 2, 0, srav, 0x80000000, 31, 0xffffffff )

        TEST_PARC_END

