#=========================================================================
# pisa_rem_test.py
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
    rem r3, r1, r2
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
    gen_rr_dest_byp_test( 5, "rem",  1, 6, 1 ),
    gen_rr_dest_byp_test( 4, "rem",  2, 6, 2 ),
    gen_rr_dest_byp_test( 3, "rem",  3, 6, 3 ),
    gen_rr_dest_byp_test( 2, "rem",  4, 6, 4 ),
    gen_rr_dest_byp_test( 1, "rem",  5, 6, 5 ),
    gen_rr_dest_byp_test( 0, "rem",  6, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_byp_test
#-------------------------------------------------------------------------

def gen_src0_byp_test():
  return [
    gen_rr_src0_byp_test( 5, "rem",  7, 6, 1 ),
    gen_rr_src0_byp_test( 4, "rem",  8, 6, 2 ),
    gen_rr_src0_byp_test( 3, "rem",  9, 6, 3 ),
    gen_rr_src0_byp_test( 2, "rem", 10, 6, 4 ),
    gen_rr_src0_byp_test( 2, "rem", 11, 6, 5 ),
    gen_rr_src0_byp_test( 0, "rem", 12, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_byp_test
#-------------------------------------------------------------------------

def gen_src1_byp_test():
  return [
    gen_rr_src1_byp_test( 5, "rem", 13, 6, 1 ),
    gen_rr_src1_byp_test( 4, "rem", 14, 6, 2 ),
    gen_rr_src1_byp_test( 3, "rem", 15, 6, 3 ),
    gen_rr_src1_byp_test( 2, "rem", 16, 6, 4 ),
    gen_rr_src1_byp_test( 1, "rem", 17, 6, 5 ),
    gen_rr_src1_byp_test( 0, "rem", 18, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_test
#-------------------------------------------------------------------------

def gen_srcs_byp_test():
  return [
    gen_rr_srcs_byp_test( 5, "rem", 19, 6, 1 ),
    gen_rr_srcs_byp_test( 4, "rem", 20, 6, 2 ),
    gen_rr_srcs_byp_test( 3, "rem", 21, 6, 3 ),
    gen_rr_srcs_byp_test( 2, "rem", 22, 6, 4 ),
    gen_rr_srcs_byp_test( 1, "rem", 23, 6, 5 ),
    gen_rr_srcs_byp_test( 0, "rem", 24, 6, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "rem", 25, 6, 1 ),
    gen_rr_src1_eq_dest_test( "rem", 26, 6, 2 ),
    gen_rr_src0_eq_src1_test( "rem", 2, 0 ),
    gen_rr_srcs_eq_dest_test( "rem", 3, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------
# Although the definition of the sign of the remainder depends on the
# application, the PARC ISA defines it to be equal to the sign of the
# dividend, and is tested as thus in this assembly test.

def gen_value_test():
  return [

    # Zero and one operands

    gen_rr_value_test( "rem",  0,  1, 0 ),
    gen_rr_value_test( "rem",  1,  1, 0 ),
    gen_rr_value_test( "rem",  0, -1, 0 ),
    gen_rr_value_test( "rem", -1, -1, 0 ),

    # Positive evenly-divisible operands

    gen_rr_value_test( "rem",       546,    42, 0 ),
    gen_rr_value_test( "rem",     63724,   716, 0 ),
    gen_rr_value_test( "rem", 167882820, 20154, 0 ),

    # Positive not evenly-divisible operands

    gen_rr_value_test( "rem",        50,   546,    50 ),
    gen_rr_value_test( "rem",       546,    50,    46 ),
    gen_rr_value_test( "rem",     63724,   793,   284 ),
    gen_rr_value_test( "rem", 167882820, 20150, 13170 ),

    # Mixed tests

    gen_rr_value_test( "rem", 0x0a01b044, 0xffffb146, 0x00000000 ),
    gen_rr_value_test( "rem", 0x0a01b044, 0xffffb14a, 0x00003372 ),
    gen_rr_value_test( "rem", 0xdeadbeef, 0x0000beef, 0xffffda72 ),
    gen_rr_value_test( "rem", 0xf5fe4fbc, 0x00004eb6, 0xffffcc8e ),
    gen_rr_value_test( "rem", 0xf5fe4fbc, 0xffffb14a, 0xffffcc8e ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):

    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )

    a = src0.int()
    b = src1.int()

    A = -a if (a < 0) else a
    B = -b if (b < 0) else b
    c = -(A % B) if (a < 0) else (A % B)

    dest = Bits( 32, c )

    asm_code.append( gen_rr_value_test( "rem", src0.uint(), src1.uint(), dest.uint() ) )
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
