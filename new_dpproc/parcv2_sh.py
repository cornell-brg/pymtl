#=========================================================================
# parcv2 sh tests
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

def sh_no_hazards():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0, 0xffff
      la    $3, tdata_0
      nop
      nop
      nop
      sh    $2, 0($3)
      lw    $4, 0($3)
      mtc0  $4, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0x00000000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in W stage

def sh_hazard_W():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0, 0xffff
      la    $3, tdata_0
      nop
      nop
      sh    $2, 0($3)
      lw    $4, 0($3)
      mtc0  $4, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0x00000000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in M stage

def sh_hazard_M():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0, 0xffff
      la    $3, tdata_0
      nop
      sh    $2, 0($3)
      lw    $4, 0($3)
      mtc0  $4, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0x00000000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0x0000ffff

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in X stage

def sh_hazard_X():

  asm_str = \
    ( test_start +
  """
      addiu $2, $0, 0xffff
      la    $3, tdata_0
      sh    $2, 0($3)
      lw    $4, 0($3)
      mtc0  $4, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0x00000000
  """ )

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

def sh_vmh_delay0():

  test_file = vmh_dir + 'parcv2-sh.vmh'

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]

# test with delay

def sh_vmh_delay5():

  test_file = vmh_dir + 'parcv2-sh.vmh'

  mem_delay       = 5
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]
