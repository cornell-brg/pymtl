#=========================================================================
# Arithmetic Components Test Suite
#=========================================================================

from pymtl import *
from arith import *

from TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# Adder unit test
#-------------------------------------------------------------------------

def test_adder( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in0     in1     cin out     cout
    [ 0x0000, 0x0000, 0,  0x0000, 0 ],
    [ 0x0001, 0x0000, 0,  0x0001, 0 ],
    [ 0x0000, 0x0001, 0,  0x0001, 0 ],
    [ 0x0001, 0x0001, 0,  0x0002, 0 ],
    [ 0x0000, 0x0000, 1,  0x0001, 0 ],
    [ 0x0001, 0x0000, 1,  0x0002, 0 ],
    [ 0x0000, 0x0001, 1,  0x0002, 0 ],
    [ 0x0001, 0x0001, 1,  0x0003, 0 ],
    [ 0x000a, 0x0015, 0,  0x001f, 0 ],
    [ 0xfffe, 0x0001, 0,  0xffff, 0 ],
    [ 0xfffe, 0x0001, 1,  0x0000, 1 ],
    [ 0xffff, 0xffff, 1,  0xffff, 1 ]
  ]

  # Instantiate and elaborate the model

  model = Adder(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]
    model.cin.value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.out.value == test_vector[3]
    if test_vector[4] != '?':
      assert model.cout.value == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_adder.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Subtractor unit test
#-------------------------------------------------------------------------

