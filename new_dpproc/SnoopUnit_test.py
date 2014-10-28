#=======================================================================
# SnoopUnit_test
#=======================================================================

from pymtl import *
from new_pmlib import TestVectorSimulator
from SnoopUnit import SnoopUnit

#-----------------------------------------------------------------------
# test_drop_unit_tv
#-----------------------------------------------------------------------
def test_drop_unit_tv( dump_vcd, test_verilog ):

  test_vectors = [

    # drop in_val in_rdy in_msg  out_val out_rdy out_msg
    [ 0,   0,     0,     0x0001, 0,      0,      0x0001 ],
    [ 0,   0,     1,     0x0001, 0,      1,      0x0001 ],
    [ 0,   1,     0,     0x0001, 1,      0,      0x0001 ],
    [ 0,   1,     1,     0x0001, 1,      1,      0x0001 ],
    [ 1,   0,     0,     0x0001, 0,      0,      0x0001 ],
    [ 0,   1,     1,     0x0001, 0,      1,      0x0001 ],
    [ 1,   1,     1,     0x0001, 0,      1,      0x0001 ],
    [ 1,   0,     1,     0x0001, 0,      1,      0x0001 ],
    [ 0,   1,     1,     0x0001, 0,      1,      0x0001 ],

  ]

  # Instantiate and elaborate the model

  model = SnoopUnit( nbits=16 )
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.drop.value     = test_vector[0]
    model.in_.val.value  = test_vector[1]
    model.in_.msg.value  = test_vector[3]
    model.out.rdy.value  = test_vector[5]

  def tv_out( model, test_vector ):

    assert model.in_.rdy.value  == test_vector[2]
    assert model.out.val.value  == test_vector[4]
    assert model.out.msg.value  == test_vector[6]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "SnoopUnit_tv.vcd" )
  sim.run_test()
