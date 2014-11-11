#=========================================================================
# Mux_test.py
#=========================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator
from Mux        import Mux

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_mux( dump_vcd, test_verilog,
                  ModelType, num_inputs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType(16, num_inputs)
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    for i in xrange(num_inputs):
      model.in_[i].value = test_vector[i]
    model.sel.value = test_vector[num_inputs]

  def tv_out( model, test_vector ):
    if test_vector[num_inputs] != '?':
      assert model.out.value == test_vector[num_inputs+1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-muxes-test_mux" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Mux2 unit tests
#-------------------------------------------------------------------------

def test_mux2( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 2, [
    [ 0x0a0a, 0x0b0b, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0, 0x0a0a ],
    [ 0x0c0c, 0x0d0d, 1, 0x0d0d ],
    [ 0x0c0c, 0x0d0d, 0, 0x0c0c ],
  ])

#-------------------------------------------------------------------------
# Mux3 unit tests
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
# Mux4 unit tests
#-------------------------------------------------------------------------

def test_mux4( dump_vcd, test_verilog ):
  run_test_mux( dump_vcd, test_verilog, Mux, 4, [
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 1, 0x0b0b ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 2, 0x0c0c ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 3, 0x0d0d ],
    [ 0x0a0a, 0x0b0b, 0x0c0c, 0x0d0d, 0, 0x0a0a ],
  ])

#-------------------------------------------------------------------------
# Mux5 unit tests
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
# Mux6 unit tests
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
# Mux7 unit tests
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
# Mux8 unit tests
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


