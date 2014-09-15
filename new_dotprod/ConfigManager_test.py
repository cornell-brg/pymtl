#==============================================================================
# ConfigManger_test.py
#==============================================================================

from new_pymtl import *
from new_pmlib import TestVectorSimulator

from ConfigManager import ConfigManager

#------------------------------------------------------------------------------
# test_ConfigManager
#------------------------------------------------------------------------------
def test_ConfigManager( dump_vcd, test_verilog ):

  addr_nbits = 5
  data_nbits = 32
  dec_sel_sz = 3
  dec_out_sz = 5

  # Define test input and output functions

  def tv_in( model, test_vector ):
    model.proc2asla.val.value              = test_vector[0]
    model.proc2asla.msg[data_nbits:].value = test_vector[1]
    model.proc2asla.msg[:data_nbits].value = test_vector[2]
    model.is_asla_done.value               = test_vector[3]

  def tv_out( model, test_vector ):
    assert   model.proc2asla.rdy  == test_vector[4]
    if test_vector[5] != '?':
      assert model.cfg_data       == test_vector[5]
    assert   model.asla_go        == test_vector[6]
    assert   model.cfg_reg_wen[1] == test_vector[7]
    assert   model.cfg_reg_wen[2] == test_vector[8]
    assert   model.cfg_reg_wen[3] == test_vector[9]
    assert   model.cfg_reg_wen[4] == test_vector[10]

  # Select and elaborate the model under test

  model = ConfigManager( addr_nbits, data_nbits, dec_sel_sz, dec_out_sz )
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define the test vectors
  test_vectors = [
    # Inputs----------------------  Outputs------------------------------------
    # p2a p2a  p2a         is_alsa  p2a  cfg         asla  base  base  base len
    # val addr data        done     rdy  data        go    a_en  b_en  c_en en
    [ 0,  1,   0x20000000, 0,       1,   0x20000000, 0,    0,    0,    0,   0 ],
    [ 1,  1,   0x20000000, 0,       1,   0x20000000, 0,    1,    0,    0,   0 ],
    [ 1,  2,   0x40000000, 0,       1,   0x40000000, 0,    0,    1,    0,   0 ],
    [ 1,  3,   0x80000000, 0,       1,   0x80000000, 0,    0,    0,    1,   0 ],
    [ 1,  4,   0x00000064, 0,       1,   0x00000064, 0,    0,    0,    0,   1 ],

    # TODO: this is different from Verilog test, okay?
    #[ 1,  0,   0x00000001, 0,       1,   0x00000001, 1,    0,    0,    0,   0 ],
    [ 1,  0,   0x00000001, 0,       1,   0x00000001, 0,    0,    0,    0,   0 ],

    [ 0,  0,   0x00000001, 0,       0,          '?', 1,    0,    0,    0,   0 ],
    [ 0,  0,   0x00000001, 0,       0,          '?', 1,    0,    0,    0,   0 ],

    # TODO: this is different from Verilog test, okay?
    #[ 0,  0,   0x00000001, 1,       1,          '?', 0,    0,    0,    0,   0 ],
    [ 0,  0,   0x00000001, 1,       0,          '?', 1,    0,    0,    0,   0 ],
    [ 0,  0,   0x00000001, 0,       1,          '?', 0,    0,    0,    0,   0 ],
  ]

  # Create the simulator and configure it
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "decoder.vcd" )

  # Run the simulator
  sim.run_test()

