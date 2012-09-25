//=========================================================================
// parcv2-sllv.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( sllv, 0x00000001,  0, 0x00000001 )
        TEST_RR_OP( sllv, 0x00000001,  1, 0x00000002 )
        TEST_RR_OP( sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_OP( sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_OP( sllv, 0x00000001, 31, 0x80000000 )

        TEST_RR_OP( sllv, 0xffffffff,  0, 0xffffffff )
        TEST_RR_OP( sllv, 0xffffffff,  1, 0xfffffffe )
        TEST_RR_OP( sllv, 0xffffffff,  7, 0xffffff80 )
        TEST_RR_OP( sllv, 0xffffffff, 14, 0xffffc000 )
        TEST_RR_OP( sllv, 0xffffffff, 31, 0x80000000 )

        TEST_RR_OP( sllv, 0x21212121,  0, 0x21212121 )
        TEST_RR_OP( sllv, 0x21212121,  1, 0x42424242 )
        TEST_RR_OP( sllv, 0x21212121,  7, 0x90909080 )
        TEST_RR_OP( sllv, 0x21212121, 14, 0x48484000 )
        TEST_RR_OP( sllv, 0x21212121, 31, 0x80000000 )

        // Verify that shifts only use bottom five bits

        TEST_RR_OP( sllv, 0x21212121, 0xffffffe0, 0x21212121 )
        TEST_RR_OP( sllv, 0x21212121, 0xffffffe1, 0x42424242 )
        TEST_RR_OP( sllv, 0x21212121, 0xffffffe7, 0x90909080 )
        TEST_RR_OP( sllv, 0x21212121, 0xffffffee, 0x48484000 )
        TEST_RR_OP( sllv, 0x21212121, 0xffffffff, 0x80000000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_SRC1_EQ_DEST( sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_SRCS_EQ_DEST( sllv, 3, 24 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_DEST_BYP( 1, sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_DEST_BYP( 2, sllv, 0x00000001, 31, 0x80000000 )

        TEST_RR_SRC01_BYP( 0, 0, sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_SRC01_BYP( 0, 1, sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_SRC01_BYP( 0, 2, sllv, 0x00000001, 31, 0x80000000 )
        TEST_RR_SRC01_BYP( 1, 0, sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_SRC01_BYP( 1, 1, sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_SRC01_BYP( 2, 0, sllv, 0x00000001, 31, 0x80000000 )

        TEST_RR_SRC10_BYP( 0, 0, sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_SRC10_BYP( 0, 1, sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_SRC10_BYP( 0, 2, sllv, 0x00000001, 31, 0x80000000 )
        TEST_RR_SRC10_BYP( 1, 0, sllv, 0x00000001,  7, 0x00000080 )
        TEST_RR_SRC10_BYP( 1, 1, sllv, 0x00000001, 14, 0x00004000 )
        TEST_RR_SRC10_BYP( 2, 0, sllv, 0x00000001, 31, 0x80000000 )

        TEST_PARC_END

