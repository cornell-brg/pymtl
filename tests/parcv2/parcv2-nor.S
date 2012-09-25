//=========================================================================
// parcv2-nor.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Logical tests
        //-----------------------------------------------------------------

        TEST_RR_OP( nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_OP( nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_OP( nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )
        TEST_RR_OP( nor, 0xf00ff00f, 0xf0f0f0f0, 0x0f000f00 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRC1_EQ_DEST( nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRCS_EQ_DEST( nor, 0xff00ff00, 0x00ff00ff )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_DEST_BYP( 1, nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_DEST_BYP( 2, nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )

        TEST_RR_SRC01_BYP( 0, 0, nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRC01_BYP( 0, 1, nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_SRC01_BYP( 0, 2, nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )
        TEST_RR_SRC01_BYP( 1, 0, nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRC01_BYP( 1, 1, nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_SRC01_BYP( 2, 0, nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )

        TEST_RR_SRC10_BYP( 0, 0, nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRC10_BYP( 0, 1, nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_SRC10_BYP( 0, 2, nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )
        TEST_RR_SRC10_BYP( 1, 0, nor, 0xff00ff00, 0x0f0f0f0f, 0x00f000f0 )
        TEST_RR_SRC10_BYP( 1, 1, nor, 0x0ff00ff0, 0xf0f0f0f0, 0x000f000f )
        TEST_RR_SRC10_BYP( 2, 0, nor, 0x00ff00ff, 0x0f0f0f0f, 0xf000f000 )

        TEST_PARC_END

