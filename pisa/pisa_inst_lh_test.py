#=========================================================================
# pisa_lh_test.py
#=========================================================================

import pytest
import random
import pisa_encoding

from new_pymtl import Bits
from new_pymtl import helpers
from PisaSim   import PisaSim

from pisa_inst_test_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    mfc0 r1, mngr2proc < 0x00002000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lh   r2, 0(r1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtc0 r2, proc2mngr > 0x00000304

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_byp_test
#-------------------------------------------------------------------------

def gen_dest_byp_test():
  return [

    gen_ld_dest_byp_test( 5, "lh", 0x2000, 0x00000203 ),
    gen_ld_dest_byp_test( 4, "lh", 0x2004, 0x00000607 ),
    gen_ld_dest_byp_test( 3, "lh", 0x2008, 0x00000a0b ),
    gen_ld_dest_byp_test( 2, "lh", 0x200c, 0x00000e0f ),
    gen_ld_dest_byp_test( 1, "lh", 0x2010, 0x00001213 ),
    gen_ld_dest_byp_test( 0, "lh", 0x2014, 0x00001617 ),

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

    gen_ld_base_byp_test( 5, "lh", 0x2000, 0x00000203 ),
    gen_ld_base_byp_test( 4, "lh", 0x2004, 0x00000607 ),
    gen_ld_base_byp_test( 3, "lh", 0x2008, 0x00000a0b ),
    gen_ld_base_byp_test( 2, "lh", 0x200c, 0x00000e0f ),
    gen_ld_base_byp_test( 1, "lh", 0x2010, 0x00001213 ),
    gen_ld_base_byp_test( 0, "lh", 0x2014, 0x00001617 ),

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
    gen_ld_base_eq_dest_test( "lh", 0x2000, 0x00000304 ),
    gen_word_data([ 0x01020304 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Verify sign extension

    gen_ld_value_test( "lh",   0, 0x00002018, 0xfffffcfd ),
    gen_ld_value_test( "lh",   0, 0x0000201a, 0xfffffafb ),

    # Test positive offsets

    gen_ld_value_test( "lh",   0, 0x00002000, 0xffffbeef ),
    gen_ld_value_test( "lh",   2, 0x00002000, 0xffffdead ),
    gen_ld_value_test( "lh",   4, 0x00002000, 0x00000203 ),
    gen_ld_value_test( "lh",   6, 0x00002000, 0x00000001 ),
    gen_ld_value_test( "lh",   8, 0x00002000, 0x00000607 ),
    gen_ld_value_test( "lh",  10, 0x00002000, 0x00000405 ),

    # Test negative offsets

    gen_ld_value_test( "lh", -10, 0x00002014, 0x00000405 ),
    gen_ld_value_test( "lh",  -8, 0x00002014, 0x00000a0b ),
    gen_ld_value_test( "lh",  -6, 0x00002014, 0x00000809 ),
    gen_ld_value_test( "lh",  -4, 0x00002014, 0x00000e0f ),
    gen_ld_value_test( "lh",  -2, 0x00002014, 0x00000c0d ),
    gen_ld_value_test( "lh",   0, 0x00002014, 0xffffcafe ),

    # Test positive offset with unaligned base

    gen_ld_value_test( "lh",   1, 0x00001fff, 0xffffbeef ),
    gen_ld_value_test( "lh",   5, 0x00001fff, 0x00000203 ),
    gen_ld_value_test( "lh",   9, 0x00001fff, 0x00000607 ),
    gen_ld_value_test( "lh",  13, 0x00001fff, 0x00000a0b ),
    gen_ld_value_test( "lh",  17, 0x00001fff, 0x00000e0f ),
    gen_ld_value_test( "lh",  21, 0x00001fff, 0xffffcafe ),

    # Test negative offset with unaligned base

    gen_ld_value_test( "lh", -21, 0x00002015, 0xffffbeef ),
    gen_ld_value_test( "lh", -17, 0x00002015, 0x00000203 ),
    gen_ld_value_test( "lh", -13, 0x00002015, 0x00000607 ),
    gen_ld_value_test( "lh",  -9, 0x00002015, 0x00000a0b ),
    gen_ld_value_test( "lh",  -5, 0x00002015, 0x00000e0f ),
    gen_ld_value_test( "lh",  -1, 0x00002015, 0xffffcafe ),

    gen_word_data([
      0xdeadbeef,
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0xcafecafe,
      0xfafbfcfd,
    ])

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
    result = helpers.sext( Bits( 16, data[a] ), 32 )

    asm_code.append( gen_ld_value_test( "lh", offset.int(), base.uint(), result.uint() ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_hword_data( data ) )
  return asm_code

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test     ),
  asm_test( gen_dest_byp_test  ),
  asm_test( gen_base_byp_test   ),
  asm_test( gen_srcs_dest_test ),
  asm_test( gen_value_test     ),
  asm_test( gen_random_test    ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

