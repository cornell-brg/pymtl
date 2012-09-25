//=========================================================================
// parcv2-or.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Logical tests
        //-----------------------------------------------------------------

        TEST_RR_OP( or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_OP( or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_OP( or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )
        TEST_RR_OP( or, 0xf00ff00f, 0xf0f0f0f0, 0xf0fff0ff )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRC1_EQ_DEST( or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRCS_EQ_DEST( or, 0xff00ff00, 0xff00ff00 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_DEST_BYP( 1, or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_DEST_BYP( 2, or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )

        TEST_RR_SRC01_BYP( 0, 0, or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRC01_BYP( 0, 1, or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_SRC01_BYP( 0, 2, or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )
        TEST_RR_SRC01_BYP( 1, 0, or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRC01_BYP( 1, 1, or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_SRC01_BYP( 2, 0, or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )

        TEST_RR_SRC10_BYP( 0, 0, or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRC10_BYP( 0, 1, or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_SRC10_BYP( 0, 2, or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )
        TEST_RR_SRC10_BYP( 1, 0, or, 0xff00ff00, 0x0f0f0f0f, 0xff0fff0f )
        TEST_RR_SRC10_BYP( 1, 1, or, 0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 )
        TEST_RR_SRC10_BYP( 2, 0, or, 0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff )

        TEST_PARC_END

