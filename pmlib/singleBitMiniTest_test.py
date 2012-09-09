#=========================================================================
# Single bit mini test Test Suite
#=========================================================================

from pymtl import *
from singleBitMiniTest import *

from TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_singleBitMiniTest( dump_vcd, ModelType, test_vectors, wait_cycles ):

  # Instantiate and elaborate the model

  model = ModelType(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
  	model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
  	assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out, wait_cycles )
  if dump_vcd:
    sim.dump_vcd( "pmlib-singleBitMiniTest-test" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# test vector lsb
#-------------------------------------------------------------------------

test_msg_lsb = [
    [ 0x0a0a, 0x0 ],
    [ 0x000c, 0x0 ],
    [ 0x0c0b, 0x1 ],
    [ 0x0c07, 0x1 ],
    [ 0x0001, 0x1 ],
    [ 0x0002, 0x0 ],
    [ 0x0003, 0x1 ],
    [ 0x0004, 0x0 ],
    [ 0x0005, 0x1 ],
    [ 0x0006, 0x0 ],
  ]

#-------------------------------------------------------------------------
# test vector msb
#-------------------------------------------------------------------------

test_msg_msb = [
    [ 0x20a0, 0x0 ],
    [ 0x4000, 0x0 ],
    [ 0xb0c0, 0x1 ],
    [ 0x80c0, 0x1 ],
    [ 0xf000, 0x1 ],
    [ 0x5000, 0x0 ],
    [ 0xa000, 0x1 ],
    [ 0x4000, 0x0 ],
    [ 0xc000, 0x1 ],
    [ 0x6000, 0x0 ],
  ]

#-------------------------------------------------------------------------
# slice within a model ver1 unit tests
#-------------------------------------------------------------------------

def test_singlemodel_ver1( dump_vcd ):
  run_test_singleBitMiniTest( dump_vcd, slice_in_model_ver1, test_msg_lsb, 0 )

#-------------------------------------------------------------------------
# slice within a model ver2 unit tests
#-------------------------------------------------------------------------

def test_singlemodel_ver2( dump_vcd ):
  run_test_singleBitMiniTest( dump_vcd, slice_in_model_ver2, test_msg_msb, 0 )

#-------------------------------------------------------------------------
# slice between models ver1 unit tests
#-------------------------------------------------------------------------

def test_twomodels_ver1( dump_vcd ):
  run_test_singleBitMiniTest( dump_vcd, slice_bet_models_1, test_msg_lsb, 1 )

#-------------------------------------------------------------------------
# slice between models ver1 unit tests
#-------------------------------------------------------------------------

def test_twomodels_ver2( dump_vcd ):
  run_test_singleBitMiniTest( dump_vcd, slice_bet_models_2, test_msg_lsb, 1 )

