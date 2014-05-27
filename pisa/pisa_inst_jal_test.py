#=========================================================================
# pisa_jal_test.py
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

    jal label_a
    ori r3, r3, 0b01

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    ori r3, r3, 0b10

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b10

  """

#-------------------------------------------------------------------------
# gen_link_byp_test
#-------------------------------------------------------------------------

def gen_link_byp_test():
  return [
    gen_jal_link_byp_test( 5 ),
    gen_jal_link_byp_test( 4 ),
    gen_jal_link_byp_test( 3 ),
    gen_jal_link_byp_test( 2 ),
    gen_jal_link_byp_test( 1 ),
    gen_jal_link_byp_test( 0 ),
  ]

#-------------------------------------------------------------------------
# gen_jump_test
#-------------------------------------------------------------------------
# Currently we have to hard code the expected values for the link
# address. Maybe our assembler should support the la pseudo instruction?
# Maybe our assembler should support the la pseudo instruction? Not sure
# if that would help since we need to put the expected value in the
# proc2mgnr queue.

def gen_jump_test():
  return """
                                                  # PC
    # Use r3 to track the control flow pattern    #
    addiu r3, r0, 0                               # 0x00000400
                                                  #
    jal   label_a           # j -.                # 0x00000404
    ori   r3, r3, 0b000001  #    |                # 0x00000408
                            #    |                #
  label_b:                  # <--+-.              #
    ori   r3, r3, 0b000010  #    | |              # 0x0000040c
    addiu r5, r31, 0        #    | |              # 0x00000410
    jal   label_c           # j -+-+-.            # 0x00000414
    ori   r3, r3, 0b000100  #    | | |            # 0x00000418
                            #    | | |            #
  label_a:                  # <--' | |            #
    ori   r3, r3, 0b001000  #      | |            # 0x0000041c
    addiu r4, r31, 0        #      | |            # 0x00000420
    jal   label_b           # j ---' |            # 0x00000424
    ori   r3, r3, 0b010000  #        |            # 0x00000428
                            #        |            #
  label_c:                  # <------'            #
    ori   r3, r3, 0b100000  #                     # 0x0000042c
    addiu r6, r31, 0        #                     # 0x00000430

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b101010

    # Check the link addresses
    mtc0  r4, proc2mngr > 0x00000408
    mtc0  r5, proc2mngr > 0x00000428
    mtc0  r6, proc2mngr > 0x00000418

  """

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test    ),
  asm_test( gen_link_byp_test ),
  asm_test( gen_jump_test     ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

