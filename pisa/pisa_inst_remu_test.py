#=========================================================================
# pisa_remu_test.py
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
    mfc0 r1, mngr2proc < 21
    mfc0 r2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    remu r3, r1, r2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtc0 r3, proc2mngr > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# gen_dest_byp_test
#-------------------------------------------------------------------------

def gen_dest_byp_test():
  return [
    gen_rr_dest_byp_test( 5, "remu",  1, 6, 1 ),
    gen_rr_dest_byp_test( 4, "remu",  2, 6, 2 ),
    gen_rr_dest_byp_test( 3, "remu",  3, 6, 3 ),
    gen_rr_dest_byp_test( 2, "remu",  4, 6, 4 ),
    gen_rr_dest_byp_test( 1, "remu",  5, 6, 5 ),
    gen_rr_dest_byp_test( 0, "remu",  6, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_byp_test
#-------------------------------------------------------------------------

def gen_src0_byp_test():
  return [
    gen_rr_src0_byp_test( 5, "remu",  7, 6, 1 ),
    gen_rr_src0_byp_test( 4, "remu",  8, 6, 2 ),
    gen_rr_src0_byp_test( 3, "remu",  9, 6, 3 ),
    gen_rr_src0_byp_test( 2, "remu", 10, 6, 4 ),
    gen_rr_src0_byp_test( 2, "remu", 11, 6, 5 ),
    gen_rr_src0_byp_test( 0, "remu", 12, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_byp_test
#-------------------------------------------------------------------------

def gen_src1_byp_test():
  return [
    gen_rr_src1_byp_test( 5, "remu", 13, 6, 1 ),
    gen_rr_src1_byp_test( 4, "remu", 14, 6, 2 ),
    gen_rr_src1_byp_test( 3, "remu", 15, 6, 3 ),
    gen_rr_src1_byp_test( 2, "remu", 16, 6, 4 ),
    gen_rr_src1_byp_test( 1, "remu", 17, 6, 5 ),
    gen_rr_src1_byp_test( 0, "remu", 18, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_test
#-------------------------------------------------------------------------

def gen_srcs_byp_test():
  return [
    gen_rr_srcs_byp_test( 5, "remu", 19, 6, 1 ),
    gen_rr_srcs_byp_test( 4, "remu", 20, 6, 2 ),
    gen_rr_srcs_byp_test( 3, "remu", 21, 6, 3 ),
    gen_rr_srcs_byp_test( 2, "remu", 22, 6, 4 ),
    gen_rr_srcs_byp_test( 1, "remu", 23, 6, 5 ),
    gen_rr_srcs_byp_test( 0, "remu", 24, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "remu", 25, 6, 1 ),
    gen_rr_src1_eq_dest_test( "remu", 26, 6, 2 ),
    gen_rr_src0_eq_src1_test( "remu", 2, 0 ),
    gen_rr_srcs_eq_dest_test( "remu", 3, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------
# Still not quite sure what is the "right" thing to do for negative
# operands?

def gen_value_test():
  return [

    # Zero and one operands

    gen_rr_value_test( "remu",  0,  1, 0 ),
    gen_rr_value_test( "remu",  1,  1, 0 ),

    # Positive evenly-divisible operands

    gen_rr_value_test( "remu",       546,    42, 0 ),
    gen_rr_value_test( "remu",     63724,   716, 0 ),
    gen_rr_value_test( "remu", 167882820, 20154, 0 ),

    # Positive not evenly-divisible operands

    gen_rr_value_test( "remu",        50,   546,    50 ),
    gen_rr_value_test( "remu",       546,    50,    46 ),
    gen_rr_value_test( "remu",     63724,   793,   284 ),
    gen_rr_value_test( "remu", 167882820, 20150, 13170 ),

    # Test that operands are treated as unsigned

    gen_rr_value_test( "remu", 0x00000000, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "remu", 0xffffffff, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "remu", 0x0a01b044, 0xffffb14a, 0x0a01b044 ),
    gen_rr_value_test( "remu", 0xdeadbeef, 0x0000beef, 0x0000227f ),
    gen_rr_value_test( "remu", 0xf5fe4fbc, 0x00004eb6, 0x000006f0 ),
    gen_rr_value_test( "remu", 0xf5fe4fbc, 0xffffb14a, 0xf5fe4fbc ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    dest = Bits( 32, src0 % src1 )
    asm_code.append( gen_rr_value_test( "remu", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test     ),
  asm_test( gen_dest_byp_test  ),
  asm_test( gen_src0_byp_test  ),
  asm_test( gen_src1_byp_test  ),
  asm_test( gen_srcs_byp_test  ),
  asm_test( gen_srcs_dest_test ),
  asm_test( gen_value_test     ),
  asm_test( gen_random_test    ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()
