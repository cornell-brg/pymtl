//=========================================================================
// parcv2-srlv.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( srlv, 0x80000000,  0, 0x80000000 )
        TEST_RR_OP( srlv, 0x80000000,  1, 0x40000000 )
        TEST_RR_OP( srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_OP( srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_OP( srlv, 0x80000001, 31, 0x00000001 )

        TEST_RR_OP( srlv, 0xffffffff,  0, 0xffffffff )
        TEST_RR_OP( srlv, 0xffffffff,  1, 0x7fffffff )
        TEST_RR_OP( srlv, 0xffffffff,  7, 0x01ffffff )
        TEST_RR_OP( srlv, 0xffffffff, 14, 0x0003ffff )
        TEST_RR_OP( srlv, 0xffffffff, 31, 0x00000001 )

        TEST_RR_OP( srlv, 0x21212121,  0, 0x21212121 )
        TEST_RR_OP( srlv, 0x21212121,  1, 0x10909090 )
        TEST_RR_OP( srlv, 0x21212121,  7, 0x00424242 )
        TEST_RR_OP( srlv, 0x21212121, 14, 0x00008484 )
        TEST_RR_OP( srlv, 0x21212121, 31, 0x00000000 )

        // Verify that shifts only use bottom five bits

        TEST_RR_OP( srlv, 0x21212121, 0xffffffe0, 0x21212121 )
        TEST_RR_OP( srlv, 0x21212121, 0xffffffe1, 0x10909090 )
        TEST_RR_OP( srlv, 0x21212121, 0xffffffe7, 0x00424242 )
        TEST_RR_OP( srlv, 0x21212121, 0xffffffee, 0x00008484 )
        TEST_RR_OP( srlv, 0x21212121, 0xffffffff, 0x00000000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_SRC1_EQ_DEST( srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_SRCS_EQ_DEST( srlv, 7, 0 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_DEST_BYP( 1, srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_DEST_BYP( 2, srlv, 0x80000000, 31, 0x00000001 )

        TEST_RR_SRC01_BYP( 0, 0, srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_SRC01_BYP( 0, 1, srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_SRC01_BYP( 0, 2, srlv, 0x80000000, 31, 0x00000001 )
        TEST_RR_SRC01_BYP( 1, 0, srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_SRC01_BYP( 1, 1, srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_SRC01_BYP( 2, 0, srlv, 0x80000000, 31, 0x00000001 )

        TEST_RR_SRC10_BYP( 0, 0, srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_SRC10_BYP( 0, 1, srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_SRC10_BYP( 0, 2, srlv, 0x80000000, 31, 0x00000001 )
        TEST_RR_SRC10_BYP( 1, 0, srlv, 0x80000000,  7, 0x01000000 )
        TEST_RR_SRC10_BYP( 1, 1, srlv, 0x80000000, 14, 0x00020000 )
        TEST_RR_SRC10_BYP( 2, 0, srlv, 0x80000000, 31, 0x00000001 )

        TEST_PARC_END

