//=========================================================================
// parcv2-subu.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( subu, 0x00000000, 0x00000000, 0x00000000 )
        TEST_RR_OP( subu, 0x00000001, 0x00000001, 0x00000000 )
        TEST_RR_OP( subu, 0x00000003, 0x00000007, 0xfffffffc )

        TEST_RR_OP( subu, 0x00000000, 0xffff8000, 0x00008000 )
        TEST_RR_OP( subu, 0x80000000, 0x00000000, 0x80000000 )
        TEST_RR_OP( subu, 0x80000000, 0xffff8000, 0x80008000 )

        TEST_RR_OP( subu, 0x00000000, 0x00007fff, 0xffff8001 )
        TEST_RR_OP( subu, 0x7fffffff, 0x00000000, 0x7fffffff )
        TEST_RR_OP( subu, 0x7fffffff, 0x00007fff, 0x7fff8000 )

        TEST_RR_OP( subu, 0x80000000, 0x00007fff, 0x7fff8001 )
        TEST_RR_OP( subu, 0x7fffffff, 0xffff8000, 0x80007fff )

        TEST_RR_OP( subu, 0x00000000, 0xffffffff, 0x00000001 )
        TEST_RR_OP( subu, 0xffffffff, 0x00000001, 0xfffffffe )
        TEST_RR_OP( subu, 0xffffffff, 0xffffffff, 0x00000000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( subu, 13, 11, 2 )
        TEST_RR_SRC1_EQ_DEST( subu, 14, 11, 3 )
        TEST_RR_SRCS_EQ_DEST( subu, 13, 0 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, subu, 13, 11, 2 )
        TEST_RR_DEST_BYP( 1, subu, 14, 11, 3 )
        TEST_RR_DEST_BYP( 2, subu, 15, 11, 4 )

        TEST_RR_SRC01_BYP( 0, 0, subu, 13, 11, 2 )
        TEST_RR_SRC01_BYP( 0, 1, subu, 14, 11, 3 )
        TEST_RR_SRC01_BYP( 0, 2, subu, 15, 11, 4 )
        TEST_RR_SRC01_BYP( 1, 0, subu, 13, 11, 2 )
        TEST_RR_SRC01_BYP( 1, 1, subu, 14, 11, 3 )
        TEST_RR_SRC01_BYP( 2, 0, subu, 15, 11, 4 )

        TEST_RR_SRC10_BYP( 0, 0, subu, 13, 11, 2 )
        TEST_RR_SRC10_BYP( 0, 1, subu, 14, 11, 3 )
        TEST_RR_SRC10_BYP( 0, 2, subu, 15, 11, 4 )
        TEST_RR_SRC10_BYP( 1, 0, subu, 13, 11, 2 )
        TEST_RR_SRC10_BYP( 1, 1, subu, 14, 11, 3 )
        TEST_RR_SRC10_BYP( 2, 0, subu, 15, 11, 4 )

        TEST_PARC_END

