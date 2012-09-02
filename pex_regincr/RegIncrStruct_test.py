#=========================================================================
# RegIncrStruct Unit Tests
#=========================================================================

from pymtl import *
from pmlib import TestVectorSimulator

from RegIncrStruct import RegIncrStruct

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test( name, test_vectors ):

  # Instantiate and elaborate the model

  model = RegIncrStruct()
  model.elaborate()

  # Function to set the inputs on the model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  # Function to verify the outputs from the model

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Create and run the test simulation

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.dump_vcd( name )
  sim.run_test()

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics():
  run_test( "pex-regincr-RegIncrStruct_test_basics", [
    # in   out
    [  1,  '?'],
    [  2,   2 ],
    [ 13,   3 ],
    [ 42,  14 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 51,  43 ],
    [ 51,  52 ],
  ])

