#=========================================================================
# SorterCL Test Suite
#=========================================================================

from pymtl import *
import random

from SorterCL import SorterCL

# We can use the same test harness from the behavioral-level model

from SorterBL_test import run_sorter_test

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

test_vectors_basics = [
  # ----- in -----  ----- out -----
  [  4,  3,  2,  1, '?','?','?','?'],
  [  9,  6,  7,  1, '?','?','?','?'],
  [ 12, 16,  3, 42,  1,  2,  3,  4 ],
  [ 12, 16,  3, 42,  1,  6,  7,  9 ],
  [ 12, 16,  3, 42,  3, 12, 16, 42 ],
]

def test_basics( dump_vcd ):
  run_sorter_test( dump_vcd, SorterCL, test_vectors_basics )

#-------------------------------------------------------------------------
# Test duplicates
#-------------------------------------------------------------------------

test_vectors_duplicates = [
  # ----- in -----  ----- out -----
  [  2,  8,  9,  9, '?','?','?','?'],
  [  2,  8,  2,  8, '?','?','?','?'],
  [  1,  1,  1,  1,  2,  8,  9,  9 ],
  [  1,  1,  1,  1,  2,  2,  8,  8 ],
  [  1,  1,  1,  1,  1,  1,  1,  1 ],
]

def test_duplicates( dump_vcd ):
  run_sorter_test( dump_vcd, SorterCL, test_vectors_duplicates )

#-------------------------------------------------------------------------
# Test random
#-------------------------------------------------------------------------

# Create random inputs with reference outputs. Notice how we have to skew
# the reference outputs by two cycles since we are testing a cycle-level
# model with a two-cycle latency.

test_vectors_random = []
prev0_test_vector_random = [ '?', '?', '?', '?' ]
prev1_test_vector_random = [ '?', '?', '?', '?' ]

for i in xrange(90):

  # Create random list of four integers

  in_list = [ random.randint(0,99) for x in xrange(4) ]

  # Create output list which is sorted version of input

  out_list = in_list[:]
  out_list.sort()

  # Add these lists to our test_vectors

  test_vectors_random.append( in_list + prev1_test_vector_random )

  # Save outputs for verifying on a later cycle

  prev1_test_vector_random = prev0_test_vector_random
  prev0_test_vector_random = out_list[:]

def test_random( dump_vcd ):
  run_sorter_test( dump_vcd, SorterCL, test_vectors_random )

