#=========================================================================
# MinMax Unit Tests
#=========================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator

from MinMax import MinMax

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

  # Test vectors

  test_vectors = [
   # -- in -- -- out --
    [  4,  3,   3,  4 ],
    [  9,  6,   6,  9 ],
    [ 12, 16,  12, 16 ],
    [ 12, 16,  12, 16 ],
  ]

  # Instantiate and elaborate the model

  model = MinMax()
  model.vcd_file = dump_vcd
  model.elaborate()

  # Function to set the inputs on the model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  # Function to verify the outputs from the model

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.min.value == test_vector[2]
    if test_vector[3] != '?':
      assert model.max.value == test_vector[3]

  # Create and run the test simulation

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

