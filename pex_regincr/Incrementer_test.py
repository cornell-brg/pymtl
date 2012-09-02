#=========================================================================
# Incrementer Test Suite
#=========================================================================

from pymtl import *
import pmlib

from Incrementer import Incrementer

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in   out
    [  0,   1 ],
    [  1,   2 ],
    [ 13,  14 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 51,  52 ],
    [ 51,  52 ],
  ]

  # Instantiate and elaborate the model

  model = Incrementer(16)
  model.elaborate()

  # Function to set the inputs on the model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  # Function to verify the outputs from the model

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Create and run the test simulation

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pex-regincr-Incrementer_test_basics.vcd" )
  sim.run_test()

