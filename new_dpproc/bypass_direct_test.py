#=========================================================================
# bypass logic direct test
#=========================================================================

from pymtl import *

from new_pmlib.SparseMemoryImage import SparseMemoryImage

#---------------------------------------------------------------------------
# String based Assembly Tests
#---------------------------------------------------------------------------
# Directed string based assembly tests

# Test instructions bypass from X

def bypass_from_X():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      addiu $2, $0, 4
      addiu $1, $2, -5
      mul   $3, $1, $2
      mtc0  $3, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xfffffffc

  return [ mem_delay, sparse_mem_img, expected_result ]

