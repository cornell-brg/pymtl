#=======================================================================
# SRAMs_test.py
#=======================================================================
# Unit Tests for SRAM collections

from pymtl      import *
from pclib.test import TestVectorSimulator

from SRAMs import (
  SRAMBitsComb_rst_1rw,
  SRAMBytesComb_rst_1rw,
  SRAMBitsSync_rst_1rw,
  SRAMBytesSync_rst_1rw,
)

#-----------------------------------------------------------------------
# SRAMBitsComb_rst_1rw
#-----------------------------------------------------------------------
def test_SRAMBitsComb_rst_1rw( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [

    #  wen, addr, wdata,    rdata
    [    0,    0, 0x000000, 0xa0a0a0 ],
    [    1,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0x000000 ],
    [    1,    0, 0xadbeef, '?'      ],
    [    0,    0, 0x000000, 0xadbeef ],
    [    1,    0, 0xcdefab, '?'      ],
    [    0,    0, 0x000000, 0xcdefab ],
    [    1,    0, 0x112233, '?'      ],
    [    0,    0, 0x000000, 0x112233 ],
    [    1,    0, 0xadbeef, '?'      ],
    [    0,    0, 0x000000, 0xadbeef ],
    [    1,    0, 0xffffff, '?'      ],
    [    0,    0, 0x000000, 0xffffff ],
    [    1,   12, 0xadbeef, '?'      ],
    [    0,   12, 0xbbcccc, 0xadbeef ],
  ]

  # Instantiate and elaborate the model

  model = SRAMBitsComb_rst_1rw( 16, 26, reset_value = 0xa0a0a0 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.wen.value   = test_vector[0]
    model.addr.value  = test_vector[1]
    model.wdata.value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.rdata.value == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# SRAMBytesComb_rst_1rw
#-----------------------------------------------------------------------
def test_SRAMBytesComb_rst_1rw( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [

    #  wen,  wben,    addr, wdata,      rdata
    [    0,  0b0000,     0, 0x00000000, 0xa0a0a0a0 ],
    [    1,  0b1111,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x00000000 ],
    [    1,  0b0001,     0, 0xdeadbeef, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x000000ef ],
    [    1,  0b0110,     0, 0xabcdefab, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x00cdefef ],
    [    1,  0b1011,     0, 0xff000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xffcd0000 ],
    [    1,  0b1111,     0, 0xdeadbeef, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xdeadbeef ],
    [    1,  0b1111,     0, 0xffffffff, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xffffffff ],
    [    1,  0b1111,    12, 0xdeadbeef, '?'        ],
    [    0,  0b1111,    12, 0xbbbbcccc, 0xdeadbeef ],
  ]

  # Instantiate and elaborate the model

  model = SRAMBytesComb_rst_1rw( 16, 4, reset_value = 0xa0a0a0a0 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.wen.value   = test_vector[0]
    model.wben.value  = test_vector[1]
    model.addr.value  = test_vector[2]
    model.wdata.value = test_vector[3]

  def tv_out( model, test_vector ):
    if test_vector[4] != '?':
      assert model.rdata.value == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# SRAMBitsSync_rst_1rw
#-----------------------------------------------------------------------
def test_SRAMBitsSync_rst_1rw( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [

    #  wen, addr, wdata,    rdata
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0xa0a0a0 ],
    [    1,    0, 0x000000, 0xa0a0a0 ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0x000000 ],
    [    1,    0, 0xadbeef, 0x000000 ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0xadbeef ],
    [    1,    0, 0xcdefab, 0xadbeef ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0xcdefab ],
    [    1,    0, 0x112233, 0xcdefab ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0x112233 ],
    [    1,    0, 0xadbeef, 0x112233 ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0xadbeef ],
    [    1,    0, 0xffffff, 0xadbeef ],
    [    0,    0, 0x000000, '?'      ],
    [    0,    0, 0x000000, 0xffffff ],
    [    0,   12, 0x000000, 0xffffff ],
    [    1,   12, 0xadbeef, 0xa0a0a0 ],
    [    0,   12, 0xbbcccc, '?'      ],
    [    0,   12, 0x000000, 0xadbeef ],
  ]

  # Instantiate and elaborate the model

  model = SRAMBitsSync_rst_1rw( 16, 26, reset_value = 0xa0a0a0 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.wen.value   = test_vector[0]
    model.addr.value  = test_vector[1]
    model.wdata.value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.rdata.value == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# SRAMBytesSync_rst_1rw
#-----------------------------------------------------------------------
def test_SRAMBytesSync_rst_1rw( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [

    #  wen,  wben,    addr, wdata,      rdata
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xa0a0a0a0 ],
    [    1,  0b1111,     0, 0x00000000, 0xa0a0a0a0 ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x00000000 ],
    [    1,  0b0001,     0, 0xdeadbeef, 0x00000000 ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x000000ef ],
    [    1,  0b0110,     0, 0xabcdefab, 0x000000ef ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0x00cdefef ],
    [    1,  0b1011,     0, 0xff000000, 0x00cdefef ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xffcd0000 ],
    [    1,  0b1111,     0, 0xdeadbeef, 0xffcd0000 ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xdeadbeef ],
    [    1,  0b1111,     0, 0xffffffff, 0xdeadbeef ],
    [    0,  0b0000,     0, 0x00000000, '?'        ],
    [    0,  0b0000,     0, 0x00000000, 0xffffffff ],
    [    0,  0b0000,    12, 0x00000000, 0xffffffff ],
    [    1,  0b1111,    12, 0xdeadbeef, 0xa0a0a0a0 ],
    [    0,  0b1111,    12, 0xbbbbcccc, '?'        ],
    [    0,  0b0000,    12, 0x00000000, 0xdeadbeef ],
  ]

  # Instantiate and elaborate the model

  model = SRAMBytesSync_rst_1rw( 16, 4, reset_value = 0xa0a0a0a0 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.wen.value   = test_vector[0]
    model.wben.value  = test_vector[1]
    model.addr.value  = test_vector[2]
    model.wdata.value = test_vector[3]

  def tv_out( model, test_vector ):
    if test_vector[4] != '?':
      assert model.rdata.value == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