def test_subtractor( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in0     in1     out
    [ 0x0000, 0x0000, 0x0000 ],
    [ 0x0001, 0x0000, 0x0001 ],
    [ 0x0000, 0x0001, 0xffff ],
    [ 0x0001, 0x0001, 0x0000 ],
    [ 0x000a, 0x0004, 0x0006 ],
    [ 0x0141, 0x0079, 0x00c8 ],
    [ 0x0400, 0x0200, 0x0200 ],
    [ 0xffff, 0x0001, 0xfffe ],
    [ 0xffff, 0xffff, 0x0000 ],
    [ 0x0000, 0xffff, 0x0001 ],
    [ 0xfffe, 0xffff, 0xffff ],
  ]

  # Instantiate and elaborate the model

  model = Subtractor(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_subtractor.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Incrementer tests with varying incrementer amounts
#-------------------------------------------------------------------------

def run_test_incrementer( dump_vcd, increment_amount, test_vectors ):

  # Instantiate and elaborate the model

  model = Incrementer( 16, increment_amount )
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
    sim.dump_vcd( "pmlib-arith-test_incrementer_ia" +
                  str(increment_amount) + ".vcd" )
  sim.run_test()

def test_incrementer_ia1( dump_vcd ):
  run_test_incrementer( dump_vcd, 1, [
    # in      out
    [ 0x0000, 0x0001 ],
    [ 0x0001, 0x0002 ],
    [ 0x000a, 0x000b ],
    [ 0x0141, 0x0142 ],
    [ 0x0400, 0x0401 ],
    [ 0xfffe, 0xffff ],
    [ 0xffff, 0x0000 ],
  ])

def test_incrementer_ia123( dump_vcd ):
  run_test_incrementer( dump_vcd, 123, [
    # in      out
    [ 0x0000, 0x007b ],
    [ 0x0001, 0x007c ],
    [ 0x000a, 0x0085 ],
    [ 0x0141, 0x01bc ],
    [ 0x0400, 0x047b ],
    [ 0xfffe, 0x0079 ],
    [ 0xffff, 0x007a ],
  ])

def test_incrementer_ia1024( dump_vcd ):
  run_test_incrementer( dump_vcd, 1024, [
    # in      out
    [ 0x0000, 0x0400 ],
    [ 0x0001, 0x0401 ],
    [ 0x000a, 0x040a ],
    [ 0x0141, 0x0541 ],
    [ 0x0400, 0x0800 ],
    [ 0xfffe, 0x03fe ],
    [ 0xffff, 0x03ff ],
  ])

#-------------------------------------------------------------------------
# ZeroExtender tests with varying bitwidths
#-------------------------------------------------------------------------

def run_test_zero_extender( dump_vcd, in_nbits, out_nbits, test_vectors ):

  # Instantiate and elaborate the model

  model = ZeroExtender( in_nbits, out_nbits )
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
    sim.dump_vcd( "pmlib-arith-test_zero_extender" +
                  "_i" + str(in_nbits) + "_o" + str(out_nbits) + ".vcd" )
  sim.run_test()

def test_zero_extender_i1o4( dump_vcd ):
  run_test_zero_extender( dump_vcd, 1, 4, [
    # in   out
    [ 0x0, 0x0 ],
    [ 0x1, 0x1 ],
  ])

def test_zero_extender_i2o4( dump_vcd ):
  run_test_zero_extender( dump_vcd, 2, 4, [
    # in   out
    [ 0x0, 0x0 ],
    [ 0x1, 0x1 ],
    [ 0x2, 0x2 ],
    [ 0x3, 0x3 ],
  ])

def test_zero_extender_i4o16( dump_vcd ):
  run_test_zero_extender( dump_vcd, 4, 16, [
    # in   out
    [ 0x0, 0x0000 ],
    [ 0x1, 0x0001 ],
    [ 0x2, 0x0002 ],
    [ 0x3, 0x0003 ],
  ])

#-------------------------------------------------------------------------
# SignExtender tests with varying bitwidths
#-------------------------------------------------------------------------

def run_test_sign_extender( dump_vcd, in_nbits, out_nbits, test_vectors ):

  # Instantiate and elaborate the model

  model = SignExtender( in_nbits, out_nbits )
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
    sim.dump_vcd( "pmlib-arith-test_sign_extender" +
                  "_i" + str(in_nbits) + "_o" + str(out_nbits) + ".vcd" )
  sim.run_test()

# def test_sign_extender_i1o4( dump_vcd ):
#   run_test_sign_extender( dump_vcd, 1, 4, [
#     # in   out
#     [ 0x0, 0x0 ],
#     [ 0x1, 0xf ],
#   ])
#
# def test_sign_extender_i2o4( dump_vcd ):
#   run_test_sign_extender( dump_vcd, 2, 4, [
#     # in   out
#     [ 0x0, 0x0 ],
#     [ 0x1, 0x0 ],
#     [ 0x2, 0xe ],
#     [ 0x3, 0xf ],
#   ])
#
# def test_sign_extender_i4o16( dump_vcd ):
#   run_test_sign_extender( dump_vcd, 4, 16, [
#     # in   out
#     [ 0x0, 0x0000 ],
#     [ 0x1, 0x0001 ],
#     [ 0x2, 0xfffe ],
#     [ 0x3, 0xffff ],
#   ])

#-------------------------------------------------------------------------
# EqComparator unit test
#-------------------------------------------------------------------------

def test_EqComparator( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in0     in1     out
    [ 0x0000, 0x0000, 1 ],
    [ 0x0001, 0x0001, 1 ],
    [ 0x000a, 0x000a, 1 ],
    [ 0x007f, 0x007f, 1 ],
    [ 0x0141, 0x0140, 0 ],
    [ 0x0400, 0x0400, 1 ],
    [ 0x7fff, 0x7fff, 1 ],
    [ 0x8000, 0x7fff, 0 ],
    [ 0x8001, 0x8002, 0 ],
    [ 0xffff, 0xffff, 1 ],
  ]

  # Instantiate and elaborate the model

  model = EqComparator(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_EqComparator.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# LtComparator unit test
#-------------------------------------------------------------------------

def test_LtComparator( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in0     in1     out
    [ 0x0000, 0x0000, 0 ],
    [ 0x0001, 0x0001, 0 ],
    [ 0x0000, 0x0001, 1 ],
    [ 0x000a, 0x000a, 0 ],
    [ 0x000b, 0x000a, 0 ],
    [ 0x000b, 0x000c, 1 ],
    [ 0x007f, 0x007f, 0 ],
    [ 0x0141, 0x0140, 0 ],
    [ 0x0400, 0x0400, 0 ],
    [ 0x7fff, 0x7fff, 0 ],
    [ 0x8000, 0x7fff, 0 ],
    [ 0x8001, 0x8002, 1 ],
    [ 0xffff, 0xffff, 0 ],
  ]

  # Instantiate and elaborate the model

  model = LtComparator(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_LtComparator.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# GtComparator unit test
#-------------------------------------------------------------------------

def test_GtComparator( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in0     in1     out
    [ 0x0000, 0x0000, 0 ],
    [ 0x0001, 0x0001, 0 ],
    [ 0x0000, 0x0001, 0 ],
    [ 0x000a, 0x000a, 0 ],
    [ 0x000b, 0x000a, 1 ],
    [ 0x000b, 0x000c, 0 ],
    [ 0x007f, 0x007f, 0 ],
    [ 0x0141, 0x0140, 1 ],
    [ 0x0400, 0x0400, 0 ],
    [ 0x7fff, 0x7fff, 0 ],
    [ 0x8000, 0x7fff, 1 ],
    [ 0x8001, 0x8002, 0 ],
    [ 0xffff, 0xffff, 0 ],
  ]

  # Instantiate and elaborate the model

  model = GtComparator(16)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_GtComparator.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# SignUnit tests with varying bitwidths
#-------------------------------------------------------------------------

def run_test_sign_unit( dump_vcd, nbits, test_vectors ):

  # Instantiate and elaborate the model

  model = SignUnit( nbits )
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
    sim.dump_vcd( "pmlib-arith-test_sign_unit_n" + str(nbits) + ".vcd" )
  sim.run_test()

def test_sign_unit_n4( dump_vcd ):
  run_test_sign_unit( dump_vcd, 4, [
   # in      out
   [ 0b0000, 0b0000 ],
   [ 0b0001, 0b1111 ],
   [ 0b0101, 0b1011 ],
   [ 0b0111, 0b1001 ],
   [ 0b1001, 0b0111 ],
   [ 0b1010, 0b0110 ],
   [ 0b1101, 0b0011 ],
   [ 0b1110, 0b0010 ],
   [ 0b1111, 0b0001 ],
  ])

def test_sign_unit_n7( dump_vcd ):
  run_test_sign_unit( dump_vcd, 7, [
   # in         out
   [ 0b0000000, 0b0000000 ],
   [ 0b0000001, 0b1111111 ],
   [ 0b0000101, 0b1111011 ],
   [ 0b0000111, 0b1111001 ],
   [ 0b1111001, 0b0000111 ],
   [ 0b1111010, 0b0000110 ],
   [ 0b1101101, 0b0010011 ],
   [ 0b1001110, 0b0110010 ],
   [ 0b1001111, 0b0110001 ],
  ])

#-------------------------------------------------------------------------
# UnsignUnit tests with varying bitwidths
#-------------------------------------------------------------------------

def run_test_unsign_unit( dump_vcd, nbits, test_vectors ):

  # Instantiate and elaborate the model

  model = UnsignUnit( nbits )
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
    sim.dump_vcd( "pmlib-arith-test_unsign_unit_n" + str(nbits) + ".vcd" )
  sim.run_test()

def test_unsign_unit_n4( dump_vcd ):
  run_test_unsign_unit( dump_vcd, 4, [
    # in      out
    [ 0b0000, 0b0000,],
    [ 0b0001, 0b0001,],
    [ 0b0101, 0b0101,],
    [ 0b0111, 0b0111,],
    [ 0b1001, 0b0111,],
    [ 0b1010, 0b0110,],
    [ 0b1101, 0b0011,],
    [ 0b1110, 0b0010,],
    [ 0b1111, 0b0001,],
  ])

def test_unsign_unit_n7( dump_vcd ):
  run_test_unsign_unit( dump_vcd, 7, [
    # in     out
    [ 0b0000000, 0b0000000 ],
    [ 0b0000001, 0b0000001 ],
    [ 0b0000101, 0b0000101 ],
    [ 0b0000111, 0b0000111 ],
    [ 0b1111001, 0b0000111 ],
    [ 0b1111010, 0b0000110 ],
    [ 0b1101101, 0b0010011 ],
    [ 0b0000101, 0b0000101 ],
    [ 0b1001110, 0b0110010 ],
    [ 0b1001111, 0b0110001 ],
  ])

#-------------------------------------------------------------------------
# LeftLogicalShifter unit test
#-------------------------------------------------------------------------

def test_LeftLogicalShifter( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in        shamnt  out
    [ 0b000001, 1, 0b000010 ],
    [ 0b000000, 0, 0b000000 ],
    [ 0b000001, 0, 0b000001 ],
    [ 0b000001, 2, 0b000100 ],
    [ 0b000001, 3, 0b001000 ],
    [ 0b000001, 4, 0b010000 ],
    [ 0b101010, 1, 0b010100 ],
    [ 0b101010, 2, 0b101000 ],
    [ 0b111111, 3, 0b111000 ],
    [ 0b111111, 6, 0b000000 ],
  ]

  # Instantiate and elaborate the model

  model = LeftLogicalShifter(6,3)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value   = test_vector[0]
    model.shamt.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_LeftLogicShifter.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# RightLogicalShifter unit test
#-------------------------------------------------------------------------

def test_RightLogicalShifter( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in        shamnt  out
    [ 0b100000, 1, 0b010000 ],
    [ 0b000000, 0, 0b000000 ],
    [ 0b100000, 0, 0b100000 ],
    [ 0b100000, 2, 0b001000 ],
    [ 0b100000, 3, 0b000100 ],
    [ 0b100000, 4, 0b000010 ],
    [ 0b101010, 1, 0b010101 ],
    [ 0b101010, 2, 0b001010 ],
    [ 0b111111, 3, 0b000111 ],
    [ 0b111111, 6, 0b000000 ],
  ]

  # Instantiate and elaborate the model

  model = RightLogicalShifter(6,3)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value   = test_vector[0]
    model.shamt.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-arith-test_RightLogicShifter.vcd" )
  sim.run_test()

