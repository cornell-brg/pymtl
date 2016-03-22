#=========================================================================
# RegisterFile_test.py
#=========================================================================

from pymtl        import *
from pclib.test   import TestVectorSimulator
from RegisterFile import RegisterFile

#-------------------------------------------------------------------------
# Test 1R1W Register File
#-------------------------------------------------------------------------

def test_regfile_1R1W( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [
    # rd_addr0  rd_data0  wr_en  wr_addr  wr_data
    [       0,   '?',        0,       0,   0x0000 ],
    [       1,   '?',        0,       1,   0x0008 ],
    # Write followed by Read
    [       3,   '?',        1,       2,   0x0005 ],
    [       2,   0x0005,     0,       2,   0x0000 ],
    # Simultaneous Write and Read
    [       3,   '?',        1,       3,   0x0007 ],
    [       3,   0x0007,     1,       7,   0x0090 ],
    [       7,   0x0090,     1,       3,   0x0007 ],
    # Write to zero
    [       0,   '?',        1,       0,   0x0FFF ],
    [       0,   0x0FFF,     1,       4,   0x0FFF ],
    [       0,   0x0FFF,     0,       4,   0x0BBB ],
    [       0,   0x0FFF,     0,       4,   0x0FFF ],
    [       4,   0x0FFF,     0,       0,   0x0000 ],
  ]

  # Instantiate and elaborate the model

  model = RegisterFile( dtype = 16, nregs = 8, rd_ports = 1 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model, verilator_xinit=test_verilog )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.rd_addr[0].value = test_vector[0]
    model.wr_en.value      = test_vector[2]
    model.wr_addr.value    = test_vector[3]
    model.wr_data.value    = test_vector[4]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.rd_data[0].value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# Test 2R2W Register File
#-------------------------------------------------------------------------

def test_regfile_2R2W( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [
    # ---read 0---  ---read 1---  -----write 0-----  -----write 1-----
    # addr    data  addr    data  en  addr     data  en  addr     data
    [   10, '?',      14, '?',     0,   10,  0x0000,  0,   10,  0x0000],
    [   13, '?',      14, '?',     1,   14,  0x0005,  0,   14,  0x0005],
    [   12, '?',      14, 0x0005,  0,   10,  0x0006,  1,   12,  0x0006],
    [   12, 0x0006,   12, 0x0006,  0,   13,  0x0008,  1,   13,  0x0009],
    [   12, 0x0006,   12, 0x0006,  0,   13,  0x0007,  0,   13,  0x000a],
    [   17, '?',      13, 0x0009,  0,   17,  0x0090,  1,   17,  0x0010],
    [   14, 0x0005,   17, 0x0010,  0,   17,  0x0090,  0,   17,  0x0020],
    [   16, '?',      17, 0x0010,  1,   17,  0x0090,  1,   16,  0x0090],
    [   16, 0x0090,   17, 0x0090,  1,   17,  0x0011,  0,   16,  0x0011],
    [   16, 0x0090,   17, 0x0011,  0,   10,  0x0000,  0,   10,  0x0000],
  ]

  # Instantiate and elaborate the model

  model = RegisterFile( dtype=16, nregs=32, rd_ports=2, wr_ports=2 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model, verilator_xinit=test_verilog )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.rd_addr[0].value = test_vector[0]
    model.rd_addr[1].value = test_vector[2]
    model.wr_en  [0].value = test_vector[4]
    model.wr_addr[0].value = test_vector[5]
    model.wr_data[0].value = test_vector[6]
    model.wr_en  [1].value = test_vector[7]
    model.wr_addr[1].value = test_vector[8]
    model.wr_data[1].value = test_vector[9]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.rd_data[0].value == test_vector[1]
    if test_vector[3] != '?':
      assert model.rd_data[1].value == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

