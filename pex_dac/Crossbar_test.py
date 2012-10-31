#=========================================================================
# Crossbar Test Suite
#=========================================================================

from pymtl import *

from pmlib    import TestVectorSimulator
from Crossbar import Crossbar

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_crossbar( dump_vcd, ModelType, num_inputs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( num_inputs, 16 )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    n = num_inputs
    for i in xrange(num_inputs):
      model.in_[i].value = test_vector[i]
      model.sel[i].value = test_vector[n+i]

  def tv_out( model, test_vector ):
    n = 2*num_inputs
    for i in xrange(num_inputs):
      assert model.out[i].value == test_vector[n+i]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_crossbar" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# 3 Port Crossbar Unit Tests
#-------------------------------------------------------------------------

def test_crossbar3( dump_vcd ):
  run_test_crossbar( dump_vcd, Crossbar, 3, [
    [ 0xdead, 0xbeef, 0xcafe, 0, 1, 2, 0xdead, 0xbeef, 0xcafe ],
    [ 0xdead, 0xbeef, 0xcafe, 0, 2, 1, 0xdead, 0xcafe, 0xbeef ],
    [ 0xdead, 0xbeef, 0xcafe, 1, 2, 0, 0xbeef, 0xcafe, 0xdead ],
    [ 0xdead, 0xbeef, 0xcafe, 1, 0, 2, 0xbeef, 0xdead, 0xcafe ],
    [ 0xdead, 0xbeef, 0xcafe, 2, 1, 0, 0xcafe, 0xbeef, 0xdead ],
    [ 0xdead, 0xbeef, 0xcafe, 2, 0, 1, 0xcafe, 0xdead, 0xbeef ],
  ])




