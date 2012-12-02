#=========================================================================
# Crossbar Test Suite
#=========================================================================

from pymtl import *

from pmlib     import TestVectorSimulator
#from Crossbar3 import Crossbar3
from WCrossbar3 import Crossbar3

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_crossbar( dump_vcd, ModelType, num_inputs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType()
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    n = num_inputs
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]
    model.in2.value = test_vector[2]
    model.sel0.value = test_vector[3]
    model.sel1.value = test_vector[4]
    model.sel2.value = test_vector[5]

  def tv_out( model, test_vector ):
    assert model.out0.value == test_vector[6]
    assert model.out1.value == test_vector[7]
    assert model.out2.value == test_vector[8]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_crossbar" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# 3 Port Crossbar Unit Tests
#-------------------------------------------------------------------------

def test_crossbar3( dump_vcd ):
  run_test_crossbar( dump_vcd, Crossbar3, 3, [
    [ 0xdead, 0xbeef, 0xcafe, 0, 1, 2, 0xdead, 0xbeef, 0xcafe ],
    [ 0xdead, 0xbeef, 0xcafe, 0, 2, 1, 0xdead, 0xcafe, 0xbeef ],
    [ 0xdead, 0xbeef, 0xcafe, 1, 2, 0, 0xbeef, 0xcafe, 0xdead ],
    [ 0xdead, 0xbeef, 0xcafe, 1, 0, 2, 0xbeef, 0xdead, 0xcafe ],
    [ 0xdead, 0xbeef, 0xcafe, 2, 1, 0, 0xcafe, 0xbeef, 0xdead ],
    [ 0xdead, 0xbeef, 0xcafe, 2, 0, 1, 0xcafe, 0xdead, 0xbeef ],
  ])
