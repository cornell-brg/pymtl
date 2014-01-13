#=========================================================================
# Unit Tests for Registers
#=========================================================================

from new_pymtl import *
from regs      import *

from TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# Register unit tests
#-------------------------------------------------------------------------

def test_reg( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in      out
    [ 0x0a0a, '?'    ],
    [ 0x0b0b, 0x0a0a ],
    [ 0x0c0c, 0x0b0b ],
    [ 0x0d0d, 0x0c0c ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0e0e, 0x0d0d ],
    [ 0x0e0e, 0x0e0e ],
  ]

  # Instantiate and elaborate the model

  model = Reg(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-regs-test_reg.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Register with enable signal unit tests
#-------------------------------------------------------------------------

def test_reg_en( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in      en out
    [ 0x0a0a, 0, '?'    ],
    [ 0x0b0b, 1, '?'    ],
    [ 0x0c0c, 0, 0x0b0b ],
    [ 0x0d0d, 1, 0x0b0b ],
    [ 0x0d0d, 0, 0x0d0d ],
    [ 0x0d0d, 1, 0x0d0d ],
    [ 0x0e0e, 1, 0x0d0d ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0f0f, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
  ]

  # Instantiate and elaborate the model

  model = RegEn(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]
    model.en.value  = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-regs-test_reg_en.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Register with reset signal unit tests
#-------------------------------------------------------------------------

def run_test_reg_rst( dump_vcd, reset_value, test_vectors ):

  # Instantiate and elaborate the model

  model = RegRst( 16, reset_value )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-regs-test_reg_rst_rv" +
                  hex(reset_value) + ".vcd" )
  sim.run_test()

def test_reg_rst_rv0x0( dump_vcd ):
  run_test_reg_rst( dump_vcd, 0x0000, [
    # in      out
    [ 0x0a0a, 0x0000 ],
    [ 0x0b0b, 0x0a0a ],
    [ 0x0c0c, 0x0b0b ],
    [ 0x0d0d, 0x0c0c ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0e0e, 0x0d0d ],
    [ 0x0e0e, 0x0e0e ],
  ])

def test_reg_rst_rv0xbeef( dump_vcd ):
  run_test_reg_rst( dump_vcd, 0xbeef, [
    # in      out
    [ 0x0a0a, 0xbeef ],
    [ 0x0b0b, 0x0a0a ],
    [ 0x0c0c, 0x0b0b ],
    [ 0x0d0d, 0x0c0c ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0e0e, 0x0d0d ],
    [ 0x0e0e, 0x0e0e ],
  ])

def test_reg_rst_rv0xabcd( dump_vcd ):
  run_test_reg_rst( dump_vcd, 0xabcd, [
    # in      out
    [ 0x0a0a, 0xabcd ],
    [ 0x0b0b, 0x0a0a ],
    [ 0x0c0c, 0x0b0b ],
    [ 0x0d0d, 0x0c0c ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0e0e, 0x0d0d ],
    [ 0x0e0e, 0x0e0e ],
  ])

#-------------------------------------------------------------------------
# Register with reset signal unit tests
#-------------------------------------------------------------------------

def run_test_reg_en_rst( dump_vcd, reset_value, test_vectors ):

  # Instantiate and elaborate the model

  model = RegEnRst( 16, reset_value )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]
    model.en.value  = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-regs-test_reg_en_rst_rv" +
                  hex(reset_value) + ".vcd" )
  sim.run_test()

def test_reg_en_rst_rv0x0( dump_vcd ):
  run_test_reg_en_rst( dump_vcd, 0x0000, [
    # in      en out
    [ 0x0a0a, 0, 0x0000 ],
    [ 0x0b0b, 1, 0x0000 ],
    [ 0x0c0c, 0, 0x0b0b ],
    [ 0x0d0d, 1, 0x0b0b ],
    [ 0x0d0d, 0, 0x0d0d ],
    [ 0x0d0d, 1, 0x0d0d ],
    [ 0x0e0e, 1, 0x0d0d ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0f0f, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
  ])

def test_reg_en_rst_rv0x0( dump_vcd ):
  run_test_reg_en_rst( dump_vcd, 0xbeef, [
    # in      en out
    [ 0x0a0a, 0, 0xbeef ],
    [ 0x0b0b, 1, 0xbeef ],
    [ 0x0c0c, 0, 0x0b0b ],
    [ 0x0d0d, 1, 0x0b0b ],
    [ 0x0d0d, 0, 0x0d0d ],
    [ 0x0d0d, 1, 0x0d0d ],
    [ 0x0e0e, 1, 0x0d0d ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0f0f, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
  ])

def test_reg_en_rst_rv0x0( dump_vcd ):
  run_test_reg_en_rst( dump_vcd, 0xabcd, [
    # in      en out
    [ 0x0a0a, 0, 0xabcd ],
    [ 0x0b0b, 1, 0xabcd ],
    [ 0x0c0c, 0, 0x0b0b ],
    [ 0x0d0d, 1, 0x0b0b ],
    [ 0x0d0d, 0, 0x0d0d ],
    [ 0x0d0d, 1, 0x0d0d ],
    [ 0x0e0e, 1, 0x0d0d ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0f0f, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
    [ 0x0e0e, 0, 0x0e0e ],
  ])

