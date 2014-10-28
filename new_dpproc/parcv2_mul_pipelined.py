#=========================================================================
# parcv2 pipelined mul tests
#=========================================================================

from pymtl import *

from new_pmlib.SparseMemoryImage import SparseMemoryImage

#---------------------------------------------------------------------------
# String based Assembly Tests
#---------------------------------------------------------------------------
# Directed string based assembly tests

# test_start string

test_start = """
  .text;
  .align  4;
  .global _test;
  .ent    _test;
  _test:
"""

# test_end string

test_end   = """
  .end    _test;
"""

def mul_pipeline_addi_raw():
  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  2
      mul   $3, $2, $1
      addiu $2, $3,  4
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 12
  return [ mem_delay, sparse_mem_img, expected_result ]


def mul_pipeline_add_raw():
  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  2
      mul   $3, $2, $1
      addu  $2, $3, $3
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 16
  return [ mem_delay, sparse_mem_img, expected_result ]

def mul_pipeline_addi_waw():
  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  2
      mul   $3, $2, $1
      addiu $3, $2,  1
      nop
      nop
      nop
      nop
      nop
      nop
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 5
  return [ mem_delay, sparse_mem_img, expected_result ]

def mul_pipeline_add_waw():
  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  3
      mul   $3, $2, $1
      addu  $3, $2, $2
      nop
      nop
      nop
      nop
      nop
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 8
  return [ mem_delay, sparse_mem_img, expected_result ]

def mul_pipeline_fill():
  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  2
      addiu $1, $0,  3
      mul   $3, $2, $1
      mul   $4, $2, $1
      mul   $5, $2, $1
      mul   $6, $2, $1
      addu  $7, $2, $2
      addu  $7, $2, $2
      addu  $7, $2, $2
      addu  $7, $2, $2
      addu  $7, $4, $3
      addu  $7, $7, $5
      addu  $7, $7, $6
      mtc0  $7, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 24
  return [ mem_delay, sparse_mem_img, expected_result ]
