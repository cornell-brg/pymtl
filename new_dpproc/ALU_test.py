#=========================================================================
# ALU Test
#=========================================================================

from pymtl import *
import new_pmlib

import ALU
#from ALU import ALU

def test_alu( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [
    # func   in0         in1         out
    # ADD
    [ ALU.ADD,  0x00000000, 0x00000000, 0x00000000 ],
    [ ALU.ADD,  0x00000001, 0x00000001, 0x00000002 ],
    [ ALU.ADD,  0x00000003, 0x00000007, 0x0000000a ],
    [ ALU.ADD,  0x00000000, 0xffff8000, 0xffff8000 ],
    [ ALU.ADD,  0x80000000, 0x00000000, 0x80000000 ],
    [ ALU.ADD,  0x80000000, 0xffff8000, 0x7fff8000 ],
    [ ALU.ADD,  0x00000000, 0x00007fff, 0x00007fff ],
    [ ALU.ADD,  0x7fffffff, 0x00000000, 0x7fffffff ],
    [ ALU.ADD,  0x7fffffff, 0x00007fff, 0x80007ffe ],
    [ ALU.ADD,  0x80000000, 0x00007fff, 0x80007fff ],
    [ ALU.ADD,  0x7fffffff, 0xffff8000, 0x7fff7fff ],
    [ ALU.ADD,  0x00000000, 0xffffffff, 0xffffffff ],
    [ ALU.ADD,  0xffffffff, 0x00000001, 0x00000000 ],
    [ ALU.ADD,  0xffffffff, 0xffffffff, 0xfffffffe ],
    # SUB
    [ ALU.SUB,  0x00000000, 0x00000000, 0x00000000 ],
    [ ALU.SUB,  0x00000001, 0x00000001, 0x00000000 ],
    [ ALU.SUB,  0x00000003, 0x00000007, 0xfffffffc ],
    [ ALU.SUB,  0x00000000, 0xffff8000, 0x00008000 ],
    [ ALU.SUB,  0x80000000, 0x00000000, 0x80000000 ],
    [ ALU.SUB,  0x80000000, 0xffff8000, 0x80008000 ],
    [ ALU.SUB,  0x00000000, 0x00007fff, 0xffff8001 ],
    [ ALU.SUB,  0x7fffffff, 0x00000000, 0x7fffffff ],
    [ ALU.SUB,  0x7fffffff, 0x00007fff, 0x7fff8000 ],
    [ ALU.SUB,  0x80000000, 0x00007fff, 0x7fff8001 ],
    [ ALU.SUB,  0x7fffffff, 0xffff8000, 0x80007fff ],
    [ ALU.SUB,  0x00000000, 0xffffffff, 0x00000001 ],
    [ ALU.SUB,  0xffffffff, 0x00000001, 0xfffffffe ],
    [ ALU.SUB,  0xffffffff, 0xffffffff, 0x00000000 ],
    # OR
    [ ALU.OR,   0xff00ff00, 0x0f0f0f0f, 0xff0fff0f ],
    [ ALU.OR,   0x0ff00ff0, 0xf0f0f0f0, 0xfff0fff0 ],
    [ ALU.OR,   0x00ff00ff, 0x0f0f0f0f, 0x0fff0fff ],
    [ ALU.OR,   0xf00ff00f, 0xf0f0f0f0, 0xf0fff0ff ],
    # SLL
    [ ALU.SLL,           0, 0x00000001, 0x00000001 ],
    [ ALU.SLL,           1, 0x00000001, 0x00000002 ],
    [ ALU.SLL,           7, 0x00000001, 0x00000080 ],
    [ ALU.SLL,          14, 0x00000001, 0x00004000 ],
    [ ALU.SLL,          31, 0x00000001, 0x80000000 ],
    [ ALU.SLL,           0, 0xffffffff, 0xffffffff ],
    [ ALU.SLL,           1, 0xffffffff, 0xfffffffe ],
    [ ALU.SLL,           7, 0xffffffff, 0xffffff80 ],
    [ ALU.SLL,          14, 0xffffffff, 0xffffc000 ],
    [ ALU.SLL,          31, 0xffffffff, 0x80000000 ],
    [ ALU.SLL,           0, 0x21212121, 0x21212121 ],
    [ ALU.SLL,           1, 0x21212121, 0x42424242 ],
    [ ALU.SLL,           7, 0x21212121, 0x90909080 ],
    [ ALU.SLL,          14, 0x21212121, 0x48484000 ],
    [ ALU.SLL,          31, 0x21212121, 0x80000000 ],
  ]

  # Instantiate and elaborate the model

  model = ALU.ALU( 32 )
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.sel.value = test_vector[0]
    model.in0.value = test_vector[1]
    model.in1.value = test_vector[2]

  def tv_out( model, test_vector ):
    #if test_vector[3] != '?':
    assert model.out.value == test_vector[3]

  # Run the test

  sim = new_pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "plab2-test_alu_add.vcd" )
  sim.run_test()



