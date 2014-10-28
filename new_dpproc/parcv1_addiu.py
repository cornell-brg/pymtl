#=========================================================================
# parcv1 addiu tests
#=========================================================================

from pymtl import *

from pclib.SparseMemoryImage import SparseMemoryImage

#---------------------------------------------------------------------------
# String based Assembly Tests
#---------------------------------------------------------------------------
# Directed string based assembly tests

# Test instructions with no data hazards

def addiu_no_hazards():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      addiu $2, $0, 4
      nop
      nop
      nop
      mtc0  $2, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 4

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in W stage

def addiu_hazard_W():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      addiu $2, $0, 4
      nop
      nop
      mtc0  $2, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 4

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in M stage

def addiu_hazard_M():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      addiu $2, $0, 4
      nop
      mtc0  $2, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 4

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in X stage

def addiu_hazard_X():

  asm_str = \
  """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
    _test:
      addiu $2, $0, 4
      mtc0  $2, $1
    .end    _test;
  """

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 4

  return [ mem_delay, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# VMH File Assembly Tests
#---------------------------------------------------------------------------
# Self-checking VMH file based assembly tests

# VMH Files location

vmh_dir = '../tests/build/vmh/'

# test with no delay

def addiu_vmh_delay0():

  test_file = vmh_dir + 'parcv1-addiu.vmh'

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]

# test with delay

def addiu_vmh_delay5():

  test_file = vmh_dir + 'parcv1-addiu.vmh'

  mem_delay       = 5
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]
