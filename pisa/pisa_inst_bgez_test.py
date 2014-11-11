#=========================================================================
# pisa_bgez_test.py
#=========================================================================

import pytest
import random
import pisa_encoding

from pymtl import Bits
from PisaSim   import PisaSim

from pisa_inst_test_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addiu r3, r0, 0

    mfc0  r1, mngr2proc < 1

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    bgez  r1, label_a
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

    # Only the second bit should be set if branch was taken
    mtc0  r3, proc2mngr > 0b10

  """

#-------------------------------------------------------------------------
# gen_src_byp_taken_test
#-------------------------------------------------------------------------

def gen_src_byp_taken_test():
  return [
    gen_br1_src_byp_test( 5, "bgez", 1, True ),
    gen_br1_src_byp_test( 4, "bgez", 2, True ),
    gen_br1_src_byp_test( 3, "bgez", 3, True ),
    gen_br1_src_byp_test( 2, "bgez", 4, True ),
    gen_br1_src_byp_test( 1, "bgez", 5, True ),
    gen_br1_src_byp_test( 0, "bgez", 6, True ),
  ]

#-------------------------------------------------------------------------
# gen_src_byp_nottaken_test
#-------------------------------------------------------------------------

def gen_src_byp_nottaken_test():
  return [
    gen_br1_src_byp_test( 5, "bgez", -1, False ),
    gen_br1_src_byp_test( 4, "bgez", -2, False ),
    gen_br1_src_byp_test( 3, "bgez", -3, False ),
    gen_br1_src_byp_test( 2, "bgez", -4, False ),
    gen_br1_src_byp_test( 1, "bgez", -5, False ),
    gen_br1_src_byp_test( 0, "bgez", -6, False ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_br1_value_test( "bgez", -1, False ),
    gen_br1_value_test( "bgez",  0, True  ),
    gen_br1_value_test( "bgez",  1, True  ),

    gen_br1_value_test( "bgez", 0xfffffff7, False ),
    gen_br1_value_test( "bgez", 0x7fffffff, True  ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(25):
    src   = Bits( 32, random.randint(0,0xffffffff) )
    taken = ( src.int() >= 0 )
    asm_code.append( gen_br1_value_test( "bgez", src.uint(), taken ) )
  return asm_code

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test            ),
  asm_test( gen_src_byp_taken_test    ),
  asm_test( gen_src_byp_nottaken_test ),
  asm_test( gen_value_test            ),
  asm_test( gen_random_test           ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

