#=========================================================================
# Mux_test.py
#=========================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator
from Mux        import Mux

#-------------------------------------------------------------------------
# run_test_mux
#-------------------------------------------------------------------------
def run_test_mux( dump_vcd, test_verilog,
                  ModelType, num_inputs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType(16, num_inputs)
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    for i in range(num_inputs):
      model.in_[i].value = test_vector[i]
    model.sel.value = test_vector[num_inputs]

  def tv_out( model, test_vector ):
    if test_vector[num_inputs] != '?':
      assert model.out.value == test_vector[num_inputs+1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_mux2
#-------------------------------------------------------------------------
def test_mux2( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 2, [
    [ 0x0a0a, 0x0b0b, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0, 0x0a0a ],
    [ 0x0c0c, 0x0d0d, 1, 0x0d0d ],
    [ 0x0c0c, 0x0d0d, 0, 0x0c0c ],
  ])

#-------------------------------------------------------------------------
# test_mux3
#-------------------------------------------------------------------------
def test_mux3( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 3, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0, 0x0a0a ],
    [ 0x0d0d, 0x0e0e, 0x0f0f, 1, 0x0e0e ],
    [ 0x0d0d, 0x0e0e, 0x0f0f, 2, 0x0f0f ],
    [ 0x0d0d, 0x0e0e, 0x0f0f, 0, 0x0d0d ],
  ])

#-------------------------------------------------------------------------
# test_mux4
#-------------------------------------------------------------------------
def test_mux4( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 4, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0, 0x0a0a ],
  ])

#-------------------------------------------------------------------------
# test_mux5
#-------------------------------------------------------------------------
def test_mux5( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 5, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 4, 0x0e0e ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0, 0x0a0a ],
  ])

#-------------------------------------------------------------------------
# test_mux6
#-------------------------------------------------------------------------
def test_mux6( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 6, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 4, 0x0e0e ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 5, 0x0f0f ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0, 0x0a0a ],
  ])

#-------------------------------------------------------------------------
# test_mux7
#-------------------------------------------------------------------------
def test_mux7( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 7, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 4, 0x0e0e ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 5, 0x0f0f ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 6, 0x0101 ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0, 0x0a0a ],
  ])

#-------------------------------------------------------------------------
# test_mux8
#-------------------------------------------------------------------------
def test_mux8( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 8, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 4, 0x0e0e ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 5, 0x0f0f ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 6, 0x0101 ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 7, 0x0202 ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0x0e0e, 0x0f0f, 0x0101, 0x0202, 0, 0x0a0a ],
  ])


