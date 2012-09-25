//=========================================================================
// parcv2-xor.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Logical tests
        //-----------------------------------------------------------------

        TEST_RR_OP( xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_OP( xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_OP( xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )
        TEST_RR_OP( xor, 0xf00ff00f, 0xf0f0f0f0, 0x00ff00ff )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRC1_EQ_DEST( xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRCS_EQ_DEST( xor, 0xff00ff00, 0x00000000 ) 

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_DEST_BYP( 1, xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_DEST_BYP( 2, xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )

        TEST_RR_SRC01_BYP( 0, 0, xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRC01_BYP( 0, 1, xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_SRC01_BYP( 0, 2, xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )
        TEST_RR_SRC01_BYP( 1, 0, xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRC01_BYP( 1, 1, xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_SRC01_BYP( 2, 0, xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )

        TEST_RR_SRC10_BYP( 0, 0, xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRC10_BYP( 0, 1, xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_SRC10_BYP( 0, 2, xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )
        TEST_RR_SRC10_BYP( 1, 0, xor, 0xff00ff00, 0x0f0f0f0f, 0xf00ff00f )
        TEST_RR_SRC10_BYP( 1, 1, xor, 0x0ff00ff0, 0xf0f0f0f0, 0xff00ff00 )
        TEST_RR_SRC10_BYP( 2, 0, xor, 0x00ff00ff, 0x0f0f0f0f, 0x0ff00ff0 )

        TEST_PARC_END

