#=========================================================================
# DirectedMappedWriteBackCacheTagArray Unit Test
#=========================================================================

from   pymtl import *
import pclib


import pytest

#from DirectMappedWriteBackCacheTagArray import DirectMappedWriteBackCacheTagArray
# TODO: This currently fails because DirectMappedWriteBackCacheTagArray
#       is missing SRAM/RAM implementations!

#def test_DirectMappedWriteBackCacheTagArray_test( dump_vcd ):
#
#  # Test Vectors
#
#  test_vectors = [
#
#    # -----------------------------------------  -----------------  -------- ---------- ------ ------
#    # Search                                     Write              Validate Invalidate Clean  Dirty
#    # -----------------------------------------  -----------------  -------- ---------- ------ ------
#    # do ptr tag        match  dirty  match_tag  do  ptr tag        do ptr   do ptr     do ptr do ptr
#
#    # Test reset values of state bits: valid and dirty should be 0
#
#    [ 1, 0,  0x0a0a0a0, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 2,  0x0b0b0b0, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 4,  0x0c0c0c0, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 8,  0x0d0d0d0, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#    # Do write ( Refill )
#
#    [ 0, 0,  0x0000000, 0,     0,     '?',       1,  0,  0x0a0a0a0, 1, 0,    0, 0,      1, 0,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  2,  0x0b0b0b0, 1, 2,    0, 0,      1, 2,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  4,  0x0c0c0c0, 1, 4,    0, 0,      1, 4,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  8,  0x0d0d0d0, 1, 8,    0, 0,      1, 8,  0, 0  ],
#
#    # Do search on the tag that was written
#
#    [ 1, 0,  0x0a0a0a0, '?',   '?',   '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 2,  0x0b0b0b0, 1,     0,     0x0a0a0a0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 4,  0x0c0c0c0, 1,     0,     0x0b0b0b0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 8,  0x0d0d0d0, 1,     0,     0x0c0c0c0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#    # Make lines dirty
#
#    [ 0, 0,  0x0000000, 1,     0,     0x0d0d0d0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 0  ],
#    [ 0, 0,  0x0000000, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 2  ],
#    [ 0, 0,  0x0000000, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 4  ],
#    [ 0, 0,  0x0000000, 0,     0,     '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 8  ],
#
#    # Do search on dirty lines
#
#    [ 1, 0,  0x0a0a0a0, '?',   '?',   '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 2,  0x0b0b0b0, 1,     1,     0x0a0a0a0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 4,  0x0c0c0c0, 1,     1,     0x0b0b0b0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 8,  0x0d0d0d0, 1,     1,     0x0c0c0c0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#    # Do search on nonexisting tags (force miss)
#
#    [ 1, 0,  0x3aaaaaa, 1,     1,     0x0d0d0d0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 2,  0x3bbbbbb, 0,     1,     0x0a0a0a0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 4,  0x3cccccc, 0,     1,     0x0b0b0b0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 8,  0x3dddddd, 0,     1,     0x0c0c0c0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#    # Do write (refill)
#
#    [ 0, 0,  0x0000000, 0,     1,     0x0d0d0d0, 1,  0,  0x3aaaaaa, 1, 0,    0, 0,      1, 0,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  2,  0x3bbbbbb, 1, 2,    0, 0,      1, 2,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  4,  0x3cccccc, 1, 4,    0, 0,      1, 4,  0, 0  ],
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  8,  0x3dddddd, 1, 8,    0, 0,      1, 8,  0, 0  ],
#
#    # Do search on tag that was written
#
#    [ 1, 0,  0x3aaaaaa, '?',   '?',   '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 2,  0x3bbbbbb, 1,     0,     0x3aaaaaa, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 4,  0x3cccccc, 1,     0,     0x3bbbbbb, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 8,  0x3dddddd, 1,     0,     0x3cccccc, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 0, 0,  0x0000000, 1,     0,     0x3dddddd, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#    # Multiple single line requests
#
#    [ 0, 0,  0x0000000, '?',   '?',   '?',       1,  3,  0x0e0e0e0, 1, 3,    0, 0,      1, 3,  0, 0  ],
#    [ 1, 3,  0x0e0e0e0, '?',   '?',   '?',       0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 3,  0x0e0e0e0, 1,     0,     0x0e0e0e0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 3  ],
#    [ 1, 3,  0x0e0e0e0, 1,     0,     0x0e0e0e0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 1, 3,  0x1cccccc, 1,     1,     0x0e0e0e0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  1, 3  ],
#    [ 1, 3,  0x1cccccc, 0,     1,     0x0e0e0e0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#    [ 0, 0,  0x0000000, 0,     1,     0x0e0e0e0, 0,  0,  0x0000000, 0, 0,    0, 0,      0, 0,  0, 0  ],
#
#  ]
#
#  # Instantiate and elaborate the model
#
#  model = DirectMappedWriteBackCacheTagArray( 16, 26 )
#  model.elaborate()
#
#  # Define functions mapping the test vector to ports in model
#
#  def tv_in( model, test_vector ):
#    model.search_do.value      = test_vector[0]
#    model.search_ptr.value     = test_vector[1]
#    model.search_tag.value     = test_vector[2]
#    model.write_do.value       = test_vector[6]
#    model.write_ptr.value      = test_vector[7]
#    model.write_tag.value      = test_vector[8]
#    model.validate_do.value    = test_vector[9]
#    model.validate_ptr.value   = test_vector[10]
#    model.invalidate_do.value  = test_vector[11]
#    model.invalidate_ptr.value = test_vector[12]
#    model.clean_do.value       = test_vector[13]
#    model.clean_ptr.value      = test_vector[14]
#    model.dirty_do.value       = test_vector[15]
#    model.dirty_ptr.value      = test_vector[16]
#
#  def tv_out( model, test_vector ):
#    if test_vector[3] != '?':
#      assert model.search_match.value       == test_vector[3]
#    if test_vector[4] != '?':
#      assert model.search_match_dirty.value == test_vector[4]
#    if test_vector[5] != '?':
#      assert model.search_match_tag.value   == test_vector[5]
#
#  # Run the test
#
#  sim = pclib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
#  if dump_vcd:
#    sim.dump_vcd( "DirectMappedWriteBackCacheTagArray_test.vcd" )
#  sim.run_test()
