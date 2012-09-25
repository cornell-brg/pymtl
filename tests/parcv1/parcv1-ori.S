//=========================================================================
// parcv1-ori.S
//=========================================================================


#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-------------------------------------------------------------
        // Logical tests
        //-------------------------------------------------------------

        TEST_IMM_OP( ori, 0xff00ff00, 0x0f0f, 0xff00ff0f )
        TEST_IMM_OP( ori, 0x0ff00ff0, 0xf0f0, 0x0ff0fff0 )
        TEST_IMM_OP( ori, 0x00ff00ff, 0x0f0f, 0x00ff0fff )
        TEST_IMM_OP( ori, 0xf00ff00f, 0xf0f0, 0xf00ff0ff )

        //-------------------------------------------------------------
        // Source/Destination tests
        //-------------------------------------------------------------

        TEST_IMM_SRC0_EQ_DEST( ori, 0xff00ff00, 0xf0f0, 0xff00fff0 )

        //-------------------------------------------------------------
        // Bypassing tests
        //-------------------------------------------------------------

        TEST_IMM_DEST_BYP( 0, ori, 0x0ff00ff0, 0xf0f0, 0x0ff0fff0 );
        TEST_IMM_DEST_BYP( 1, ori, 0x00ff00ff, 0x0f0f, 0x00ff0fff );
        TEST_IMM_DEST_BYP( 2, ori, 0xf00ff00f, 0xf0f0, 0xf00ff0ff );

        TEST_IMM_SRC0_BYP( 0, ori, 0x0ff00ff0, 0xf0f0, 0x0ff0fff0 );
        TEST_IMM_SRC0_BYP( 1, ori, 0x00ff00ff, 0x0f0f, 0x00ff0fff );
        TEST_IMM_SRC0_BYP( 2, ori, 0xf00ff00f, 0xf0f0, 0xf00ff0ff );

        TEST_PARC_END

