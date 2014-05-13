#==============================================================================
# DummyCOP_test.py
#==============================================================================

from new_pymtl import *
from new_pmlib import TestVectorSimulator
from DummyCOP  import DummyCOPCL

#------------------------------------------------------------------------------
# test_DummyCOP_directed
#------------------------------------------------------------------------------
def test_DummyCOP_directed( dump_vcd ):

  # Select and elaborate the model under test

  model = DummyCOPCL()
  model.elaborate()

  data_nbits = 32

  # Define test input and output functions

  def tv_in( model, test_vector ):
    model.from_cpu.val     .value = test_vector[0]
    model.from_cpu.msg[32:].value = test_vector[1]
    model.from_cpu.msg[:32].value = test_vector[2]

  def tv_out( model, test_vector ):
    assert model.from_cpu.rdy == test_vector[3]
    assert model.to_cpu       == test_vector[4]
    assert model.result       == test_vector[5]

  # Define the test vectors
  test_vectors = [
    # Inputs--------  Outputs------------------------------------
    # val addr data   rdy done result
    [ 0,  1,   99,    1,  0,   0 ],
    [ 0,  0,   99,    1,  0,   0 ],
    [ 1,  1,    7,    1,  0,   0 ],
    [ 1,  1,    6,    1,  0,   0 ],
    [ 1,  2,    2,    1,  0,   0 ],
    [ 1,  0,    1,    1,  0,   0 ],
    [ 0,  0,   99,    0,  0,   0 ],
    [ 0,  0,   99,    0,  1,   8 ],
    [ 0,  0,   99,    1,  0,   8 ],
    [ 1,  2,   10,    1,  0,   8 ],
    [ 0,  0,   99,    1,  0,   8 ],
    [ 1,  0,    1,    1,  0,   8 ],
    [ 1,  0,    2,    0,  0,   8 ],
    [ 0,  0,   99,    0,  1,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
    [ 0,  0,   99,    1,  0,  16 ],
  ]

  # Create the simulator and configure it
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "LaneManagerOneLane.vcd" )

  # Run the simulator
  sim.run_test()
