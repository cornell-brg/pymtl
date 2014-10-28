#=========================================================================
# parcv2 mul tests
#=========================================================================

from pymtl import *

from pclib.SparseMemoryImage import SparseMemoryImage

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

# Test instructions with no data hazards

def mul_no_hazards():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  -1
      mul   $3, $2, $1
      nop
      nop
      nop
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xfffffffc

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in W stage

def mul_hazard_W():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  -1
      mul   $3, $2, $1
      nop
      nop
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xfffffffc

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in M stage

def mul_hazard_M():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  -1
      mul   $3, $2, $1
      nop
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xfffffffc

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in X stage

def mul_hazard_X():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0,  4
      addiu $1, $0,  -1
      mul   $3, $2, $1
      mtc0  $3, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xfffffffc

  return [ mem_delay, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# VMH File Assembly Tests
#---------------------------------------------------------------------------
# Self-checking VMH file based assembly tests

# VMH Files location

vmh_dir = '../tests/build/vmh/'

# test with no delay

def mul_vmh_delay0():

  test_file = vmh_dir + 'parcv2-mul.vmh'

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]

# test with delay

def mul_vmh_delay5():

  test_file = vmh_dir + 'parcv2-mul.vmh'

  mem_delay       = 5
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]
