#=========================================================================
# Crossbar Test Suite
#=========================================================================

from pymtl import *

from pmlib     import TestVectorSimulator
from Crossbar5 import Crossbar5
#from WCrossbar5 import Crossbar5

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_crossbar( dump_vcd, ModelType, num_inputs, test_vectors ):

  # Instantiate and elaborate the model

  #model = ModelType()
  model = ModelType(0,0)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    n = num_inputs
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]
    model.in2.value = test_vector[2]
    model.in3.value = test_vector[3]
    model.in4.value = test_vector[4]
    model.sel0.value = test_vector[5]
    model.sel1.value = test_vector[6]
    model.sel2.value = test_vector[7]
    model.sel3.value = test_vector[8]
    model.sel4.value = test_vector[9]

  def tv_out( model, test_vector ):
    assert model.out0.value == test_vector[10]
    assert model.out1.value == test_vector[11]
    assert model.out2.value == test_vector[12]
    assert model.out3.value == test_vector[13]
    assert model.out4.value == test_vector[14]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_crossbar" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# 5 Port Crossbar Unit Tests
#-------------------------------------------------------------------------

def test_crossbar3( dump_vcd ):
  run_test_crossbar( dump_vcd, Crossbar5, 5, [
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 0, 1, 2, 3, 4, 0xde, 0xbe, 0xca, 0xab, 0xfe ],
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 1, 2, 3, 4, 0, 0xbe, 0xca, 0xab, 0xfe, 0xde ],
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 2, 3, 4, 0, 1, 0xca, 0xab, 0xfe, 0xde, 0xbe ],
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 3, 4, 0, 1, 2, 0xab, 0xfe, 0xde, 0xbe, 0xca ],
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 4, 0, 1, 2, 3, 0xfe, 0xde, 0xbe, 0xca, 0xab ],
    [ 0xde, 0xbe, 0xca, 0xab, 0xfe, 2, 0, 1, 4, 3, 0xca, 0xde, 0xbe, 0xfe, 0xab ],
  ])
