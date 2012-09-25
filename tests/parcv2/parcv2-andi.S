//=========================================================================
// parcv2-andi.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Logical tests
        //-----------------------------------------------------------------

        TEST_IMM_OP( andi, 0xff00ff00, 0x0f0f, 0x00000f00 )
        TEST_IMM_OP( andi, 0x0ff00ff0, 0xf0f0, 0x000000f0 )
        TEST_IMM_OP( andi, 0x00ff00ff, 0x0f0f, 0x0000000f )
        TEST_IMM_OP( andi, 0xf00ff00f, 0xf0f0, 0x0000f000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_IMM_SRC0_EQ_DEST( andi, 0xff00ff00, 0xf0f0, 0x0000f000 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_IMM_DEST_BYP( 0, andi, 0x0ff00ff0, 0x0f0f, 0x00000f00 )
        TEST_IMM_DEST_BYP( 1, andi, 0x00ff00ff, 0xf0f0, 0x000000f0 )
        TEST_IMM_DEST_BYP( 2, andi, 0xf00ff00f, 0x0f0f, 0x0000000f )

        TEST_IMM_SRC0_BYP( 0, andi, 0x0ff00ff0, 0x0f0f, 0x00000f00 )
        TEST_IMM_SRC0_BYP( 1, andi, 0x00ff00ff, 0xf0f0, 0x000000f0 )
        TEST_IMM_SRC0_BYP( 2, andi, 0xf00ff00f, 0x0f0f, 0x0000000f )

        TEST_PARC_END

