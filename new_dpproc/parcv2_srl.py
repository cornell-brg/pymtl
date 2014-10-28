#=========================================================================
# parcv2 srl tests
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

# Test instructions with no data hazards

def srl_no_hazards():

  asm_str = \
    ( test_start +
  """
      li   $2, 0xffffffff
      srl  $2, $2, 16
      nop
      nop
      nop
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in W stage

def srl_hazard_W():

  asm_str = \
    ( test_start +
  """
      li   $2, 0xffffffff
      srl  $2, $2, 16
      nop
      nop
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in M stage

def srl_hazard_M():

  asm_str = \
    ( test_start +
  """
      li   $2, 0xffffffff
      srl  $2, $2, 16
      nop
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in X stage

def srl_hazard_X():

  asm_str = \
    ( test_start +
  """
      li   $2, 0xffffffff
      srl  $2, $2, 16
      mtc0  $2, $1
  """
    + test_end )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# VMH File Assembly Tests
#---------------------------------------------------------------------------
# Self-checking VMH file based assembly tests

# VMH Files location

vmh_dir = '../tests/build/vmh/'

# test with no delay

def srl_vmh_delay0():

  test_file = vmh_dir + 'parcv2-srl.vmh'

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]

# test with delay

def srl_vmh_delay5():

  test_file = vmh_dir + 'parcv2-srl.vmh'

  mem_delay       = 5
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]
