#=========================================================================
# regs_test.py
#=========================================================================

import pytest

from pymtl      import *
from pclib.test import TestVectorSimulator
from regs       import *

#-------------------------------------------------------------------------
# Register unit tests
#-------------------------------------------------------------------------

def test_reg( dump_vcd, test_verilog ):

  model = Reg(16)
  if test_verilog:
    model = get_verilated( model )

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
    sim.dump_vcd( get_vcd_filename() )
  sim.run_test()

#-------------------------------------------------------------------------
# Register with enable signal unit tests
#-------------------------------------------------------------------------

def test_reg_en( dump_vcd, test_verilog ):

  model = RegEn(16)
  if test_verilog:
    model = get_verilated( model )

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
    sim.dump_vcd( get_vcd_filename() )
  sim.run_test()

#-------------------------------------------------------------------------
# Register with reset signal unit tests
#-------------------------------------------------------------------------

def run_test_reg_rst( dump_vcd, model, test_vectors ):

  # Instantiate and elaborate the model

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
    sim.dump_vcd( dump_vcd )
  sim.run_test()

@pytest.mark.parametrize( "reset", [
    (0x0000),
    (0xbeef),
    (0xabcd),
])
def test_reg_rst( dump_vcd, test_verilog, reset):
  model = RegRst( 16, reset )
  if test_verilog:
    model = get_verilated( model )

  run_test_reg_rst( get_vcd_filename() if dump_vcd else False, model, [
    # in      out
    [ 0x0a0a,  reset ],
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

def run_test_reg_en_rst( dump_vcd, model, test_vectors ):

  # Instantiate and elaborate the model

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
    sim.dump_vcd( dump_vcd )
  sim.run_test()

@pytest.mark.parametrize( "reset", [
    (0x0000),
    (0xbeef),
    (0xabcd),
])
def test_reg_en_rst( dump_vcd, test_verilog, reset ):
  model = RegEnRst( 16, reset )
  if test_verilog:
    model = get_verilated( model )

  run_test_reg_en_rst( get_vcd_filename() if dump_vcd else False, model, [
    # in      en out
    [ 0x0a0a, 0,  reset ],
    [ 0x0b0b, 1,  reset ],
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


