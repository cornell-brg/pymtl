#=======================================================================
# DecodeInstType_test.py
#=======================================================================

from new_pymtl      import *
from new_pmlib      import TestVectorSimulator
from DecodeInstType import DecodeInstType, DecodeException

import ParcISA

#-----------------------------------------------------------------------
# Test Instruction Type Decoder
#-----------------------------------------------------------------------

def test_decode( dump_vcd, test_verilog ):

  # Test vectors

  test_vectors = [
    # Bits                                Instruction
    [ 0b00000000000000000000000000000000, ParcISA.NOP    ],
    [ 0b00100100000000000000000000000000, ParcISA.ADDIU  ],
    [ 0b00110100000000000000000000000000, ParcISA.ORI    ],
    [ 0b00111100000000000000000000000000, ParcISA.LUI    ],
    [ 0b00000000000000000000000000100001, ParcISA.ADDU   ],
    [ 0b10001100000000000000000000000000, ParcISA.LW     ],
    [ 0b10101100000000000000000000000000, ParcISA.SW     ],
    [ 0b00001100000000000000000000000000, ParcISA.JAL    ],
    [ 0b00000000000000000000000000001000, ParcISA.JR     ],
    [ 0b00010100000000000000000000000000, ParcISA.BNE    ],
    [ 0b01000000100000000000000000000000, ParcISA.MTC0   ],
    [ 0b00110000000000000000000000000000, ParcISA.ANDI   ],
    [ 0b00111000000000000000000000000000, ParcISA.XORI   ],
    [ 0b00101000000000000000000000000000, ParcISA.SLTI   ],
    [ 0b00101100000000000000000000000000, ParcISA.SLTIU  ],
    [ 0b00000000000111110000000000000000, ParcISA.SLL    ],
    [ 0b00000000000000000000000000000010, ParcISA.SRL    ],
    [ 0b00000000000000000000000000000011, ParcISA.SRA    ],
    [ 0b00000000000000000000000000000100, ParcISA.SLLV   ],
    [ 0b00000000000000000000000000000110, ParcISA.SRLV   ],
    [ 0b00000000000000000000000000000111, ParcISA.SRAV   ],
    [ 0b00000000000000000000000000100011, ParcISA.SUBU   ],
    [ 0b00000000000000000000000000100100, ParcISA.AND    ],
    [ 0b00000000000000000000000000100101, ParcISA.OR     ],
    [ 0b00000000000000000000000000100110, ParcISA.XOR    ],
    [ 0b00000000000000000000000000100111, ParcISA.NOR    ],
    [ 0b00000000000000000000000000101010, ParcISA.SLT    ],
    [ 0b00000000000000000000000000101011, ParcISA.SLTU   ],
    [ 0b01110000000000000000000000000010, ParcISA.MUL    ],
    [ 0b10011100000000000000000000000101, ParcISA.DIV    ],
    [ 0b10011100000000000000000000000111, ParcISA.DIVU   ],
    [ 0b10011100000000000000000000000110, ParcISA.REM    ],
    [ 0b10011100000000000000000000001000, ParcISA.REMU   ],
    [ 0b10000100000000000000000000000000, ParcISA.LH     ],
    [ 0b10010100000000000000000000000000, ParcISA.LHU    ],
    [ 0b10000000000000000000000000000000, ParcISA.LB     ],
    [ 0b10010000000000000000000000000000, ParcISA.LBU    ],
    [ 0b10100100000000000000000000000000, ParcISA.SH     ],
    [ 0b10100000000000000000000000000000, ParcISA.SB     ],
    [ 0b00001000000000000000000000000000, ParcISA.J      ],
    [ 0b00001100000000000000000000000000, ParcISA.JAL    ],
    [ 0b00000000000000000000000000001001, ParcISA.JALR   ],
    [ 0b00010000000000000000000000000000, ParcISA.BEQ    ],
    [ 0b00011000000000000000000000000000, ParcISA.BLEZ   ],
    [ 0b00011100000000000000000000000000, ParcISA.BGTZ   ],
    [ 0b00000100000000000000000000000000, ParcISA.BLTZ   ],
    [ 0b00000100000000010000000000000000, ParcISA.BGEZ   ],
    [ 0b01000000000000000000000000000000, ParcISA.MFC0   ],
  ]

  # Instantiate and elaborate the model

  model = DecodeInstType()
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    #if test_vector[3] != '?':
    assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "plab2-test_DecodeInstType.vcd" )
  sim.run_test()


#-----------------------------------------------------------------------
# Test Decode Exception
#-----------------------------------------------------------------------

import pytest
def test_decode_exception( dump_vcd ):
  with pytest.raises( DecodeException ):

    # Test vectors
    test_vectors = [
      # Bits                                Instruction
      [ 0b00111100000000000000000000000000, ParcISA.LUI    ],
      [ 0b00000000000000000000000000100001, ParcISA.ADDU   ],
      [ 0b10001100000000000000000000000000, ParcISA.LW     ],
      [ 0b11010100000000000000000000000000, ParcISA.BNE    ],
    ]

    # Instantiate and elaborate the model
    model = DecodeInstType()
    model.elaborate()

    # Define functions mapping the test vector to ports in model

    def tv_in( model, test_vector ):
      model.in_.value = test_vector[0]

    def tv_out( model, test_vector ):
      assert model.out.value == test_vector[1]

    # Run the test

    sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
    sim.run_test()
