#=========================================================================
# regs_test.py
#=========================================================================

import pytest

from pymtl      import *
from pclib.test import TestVectorSimulator
from regs       import *

#-------------------------------------------------------------------------
# test_Reg
#-------------------------------------------------------------------------
def test_Reg( dump_vcd, test_verilog ):

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
  model.vcd_file = dump_vcd
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_Reg
#-------------------------------------------------------------------------
def test_RegEn( dump_vcd, test_verilog ):

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
  model.vcd_file = dump_vcd
  if test_verilog:
    model = get_verilated( model )
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
  sim.run_test()

#-------------------------------------------------------------------------
# test_RegRst
#-------------------------------------------------------------------------
@pytest.mark.parametrize( "reset", [
    (0x0000),
    (0xbeef),
    (0xabcd),
])
def test_RegRst( dump_vcd, test_verilog, reset):

  test_vectors = [
    # in      out
    [ 0x0a0a,  reset ],
    [ 0x0b0b, 0x0a0a ],
    [ 0x0c0c, 0x0b0b ],
    [ 0x0d0d, 0x0c0c ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0d0d, 0x0d0d ],
    [ 0x0e0e, 0x0d0d ],
    [ 0x0e0e, 0x0e0e ],
  ]

  # Instantiate and elaborate the model

  model = RegRst( 16, reset )
  model.vcd_file = dump_vcd
  print model.vcd_file
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_RegEnRst
#-------------------------------------------------------------------------
@pytest.mark.parametrize( "reset", [
    (0x0000),
    (0xbeef),
    (0xabcd),
])
def test_RegEnRst( dump_vcd, test_verilog, reset ):

  test_vectors = [
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
  ]

  # Instantiate and elaborate the model

  model = RegEnRst( 16, reset )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = get_verilated( model )
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
  sim.run_test()
