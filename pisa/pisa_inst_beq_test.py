#=========================================================================
# pisa_beq_test.py
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

    mfc0  r1, mngr2proc < 2
    mfc0  r2, mngr2proc < 2

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    beq   r1, r2, label_a
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
# gen_src0_byp_taken_test
#-------------------------------------------------------------------------

def gen_src0_byp_taken_test():
  return [
    gen_br2_src0_byp_test( 5, "beq", 1, 1, True ),
    gen_br2_src0_byp_test( 4, "beq", 2, 2, True ),
    gen_br2_src0_byp_test( 3, "beq", 3, 3, True ),
    gen_br2_src0_byp_test( 2, "beq", 4, 4, True ),
    gen_br2_src0_byp_test( 1, "beq", 5, 5, True ),
    gen_br2_src0_byp_test( 0, "beq", 6, 6, True ),
  ]

#-------------------------------------------------------------------------
# gen_src0_byp_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_byp_nottaken_test():
  return [
    gen_br2_src0_byp_test( 5, "beq", 1, 2, False ),
    gen_br2_src0_byp_test( 4, "beq", 2, 3, False ),
    gen_br2_src0_byp_test( 3, "beq", 3, 4, False ),
    gen_br2_src0_byp_test( 2, "beq", 4, 5, False ),
    gen_br2_src0_byp_test( 1, "beq", 5, 6, False ),
    gen_br2_src0_byp_test( 0, "beq", 6, 7, False ),
  ]

#-------------------------------------------------------------------------
# gen_src1_byp_taken_test
#-------------------------------------------------------------------------

def gen_src1_byp_taken_test():
  return [
    gen_br2_src1_byp_test( 5, "beq", 1, 1, True ),
    gen_br2_src1_byp_test( 4, "beq", 2, 2, True ),
    gen_br2_src1_byp_test( 3, "beq", 3, 3, True ),
    gen_br2_src1_byp_test( 2, "beq", 4, 4, True ),
    gen_br2_src1_byp_test( 1, "beq", 5, 5, True ),
    gen_br2_src1_byp_test( 0, "beq", 6, 6, True ),
  ]

#-------------------------------------------------------------------------
# gen_src1_byp_nottaken_test
#-------------------------------------------------------------------------

def gen_src1_byp_nottaken_test():
  return [
    gen_br2_src1_byp_test( 5, "beq", 1, 2, False ),
    gen_br2_src1_byp_test( 4, "beq", 2, 3, False ),
    gen_br2_src1_byp_test( 3, "beq", 3, 4, False ),
    gen_br2_src1_byp_test( 2, "beq", 4, 5, False ),
    gen_br2_src1_byp_test( 1, "beq", 5, 6, False ),
    gen_br2_src1_byp_test( 0, "beq", 6, 7, False ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_taken_test
#-------------------------------------------------------------------------

def gen_srcs_byp_taken_test():
  return [
    gen_br2_srcs_byp_test( 5, "beq", 1, 1, True ),
    gen_br2_srcs_byp_test( 4, "beq", 2, 2, True ),
    gen_br2_srcs_byp_test( 3, "beq", 3, 3, True ),
    gen_br2_srcs_byp_test( 2, "beq", 4, 4, True ),
    gen_br2_srcs_byp_test( 1, "beq", 5, 5, True ),
    gen_br2_srcs_byp_test( 0, "beq", 6, 6, True ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_nottaken_test
#-------------------------------------------------------------------------

def gen_srcs_byp_nottaken_test():
  return [
    gen_br2_srcs_byp_test( 5, "beq", 1, 2, False ),
    gen_br2_srcs_byp_test( 4, "beq", 2, 3, False ),
    gen_br2_srcs_byp_test( 3, "beq", 3, 4, False ),
    gen_br2_srcs_byp_test( 2, "beq", 4, 5, False ),
    gen_br2_srcs_byp_test( 1, "beq", 5, 6, False ),
    gen_br2_srcs_byp_test( 0, "beq", 6, 7, False ),
  ]

#-------------------------------------------------------------------------
# gen_src0_eq_src1_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_eq_src1_test():
  return [
    gen_br2_src0_eq_src1_test( "beq", 1, True ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_br2_value_test( "beq", -1, -1, True  ),
    gen_br2_value_test( "beq", -1,  0, False ),
    gen_br2_value_test( "beq", -1,  1, False ),

    gen_br2_value_test( "beq",  0, -1, False ),
    gen_br2_value_test( "beq",  0,  0, True  ),
    gen_br2_value_test( "beq",  0,  1, False ),

    gen_br2_value_test( "beq",  1, -1, False ),
    gen_br2_value_test( "beq",  1,  0, False ),
    gen_br2_value_test( "beq",  1,  1, True  ),

    gen_br2_value_test( "beq", 0xfffffff7, 0xfffffff7, True  ),
    gen_br2_value_test( "beq", 0x7fffffff, 0x7fffffff, True  ),
    gen_br2_value_test( "beq", 0xfffffff7, 0x7fffffff, False ),
    gen_br2_value_test( "beq", 0x7fffffff, 0xfffffff7, False ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(25):
    src0  = Bits( 32, random.randint(0,0xffffffff) )
    src1  = Bits( 32, random.randint(0,0xffffffff) )
    taken = ( src0 == src1 )
    asm_code.append( gen_br2_value_test( "beq", src0.uint(), src1.uint(), taken ) )
  return asm_code

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test             ),
  asm_test( gen_src0_byp_taken_test    ),
  asm_test( gen_src0_byp_nottaken_test ),
  asm_test( gen_src1_byp_taken_test    ),
  asm_test( gen_src1_byp_nottaken_test ),
  asm_test( gen_srcs_byp_taken_test    ),
  asm_test( gen_srcs_byp_nottaken_test ),
  asm_test( gen_src0_eq_src1_test      ),
  asm_test( gen_value_test             ),
  asm_test( gen_random_test            ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

