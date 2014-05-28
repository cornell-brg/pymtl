#=========================================================================
# pisa_sb_test.py
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
    sb   r2, 0(r1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   r3, 0(r1)
    mtc0 r3, proc2mngr > 0x010203ef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_byp_test
#-------------------------------------------------------------------------

def gen_dest_byp_test():
  return [

    gen_st_dest_byp_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_dest_byp_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_dest_byp_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_dest_byp_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_dest_byp_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_dest_byp_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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

    gen_st_base_byp_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_base_byp_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_base_byp_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_base_byp_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_base_byp_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_base_byp_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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

    gen_st_src_byp_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_src_byp_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_src_byp_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_src_byp_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_src_byp_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_src_byp_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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

    gen_st_srcs_byp_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_srcs_byp_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_srcs_byp_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_srcs_byp_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_srcs_byp_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_srcs_byp_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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
    gen_st_src_eq_base_test( "sb", 0x00002004, 0x05060704 ),
    gen_word_data([ 0x01020304, 0x05060708 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_st_value_test( "sb", 0x30313233,   0, 0x00002000, 0xffffff33 ),
    gen_st_value_test( "sb", 0x34353637,   1, 0x00002000, 0xffff3733 ),
    gen_st_value_test( "sb", 0x38393a3b,   2, 0x00002000, 0xff3b3733 ),
    gen_st_value_test( "sb", 0x3c3d3e3f,   3, 0x00002000, 0x3f3b3733 ),
    gen_st_value_test( "sb", 0x40414243,   4, 0x00002000, 0xffffff43 ),
    gen_st_value_test( "sb", 0x44454647,   5, 0x00002000, 0xffff4743 ),

    # Test negative offsets

    gen_st_value_test( "sb", 0x48494a4b,  -5, 0x00002018, 0x4bffffff ),
    gen_st_value_test( "sb", 0x4c4d4e4f,  -4, 0x00002018, 0xffffff4f ),
    gen_st_value_test( "sb", 0x50515253,  -3, 0x00002018, 0xffff534f ),
    gen_st_value_test( "sb", 0x54555657,  -2, 0x00002018, 0xff57534f ),
    gen_st_value_test( "sb", 0x58595a5b,  -1, 0x00002018, 0x5b57534f ),
    gen_st_value_test( "sb", 0x5c5d5e5f,   0, 0x00002018, 0xffffff5f ),

    # Test positive offset with unaligned base

    gen_st_value_test( "sb", 0x60616263,   1, 0x0000201f, 0xffffff63 ),
    gen_st_value_test( "sb", 0x64656667,   5, 0x0000201f, 0xffffff67 ),
    gen_st_value_test( "sb", 0x68696a6b,   9, 0x0000201f, 0xffffff6b ),
    gen_st_value_test( "sb", 0x6c6d6e6f,  13, 0x0000201f, 0xffffff6f ),
    gen_st_value_test( "sb", 0x70717273,  17, 0x0000201f, 0xffffff73 ),
    gen_st_value_test( "sb", 0x74757677,  21, 0x0000201f, 0xffffff77 ),

    # Test negative offset with unaligned base

    gen_st_value_test( "sb", 0x78797a7b, -21, 0x00002039, 0xffffff7b ),
    gen_st_value_test( "sb", 0x7c7d7e7f, -17, 0x00002039, 0xffffff7f ),
    gen_st_value_test( "sb", 0x80818283, -13, 0x00002039, 0xffffff83 ),
    gen_st_value_test( "sb", 0x84858687,  -9, 0x00002039, 0xffffff87 ),
    gen_st_value_test( "sb", 0x88898a8b,  -5, 0x00002039, 0xffffff8b ),
    gen_st_value_test( "sb", 0x8c8d8e8f,  -1, 0x00002039, 0xffffff8f ),

    gen_word_data([0xffffffff]*16)

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in xrange(128):
    data.append( random.randint(0,0xff) )

  # Generate random accesses to this data

  asm_code = []
  for i in xrange(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = Bits( 32, 0x2000 + b )
    offset = Bits( 16, (a - b) )
    result = Bits( 32, data[a] )

    asm_code.append( gen_st_random_test( "sb", "lbu", result.uint(), offset.int(), base.uint() ) )

  # Generate some random data to initialize memory

  initial_data = []
  for i in xrange(128):
    initial_data.append( random.randint(0,0xff) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_byte_data( initial_data ) )
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
