//========================================================================
// parcv2-divu.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------

        // Zero and one operands

        TEST_RR_OP( divu,  0,  1, 0 )
        TEST_RR_OP( divu,  1,  1, 1 )

        // Positive evenly-divisible operands

        TEST_RR_OP( divu,       546,    42,   13 )
        TEST_RR_OP( divu,     63724,   716,   89 )
        TEST_RR_OP( divu, 167882820, 20154, 8330 )

        // Positive not evenly-divisible operands

        TEST_RR_OP( divu,        50,   546,    0 )
        TEST_RR_OP( divu,       546,    50,   10 )
        TEST_RR_OP( divu,     63724,   793,   80 )
        TEST_RR_OP( divu, 167882820, 20150, 8331 )

        // Test that operands are treated as unsigned

        TEST_RR_OP( divu, 0x00000000, 0xffffffff, 0x00000000 )
        TEST_RR_OP( divu, 0xffffffff, 0xffffffff, 0x00000001 )
        TEST_RR_OP( divu, 0x0a01b044, 0xffffb14a, 0x00000000 )
        TEST_RR_OP( divu, 0xdeadbeef, 0x0000beef, 0x00012a90 )
        TEST_RR_OP( divu, 0xf5fe4fbc, 0x00004eb6, 0x00032012 )
        TEST_RR_OP( divu, 0xf5fe4fbc, 0xffffb14a, 0x00000000 )

        //--------------------------------------------------------------------
        // Source/Destination tests
        //--------------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( divu, 143, 11, 13 )
        TEST_RR_SRC1_EQ_DEST( divu, 154, 11, 14 )
        TEST_RR_SRC0_EQ_SRC1( divu, 15, 1 )
        TEST_RR_SRCS_EQ_DEST( divu, 16, 1 )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, divu, 143, 11, 13 )
        TEST_RR_DEST_BYP( 1, divu, 154, 11, 14 )
        TEST_RR_DEST_BYP( 2, divu, 165, 11, 15 )
        TEST_RR_DEST_BYP( 3, divu, 176, 11, 16 )
        TEST_RR_DEST_BYP( 4, divu, 187, 11, 17 )

        TEST_RR_SRC01_BYP( 0, 0, divu, 143, 11, 13 )
        TEST_RR_SRC01_BYP( 0, 1, divu, 154, 11, 14 )
        TEST_RR_SRC01_BYP( 0, 2, divu, 165, 11, 15 )
        TEST_RR_SRC01_BYP( 0, 3, divu, 176, 11, 16 )
        TEST_RR_SRC01_BYP( 0, 4, divu, 187, 11, 17 )

        TEST_RR_SRC01_BYP( 1, 0, divu, 143, 11, 13 )
        TEST_RR_SRC01_BYP( 1, 1, divu, 154, 11, 14 )
        TEST_RR_SRC01_BYP( 2, 0, divu, 165, 11, 15 )

        TEST_RR_SRC10_BYP( 0, 0, divu, 143, 11, 13 )
        TEST_RR_SRC10_BYP( 0, 1, divu, 154, 11, 14 )
        TEST_RR_SRC10_BYP( 0, 2, divu, 165, 11, 15 )
        TEST_RR_SRC10_BYP( 0, 3, divu, 176, 11, 16 )
        TEST_RR_SRC10_BYP( 0, 4, divu, 187, 11, 17 )

        TEST_RR_SRC10_BYP( 1, 0, divu, 143, 11, 13 )
        TEST_RR_SRC10_BYP( 1, 1, divu, 154, 11, 14 )
        TEST_RR_SRC10_BYP( 2, 0, divu, 165, 11, 15 )

        TEST_PARC_END

