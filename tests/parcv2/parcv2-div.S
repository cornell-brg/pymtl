//========================================================================
// parcv2-div.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------

        // Zero and one operands

        TEST_RR_OP( div,  0,  1, 0 )
        TEST_RR_OP( div,  1,  1, 1 )
        TEST_RR_OP( div,  0, -1, 0 )
        TEST_RR_OP( div, -1, -1, 1 )

        // Positive evenly-divisible operands

        TEST_RR_OP( div,       546,    42,   13 )
        TEST_RR_OP( div,     63724,   716,   89 )
        TEST_RR_OP( div, 167882820, 20154, 8330 )

        // Negative evenly-divisible operands

        TEST_RR_OP( div,      -546,     42,   -13 )
        TEST_RR_OP( div,    -63724,   -716,    89 )
        TEST_RR_OP( div, 167882820, -20154, -8330 )

        // Positive not evenly-divisible operands

        TEST_RR_OP( div,        50,   546,    0 )
        TEST_RR_OP( div,       546,    50,   10 )
        TEST_RR_OP( div,     63724,   793,   80 )
        TEST_RR_OP( div, 167882820, 20150, 8331 )

        // Negative not evenly-divisible operands

        TEST_RR_OP( div,        50,   -546,     0 )
        TEST_RR_OP( div,      -546,     50,   -10 )
        TEST_RR_OP( div,    -63724,   -793,    80 )
        TEST_RR_OP( div, 167882820, -20150, -8331 )

        // Mixed tests

        TEST_RR_OP( div, 0xdeadbeef, 0x0000beef, 0xffffd353 )
        TEST_RR_OP( div, 0xf5fe4fbc, 0x00004eb6, 0xffffdf75 )
        TEST_RR_OP( div, 0xf5fe4fbc, 0xffffb14a, 0x0000208b )

        //--------------------------------------------------------------------
        // Source/Destination tests
        //--------------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( div, 143, 11, 13 )
        TEST_RR_SRC1_EQ_DEST( div, 154, 11, 14 )
        TEST_RR_SRC0_EQ_SRC1( div, 15, 1 )
        TEST_RR_SRCS_EQ_DEST( div, 16, 1 )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, div, 143, 11, 13 )
        TEST_RR_DEST_BYP( 1, div, 154, 11, 14 )
        TEST_RR_DEST_BYP( 2, div, 165, 11, 15 )
        TEST_RR_DEST_BYP( 3, div, 176, 11, 16 )
        TEST_RR_DEST_BYP( 4, div, 187, 11, 17 )

        TEST_RR_SRC01_BYP( 0, 0, div, 143, 11, 13 )
        TEST_RR_SRC01_BYP( 0, 1, div, 154, 11, 14 )
        TEST_RR_SRC01_BYP( 0, 2, div, 165, 11, 15 )
        TEST_RR_SRC01_BYP( 0, 3, div, 176, 11, 16 )
        TEST_RR_SRC01_BYP( 0, 4, div, 187, 11, 17 )

        TEST_RR_SRC01_BYP( 1, 0, div, 143, 11, 13 )
        TEST_RR_SRC01_BYP( 1, 1, div, 154, 11, 14 )
        TEST_RR_SRC01_BYP( 2, 0, div, 165, 11, 15 )

        TEST_RR_SRC10_BYP( 0, 0, div, 143, 11, 13 )
        TEST_RR_SRC10_BYP( 0, 1, div, 154, 11, 14 )
        TEST_RR_SRC10_BYP( 0, 2, div, 165, 11, 15 )
        TEST_RR_SRC10_BYP( 0, 3, div, 176, 11, 16 )
        TEST_RR_SRC10_BYP( 0, 4, div, 187, 11, 17 )

        TEST_RR_SRC10_BYP( 1, 0, div, 143, 11, 13 )
        TEST_RR_SRC10_BYP( 1, 1, div, 154, 11, 14 )
        TEST_RR_SRC10_BYP( 2, 0, div, 165, 11, 15 )

        TEST_PARC_END

