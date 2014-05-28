#=========================================================================
# pisa_j_test.py
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

    j   label_a
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
# gen_jump_test
#-------------------------------------------------------------------------

def gen_jump_test():
  return """

    # Use r3 to track the control flow pattern
    addiu r3, r0, 0

    j   label_a           # j -.
    ori r3, r3, 0b000001  #    |
                          #    |
  label_b:                # <--+-.
    ori r3, r3, 0b000010  #    | |
    j   label_c           # j -+-+-.
    ori r3, r3, 0b000100  #    | | |
                          #    | | |
  label_a:                # <--' | |
    ori r3, r3, 0b001000  #      | |
    j   label_b           # j ---' |
    ori r3, r3, 0b010000  #        |
                          #        |
  label_c:                # <------'
    ori r3, r3, 0b100000  #

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b101010

  """

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test ),
  asm_test( gen_jump_test  ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

