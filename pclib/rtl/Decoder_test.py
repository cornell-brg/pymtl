#==============================================================================
# Decoder_test.py
#==============================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator
from Decoder    import Decoder

#------------------------------------------------------------------------------
# run_decoder_test
#------------------------------------------------------------------------------
def run_decoder_test( dump_vcd, test_verilog, model, test_vectors ):

  # Define test input and output functions

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.out == test_vector[1]

  # Select and elaborate the model under test

  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Create the simulator and configure it

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )

  # Run the simulator

  sim.run_test()

#------------------------------------------------------------------------------
# test_decoder_2_4
#------------------------------------------------------------------------------
def test_decoder_2_4( dump_vcd, test_verilog ):
  run_decoder_test( dump_vcd, test_verilog, Decoder(2, 4), [
    [ 0, 0b0001 ],
    [ 1, 0b0010 ],
    [ 2, 0b0100 ],
    [ 3, 0b1000 ],
    # TODO: add support for testing x conditions
    #[ 0b0x, 0b00xx ],
    #[ 0b1x, 0bxx00 ],
    #[ 0bx0, 0b0x0x ],
    #[ 0bx1, 0bx0x0 ],
    #[ 0bxx, 0bxxxx ],
  ])

#------------------------------------------------------------------------------
# test_decoder_2_3
#------------------------------------------------------------------------------
def test_decoder_2_3( dump_vcd, test_verilog ):
  run_decoder_test( dump_vcd, test_verilog, Decoder(2, 3), [
    [ 0, 0b001 ],
    [ 1, 0b010 ],
    [ 2, 0b100 ],
    [ 3, 0b000 ],
    # TODO: add support for testing x conditions
    #[ 0b0x, 0b0xx ],
    #[ 0b1x, 0bx00 ],
    #[ 0bx0, 0bx0x ],
    #[ 0bx1, 0b0x0 ],
    #[ 0bxx, 0bxxx ],
  ])
