#=========================================================================
# pisa_divu_test.py
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
    mfc0 r1, mngr2proc < 20
    mfc0 r2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    divu r3, r1, r2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtc0 r3, proc2mngr > 5
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
    gen_rr_dest_byp_test( 5, "divu",  2, 2, 1 ),
    gen_rr_dest_byp_test( 4, "divu",  4, 2, 2 ),
    gen_rr_dest_byp_test( 3, "divu",  6, 2, 3 ),
    gen_rr_dest_byp_test( 2, "divu",  8, 2, 4 ),
    gen_rr_dest_byp_test( 1, "divu", 10, 2, 5 ),
    gen_rr_dest_byp_test( 0, "divu", 12, 2, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_byp_test
#-------------------------------------------------------------------------

def gen_src0_byp_test():
  return [
    gen_rr_src0_byp_test( 5, "divu", 14, 2,  7 ),
    gen_rr_src0_byp_test( 4, "divu", 16, 2,  8 ),
    gen_rr_src0_byp_test( 3, "divu", 18, 2,  9 ),
    gen_rr_src0_byp_test( 2, "divu", 20, 2, 10 ),
    gen_rr_src0_byp_test( 2, "divu", 22, 2, 11 ),
    gen_rr_src0_byp_test( 0, "divu", 24, 2, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_byp_test
#-------------------------------------------------------------------------

def gen_src1_byp_test():
  return [
    gen_rr_src1_byp_test( 5, "divu", 26, 2, 13 ),
    gen_rr_src1_byp_test( 4, "divu", 28, 2, 14 ),
    gen_rr_src1_byp_test( 3, "divu", 30, 2, 15 ),
    gen_rr_src1_byp_test( 2, "divu", 32, 2, 16 ),
    gen_rr_src1_byp_test( 1, "divu", 34, 2, 17 ),
    gen_rr_src1_byp_test( 0, "divu", 36, 2, 18 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_test
#-------------------------------------------------------------------------

def gen_srcs_byp_test():
  return [
    gen_rr_srcs_byp_test( 5, "divu", 38, 2, 19 ),
    gen_rr_srcs_byp_test( 4, "divu", 40, 2, 20 ),
    gen_rr_srcs_byp_test( 3, "divu", 42, 2, 21 ),
    gen_rr_srcs_byp_test( 2, "divu", 44, 2, 22 ),
    gen_rr_srcs_byp_test( 1, "divu", 46, 2, 23 ),
    gen_rr_srcs_byp_test( 0, "divu", 48, 2, 24 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "divu", 50, 25, 2 ),
    gen_rr_src1_eq_dest_test( "divu", 52, 26, 2 ),
    gen_rr_src0_eq_src1_test( "divu", 2, 1 ),
    gen_rr_srcs_eq_dest_test( "divu", 3, 1 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Zero and one operands

    gen_rr_value_test( "divu",  0,  1, 0 ),
    gen_rr_value_test( "divu",  1,  1, 1 ),

    # Positive evenly-divisible operands

    gen_rr_value_test( "divu",       546,    42,   13 ),
    gen_rr_value_test( "divu",     63724,   716,   89 ),
    gen_rr_value_test( "divu", 167882820, 20154, 8330 ),

    # Positive not evenly-divisible operands

    gen_rr_value_test( "divu",        50,   546,    0 ),
    gen_rr_value_test( "divu",       546,    50,   10 ),
    gen_rr_value_test( "divu",     63724,   793,   80 ),
    gen_rr_value_test( "divu", 167882820, 20150, 8331 ),

    # Test that operands are treated as unsigned

    gen_rr_value_test( "divu", 0x00000000, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "divu", 0xffffffff, 0xffffffff, 0x00000001 ),
    gen_rr_value_test( "divu", 0x0a01b044, 0xffffb14a, 0x00000000 ),
    gen_rr_value_test( "divu", 0xdeadbeef, 0x0000beef, 0x00012a90 ),
    gen_rr_value_test( "divu", 0xf5fe4fbc, 0x00004eb6, 0x00032012 ),
    gen_rr_value_test( "divu", 0xf5fe4fbc, 0xffffb14a, 0x00000000 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    dest = Bits( 32, src0 / src1 )
    asm_code.append( gen_rr_value_test( "divu", src0.uint(), src1.uint(), dest.uint() ) )
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
