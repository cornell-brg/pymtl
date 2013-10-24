#=========================================================================
# SorterBL Test Suite
#=========================================================================

from new_pymtl import *
import random

from SorterBL import SorterBL

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_sorter_test( dump_vcd, vcd_file_name, ModelType, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType()
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Iterate setting the inputs and verifying the outputs each cycle

  print ""

  sim.reset()
  for test_vector in test_vectors:

    # Set inputs

    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]
    model.in_[3].value = test_vector[3]

    # Evaluate combinational concurrent blocks in simulator

    sim.eval_combinational()

    # Print the line trace

    sim.print_line_trace()

    # Verify outputs

    if test_vector[4] != '?':
      assert model.out[0].value == test_vector[4]

    if test_vector[5] != '?':
      assert model.out[1].value == test_vector[5]

    if test_vector[6] != '?':
      assert model.out[2].value == test_vector[6]

    if test_vector[7] != '?':
      assert model.out[3].value == test_vector[7]

    # Tick the simulator one cycle

    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

test_vectors_basics = [
  # ----- in -----  ----- out -----
  [  4,  3,  2,  1, '?','?','?','?'],
  [  9,  6,  7,  1,  1,  2,  3,  4 ],
  [ 12, 16,  3, 42,  1,  6,  7,  9 ],
  [ 12, 16,  3, 42,  3, 12, 16, 42 ],
]

def test_basics( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterBL_test_basics.vcd",
                   SorterBL, test_vectors_basics )

#-------------------------------------------------------------------------
# Test duplicates
#-------------------------------------------------------------------------

test_vectors_duplicates = [
  # ----- in -----  ----- out -----
  [  2,  8,  9,  9, '?','?','?','?'],
  [  2,  8,  2,  8,  2,  8,  9,  9 ],
  [  1,  1,  1,  1,  2,  2,  8,  8 ],
  [  1,  1,  1,  1,  1,  1,  1,  1 ],
]

def test_duplicates( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterBL_test_duplicates.vcd",
                   SorterBL, test_vectors_duplicates )

#-------------------------------------------------------------------------
# Test random
#-------------------------------------------------------------------------

# Create random inputs with reference outputs. Notice how we have to skew
# the reference outputs by one cycle since we are testing a single-cycle
# behavioral model.

test_vectors_random = []
prev_test_vector_random = [ '?', '?', '?', '?' ]

for i in xrange(90):

  # Create random list of four integers

  in_list = [ random.randint(0,99) for x in xrange(4) ]

  # Create output list which is sorted version of input

  out_list = in_list[:]
  out_list.sort()

  # Add these lists to our test_vectors

  test_vectors_random.append( in_list + prev_test_vector_random )

  # Save outputs for verifying next cycle

  prev_test_vector_random = out_list[:]

def test_random( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterBL_test_random.vcd",
                   SorterBL, test_vectors_random )

