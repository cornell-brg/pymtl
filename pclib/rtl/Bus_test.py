#=======================================================================
# Bus_test.py
#=======================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator
from Bus        import Bus

#-----------------------------------------------------------------------
# run_test_bus
#-----------------------------------------------------------------------
def run_test_bus( model, test_vectors ):

  # Instantiate and elaborate the model

  model.elaborate()

  # Define functions mapping the test vector to ports in model

  num_inputs = len( model.in_ )

  def tv_in( model, test_vector ):
    n = num_inputs
    for i in range(num_inputs):
      model.in_[i].value = test_vector[i]
    model.sel.value = test_vector[n]

  def tv_out( model, test_vector ):
    n = num_inputs + 1
    for i in range(num_inputs):
      assert model.out[i].value == test_vector[n+i]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# test_crossbar3
#-----------------------------------------------------------------------
def test_bus3( dump_vcd, test_verilog ):
  model = Bus( 3, 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  run_test_bus( model, [
    [ 0xdead, 0xbeef, 0xcafe, 0, 0xdead, 0xdead, 0xdead ],
    [ 0xdead, 0xbeef, 0xcafe, 1, 0xbeef, 0xbeef, 0xbeef ],
    [ 0xdead, 0xbeef, 0xcafe, 2, 0xcafe, 0xcafe, 0xcafe ],
  ])
