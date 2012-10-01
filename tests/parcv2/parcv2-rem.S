//========================================================================
// parcv2-rem.S
//========================================================================
// Although the definition of the sign of the remainder depends on the
// application, the PARC ISA defines it to be equal to the sign of the
// dividend, and is tested as thus in this assembly test.

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------

        // Zero and one operands

        TEST_RR_OP( rem,  0,  1, 0 )
        TEST_RR_OP( rem,  1,  1, 0 )
        TEST_RR_OP( rem,  0, -1, 0 )
        TEST_RR_OP( rem, -1, -1, 0 )

        // Positive evenly-divisible operands

        TEST_RR_OP( rem,       546,    42, 0 )
        TEST_RR_OP( rem,     63724,   716, 0 )
        TEST_RR_OP( rem, 167882820, 20154, 0 )

        // Positive not evenly-divisible operands

        TEST_RR_OP( rem,        50,   546,    50 )
        TEST_RR_OP( rem,       546,    50,    46 )
        TEST_RR_OP( rem,     63724,   793,   284 )
        TEST_RR_OP( rem, 167882820, 20150, 13170 )

        // Mixed tests

        TEST_RR_OP( rem, 0x0a01b044, 0xffffb146, 0x00000000 )
        TEST_RR_OP( rem, 0x0a01b044, 0xffffb14a, 0x00003372 )
        TEST_RR_OP( rem, 0xdeadbeef, 0x0000beef, 0xffffda72 )
        TEST_RR_OP( rem, 0xf5fe4fbc, 0x00004eb6, 0xffffcc8e )
        TEST_RR_OP( rem, 0xf5fe4fbc, 0xffffb14a, 0xffffcc8e )

        //--------------------------------------------------------------------
        // Source/Destination tests
        //--------------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( rem, 143, 10, 3 )
        TEST_RR_SRC1_EQ_DEST( rem, 154, 10, 4 )
        TEST_RR_SRC0_EQ_SRC1( rem, 15, 0 )
        TEST_RR_SRCS_EQ_DEST( rem, 16, 0 )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, rem, 143, 10, 3 )
        TEST_RR_DEST_BYP( 1, rem, 154, 10, 4 )
        TEST_RR_DEST_BYP( 2, rem, 165, 10, 5 )
        TEST_RR_DEST_BYP( 3, rem, 176, 10, 6 )
        TEST_RR_DEST_BYP( 4, rem, 187, 10, 7 )

        TEST_RR_SRC01_BYP( 0, 0, rem, 143, 10, 3 )
        TEST_RR_SRC01_BYP( 0, 1, rem, 154, 10, 4 )
        TEST_RR_SRC01_BYP( 0, 2, rem, 165, 10, 5 )
        TEST_RR_SRC01_BYP( 0, 3, rem, 176, 10, 6 )
        TEST_RR_SRC01_BYP( 0, 4, rem, 187, 10, 7 )

        TEST_RR_SRC01_BYP( 1, 0, rem, 143, 10, 3 )
        TEST_RR_SRC01_BYP( 1, 1, rem, 154, 10, 4 )
        TEST_RR_SRC01_BYP( 2, 0, rem, 165, 10, 5 )

        TEST_RR_SRC10_BYP( 0, 0, rem, 143, 10, 3 )
        TEST_RR_SRC10_BYP( 0, 1, rem, 154, 10, 4 )
        TEST_RR_SRC10_BYP( 0, 2, rem, 165, 10, 5 )
        TEST_RR_SRC10_BYP( 0, 3, rem, 176, 10, 6 )
        TEST_RR_SRC10_BYP( 0, 4, rem, 187, 10, 7 )

        TEST_RR_SRC10_BYP( 1, 0, rem, 143, 10, 3 )
        TEST_RR_SRC10_BYP( 1, 1, rem, 154, 10, 4 )
        TEST_RR_SRC10_BYP( 2, 0, rem, 165, 10, 5 )

        TEST_PARC_END

