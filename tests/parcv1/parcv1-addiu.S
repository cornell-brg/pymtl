//=========================================================================
// parcv1-addiu.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_IMM_OP( addiu, 0x00000000, 0x0000, 0x00000000 )
        TEST_IMM_OP( addiu, 0x00000001, 0x0001, 0x00000002 )
        TEST_IMM_OP( addiu, 0x00000003, 0x0007, 0x0000000a )

        TEST_IMM_OP( addiu, 0x00000000, 0x8000, 0xffff8000 )
        TEST_IMM_OP( addiu, 0x80000000, 0x0000, 0x80000000 )
        TEST_IMM_OP( addiu, 0x80000000, 0x8000, 0x7fff8000 )

        TEST_IMM_OP( addiu, 0x00000000, 0x7fff, 0x00007fff )
        TEST_IMM_OP( addiu, 0x7fffffff, 0x0000, 0x7fffffff )
        TEST_IMM_OP( addiu, 0x7fffffff, 0x7fff, 0x80007ffe )

        TEST_IMM_OP( addiu, 0x80000000, 0x7fff, 0x80007fff )
        TEST_IMM_OP( addiu, 0x7fffffff, 0x8000, 0x7fff7fff )

        TEST_IMM_OP( addiu, 0x00000000, 0xffff, 0xffffffff )
        TEST_IMM_OP( addiu, 0xffffffff, 0x0001, 0x00000000 )
        TEST_IMM_OP( addiu, 0xffffffff, 0xffff, 0xfffffffe )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_IMM_SRC0_EQ_DEST( addiu, 13, 11, 24 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_IMM_DEST_BYP( 0, addiu, 13, 11, 24 )
        TEST_IMM_DEST_BYP( 1, addiu, 13, 10, 23 )
        TEST_IMM_DEST_BYP( 2, addiu, 13,  9, 22 )

        TEST_IMM_SRC0_BYP( 0, addiu, 13, 11, 24 )
        TEST_IMM_SRC0_BYP( 1, addiu, 13, 10, 23 )
        TEST_IMM_SRC0_BYP( 2, addiu, 13,  9, 22 )

        TEST_PARC_END

