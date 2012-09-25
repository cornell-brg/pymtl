//========================================================================
// parcv2-mul.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------

        // Zero and one operands

        TEST_RR_OP( mul,  0,  0, 0 )
        TEST_RR_OP( mul,  0,  1, 0 )
        TEST_RR_OP( mul,  1,  0, 0 )
        TEST_RR_OP( mul,  1,  1, 1 )
        TEST_RR_OP( mul,  0, -1, 0 )
        TEST_RR_OP( mul, -1,  0, 0 )
        TEST_RR_OP( mul, -1, -1, 1 )

        // Positive operands

        TEST_RR_OP( mul,    42,   13,       546 )
        TEST_RR_OP( mul,   716,   89,     63724 )
        TEST_RR_OP( mul, 20154, 8330, 167882820 )

        // Negative operands

        TEST_RR_OP( mul,    42,    -13,      -546 )
        TEST_RR_OP( mul,  -716,     89,    -63724 )
        TEST_RR_OP( mul, -20154, -8330, 167882820 )

        // Mixed tests

        TEST_RR_OP( mul, 0x0deadbee, 0x10000000, 0xe0000000 )
        TEST_RR_OP( mul, 0xdeadbeef, 0x10000000, 0xf0000000 )

        //--------------------------------------------------------------------
        // Source/Destination tests
        //--------------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( mul, 13, 11, 143 )
        TEST_RR_SRC1_EQ_DEST( mul, 14, 11, 154 )
        TEST_RR_SRC0_EQ_SRC1( mul, 15, 225 )
        TEST_RR_SRCS_EQ_DEST( mul, 16, 256 )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, mul, 13, 11, 143 )
        TEST_RR_DEST_BYP( 1, mul, 14, 11, 154 )
        TEST_RR_DEST_BYP( 2, mul, 15, 11, 165 )
        TEST_RR_DEST_BYP( 3, mul, 16, 11, 176 )
        TEST_RR_DEST_BYP( 4, mul, 17, 11, 187 )

        TEST_RR_SRC01_BYP( 0, 0, mul, 13, 11, 143 )
        TEST_RR_SRC01_BYP( 0, 1, mul, 14, 11, 154 )
        TEST_RR_SRC01_BYP( 0, 2, mul, 15, 11, 165 )
        TEST_RR_SRC01_BYP( 0, 3, mul, 16, 11, 176 )
        TEST_RR_SRC01_BYP( 0, 4, mul, 17, 11, 187 )

        TEST_RR_SRC01_BYP( 1, 0, mul, 13, 11, 143 )
        TEST_RR_SRC01_BYP( 1, 1, mul, 14, 11, 154 )
        TEST_RR_SRC01_BYP( 2, 0, mul, 15, 11, 165 )

        TEST_RR_SRC10_BYP( 0, 0, mul, 13, 11, 143 )
        TEST_RR_SRC10_BYP( 0, 1, mul, 14, 11, 154 )
        TEST_RR_SRC10_BYP( 0, 2, mul, 15, 11, 165 )
        TEST_RR_SRC10_BYP( 0, 3, mul, 16, 11, 176 )
        TEST_RR_SRC10_BYP( 0, 4, mul, 17, 11, 187 )

        TEST_RR_SRC10_BYP( 1, 0, mul, 13, 11, 143 )
        TEST_RR_SRC10_BYP( 1, 1, mul, 14, 11, 154 )
        TEST_RR_SRC10_BYP( 2, 0, mul, 15, 11, 165 )

        TEST_PARC_END

