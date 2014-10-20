#=========================================================================
# pisa_jalr_test.py
#=========================================================================

import pytest
import random
import pisa_encoding

from new_pymtl import Bits
from PisaSim   import PisaSim

from pisa_inst_test_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addiu r3, r0, 0

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    lui   r1,     %hi[label_a]
    ori   r1, r0, %lo[label_a]

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    jalr  r2, r1
    ori   r3, r3, 0b01

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    ori   r3, r3, 0b10

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b10

  """

#-------------------------------------------------------------------------
# gen_link_byp_test
#-------------------------------------------------------------------------

def gen_link_byp_test():
  return [
    gen_jalr_link_byp_test( 5, reset_test_count=True  ),
    gen_jalr_link_byp_test( 4, reset_test_count=False ),
    gen_jalr_link_byp_test( 3, reset_test_count=False ),
    gen_jalr_link_byp_test( 2, reset_test_count=False ),
    gen_jalr_link_byp_test( 1, reset_test_count=False ),
    gen_jalr_link_byp_test( 0, reset_test_count=False ),
  ]

#-------------------------------------------------------------------------
# gen_src_byp_test
#-------------------------------------------------------------------------

def gen_src_byp_test():
  return [
    gen_jalr_src_byp_test( 5 ),
    gen_jalr_src_byp_test( 4 ),
    gen_jalr_src_byp_test( 3 ),
    gen_jalr_src_byp_test( 2 ),
    gen_jalr_src_byp_test( 1 ),
    gen_jalr_src_byp_test( 0 ),
  ]

#-------------------------------------------------------------------------
# gen_jump_test
#-------------------------------------------------------------------------

def gen_jump_test():
  return """
                                                  # PC
    # Use r3 to track the control flow pattern    #
    addiu r3, r0, 0                               # 0x00000400
                                                  #
    lui   r1,     %hi[label_a]                    # 0x00000404
    ori   r1, r0, %lo[label_a]                    # 0x00000408
    jalr  r30, r1               # j -.            # 0x0000040c
                                #    |            #
    ori   r3, r3, 0b000001      #    |            # 0x00000410
                                #    |            #
  label_b:                      # <--+-.          #
    ori   r3, r3, 0b000010      #    | |          # 0x00000414
    addiu r5, r29, 0            #    | |          # 0x00000418
                                #    | |          #
    lui   r1,     %hi[label_c]  #    | |          # 0x0000041c
    ori   r1, r0, %lo[label_c]  #    | |          # 0x00000420
    jalr  r28, r1               # j -+-+-.        # 0x00000424
                                #    | | |        #
    ori   r3, r3, 0b000100      #    | | |        # 0x00000428
                                #    | | |        #
  label_a:                      # <--' | |        #
    ori   r3, r3, 0b001000      #      | |        # 0x0000042c
    addiu r4, r30, 0            #      | |        # 0x00000430
                                #      | |        #
    lui   r1,     %hi[label_b]  #      | |        # 0x00000434
    ori   r1, r0, %lo[label_b]  #      | |        # 0x00000438
    jalr  r29, r1               # j ---' |        # 0x0000043c
                                #        |        #
    ori   r3, r3, 0b010000      #        |        # 0x00000440
                                #        |        #
  label_c:                      # <------'        #
    ori   r3, r3, 0b100000      #                 # 0x00000444
    addiu r6, r28, 0            #                 # 0x00000448

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b101010

    # Check the link addresses
    mtc0  r4, proc2mngr > 0x00000410
    mtc0  r5, proc2mngr > 0x00000440
    mtc0  r6, proc2mngr > 0x00000428

  """

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test    ),
  asm_test( gen_link_byp_test ),
  asm_test( gen_src_byp_test  ),
  asm_test( gen_jump_test     ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

