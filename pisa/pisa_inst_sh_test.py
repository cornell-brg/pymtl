#=========================================================================
# pisa_sh_test.py
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
    mfc0 r1, mngr2proc < 0x00002000
    mfc0 r2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sh   r2, 0(r1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   r3, 0(r1)
    mtc0 r3, proc2mngr > 0x0102beef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_byp_test
#-------------------------------------------------------------------------

def gen_dest_byp_test():
  return [

    gen_st_dest_byp_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_dest_byp_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_dest_byp_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_dest_byp_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_dest_byp_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_dest_byp_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_byp_test
#-------------------------------------------------------------------------

def gen_base_byp_test():
  return [

    gen_st_base_byp_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_base_byp_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_base_byp_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_base_byp_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_base_byp_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_base_byp_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]


#-------------------------------------------------------------------------
# gen_src_byp_test
#-------------------------------------------------------------------------

def gen_src_byp_test():
  return [

    gen_st_src_byp_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_src_byp_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_src_byp_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_src_byp_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_src_byp_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_src_byp_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_byp_test
#-------------------------------------------------------------------------

def gen_srcs_byp_test():
  return [

    gen_st_srcs_byp_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_srcs_byp_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_srcs_byp_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_srcs_byp_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_srcs_byp_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_srcs_byp_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_st_src_eq_base_test( "sh", 0x00002000, 0x01022000 ),
    gen_word_data([ 0x01020304 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_st_value_test( "sh", 0x30313233,   0, 0x00002000, 0xffff3233 ),
    gen_st_value_test( "sh", 0x34353637,   2, 0x00002000, 0x36373233 ),
    gen_st_value_test( "sh", 0x38393a3b,   4, 0x00002000, 0xffff3a3b ),
    gen_st_value_test( "sh", 0x3c3d3e3f,   6, 0x00002000, 0x3e3f3a3b ),
    gen_st_value_test( "sh", 0x40414243,   8, 0x00002000, 0xffff4243 ),
    gen_st_value_test( "sh", 0x44454647,  10, 0x00002000, 0x46474243 ),

    # Test negative offsets

    gen_st_value_test( "sh", 0x48494a4b, -10, 0x00002018, 0x4a4bffff ),
    gen_st_value_test( "sh", 0x4c4d4e4f,  -8, 0x00002018, 0xffff4e4f ),
    gen_st_value_test( "sh", 0x50515253,  -6, 0x00002018, 0x52534e4f ),
    gen_st_value_test( "sh", 0x54555657,  -4, 0x00002018, 0xffff5657 ),
    gen_st_value_test( "sh", 0x58595a5b,  -2, 0x00002018, 0x5a5b5657 ),
    gen_st_value_test( "sh", 0x5c5d5e5f,   0, 0x00002018, 0xffff5e5f ),

    # Test positive offset with unaligned base

    gen_st_value_test( "sh", 0x60616263,   1, 0x0000201f, 0xffff6263 ),
    gen_st_value_test( "sh", 0x64656667,   5, 0x0000201f, 0xffff6667 ),
    gen_st_value_test( "sh", 0x68696a6b,   9, 0x0000201f, 0xffff6a6b ),
    gen_st_value_test( "sh", 0x6c6d6e6f,  13, 0x0000201f, 0xffff6e6f ),
    gen_st_value_test( "sh", 0x70717273,  17, 0x0000201f, 0xffff7273 ),
    gen_st_value_test( "sh", 0x74757677,  21, 0x0000201f, 0xffff7677 ),

    # Test negative offset with unaligned base

    gen_st_value_test( "sh", 0x78797a7b, -21, 0x00002039, 0xffff7a7b ),
    gen_st_value_test( "sh", 0x7c7d7e7f, -17, 0x00002039, 0xffff7e7f ),
    gen_st_value_test( "sh", 0x80818283, -13, 0x00002039, 0xffff8283 ),
    gen_st_value_test( "sh", 0x84858687,  -9, 0x00002039, 0xffff8687 ),
    gen_st_value_test( "sh", 0x88898a8b,  -5, 0x00002039, 0xffff8a8b ),
    gen_st_value_test( "sh", 0x8c8d8e8f,  -1, 0x00002039, 0xffff8e8f ),

    gen_word_data([0xffffffff]*16)

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in xrange(128):
    data.append( random.randint(0,0xffff) )

  # Generate random accesses to this data

  asm_code = []
  for i in xrange(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = Bits( 32, 0x2000 + (2*b) )
    offset = Bits( 16, (2*(a - b)) )
    result = Bits( 32, data[a] )

    asm_code.append( gen_st_random_test( "sh", "lhu", result.uint(), offset.int(), base.uint() ) )

  # Generate some random data to initialize memory

  initial_data = []
  for i in xrange(128):
    initial_data.append( random.randint(0,0xffff) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_hword_data( initial_data ) )
  return asm_code

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test     ),
  asm_test( gen_dest_byp_test  ),
  asm_test( gen_base_byp_test  ),
  asm_test( gen_src_byp_test   ),
  asm_test( gen_srcs_byp_test  ),
  asm_test( gen_srcs_dest_test ),
  asm_test( gen_value_test     ),
  asm_test( gen_random_test    ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()
