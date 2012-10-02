//=========================================================================
// parcv2-xori.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Logical tests
        //-----------------------------------------------------------------

        TEST_IMM_OP( xori, 0xff00ff00, 0x0f0f, 0xff00f00f )
        TEST_IMM_OP( xori, 0x0ff00ff0, 0xf0f0, 0x0ff0ff00 )
        TEST_IMM_OP( xori, 0x00ff00ff, 0x0f0f, 0x00ff0ff0 )
        TEST_IMM_OP( xori, 0xf00ff00f, 0xf0f0, 0xf00f00ff )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_IMM_SRC0_EQ_DEST( xori, 0xff00ff00, 0x0f0f, 0xff00f00f )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_IMM_DEST_BYP( 0, xori, 0x0ff00ff0, 0xf0f0, 0x0ff0ff00 )
        TEST_IMM_DEST_BYP( 1, xori, 0x00ff00ff, 0x0f0f, 0x00ff0ff0 )
        TEST_IMM_DEST_BYP( 2, xori, 0xf00ff00f, 0xf0f0, 0xf00f00ff )

        TEST_IMM_SRC0_BYP( 0, xori, 0x0ff00ff0, 0xf0f0, 0x0ff0ff00 )
        TEST_IMM_SRC0_BYP( 1, xori, 0x00ff00ff, 0x0f0f, 0x00ff0ff0 )
        TEST_IMM_SRC0_BYP( 2, xori, 0xf00ff00f, 0xf0f0, 0xf00f00ff )

        TEST_PARC_END

