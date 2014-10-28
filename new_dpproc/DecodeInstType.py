#=======================================================================
# DecodeInstType
#=======================================================================
# Parc Instruction Type Decoder

from pymtl import *

import ParcISA as isa

#-----------------------------------------------------------------------
# DecodeInstType
#-----------------------------------------------------------------------
# Parc Instruction Type Decoder
class DecodeInstType( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    s.in_ = InPort ( 32 )
    s.out = OutPort(  8 )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    @s.combinational
    def comb_logic():
      if     s.in_            == 0:        s.out.value = isa.NOP
      elif   s.in_[ isa.OP ]  == 0b001001: s.out.value = isa.ADDIU
      elif   s.in_[ isa.OP ]  == 0b001101: s.out.value = isa.ORI
      elif   s.in_[ isa.OP ]  == 0b001111: s.out.value = isa.LUI
      elif   s.in_[ isa.OP ]  == 0b100011: s.out.value = isa.LW
      elif   s.in_[ isa.OP ]  == 0b101011: s.out.value = isa.SW
      elif   s.in_[ isa.OP ]  == 0b000011: s.out.value = isa.JAL
      elif   s.in_[ isa.OP ]  == 0b000101: s.out.value = isa.BNE
      elif   s.in_[ isa.OP ]  == 0b010000:
        if   s.in_[ isa.RS ]  == 0b00100:  s.out.value = isa.MTC0
        elif s.in_[ isa.RS ]  == 0b00000:  s.out.value = isa.MFC0
        else: raise DecodeException( s.in_ )
      elif   s.in_[ isa.OP ]  == 0b010010:
        if   s.in_[ isa.RS ]  == 0b00100:  s.out.value = isa.MTC2
        elif s.in_[ isa.RS ]  == 0b00000:  s.out.value = isa.MFC2
        else: raise DecodeException( s.in_ )
      elif   s.in_[ isa.OP ]     == 0b000000:
        if   s.in_[ isa.FUNC ] == 0b100001: s.out.value = isa.ADDU
        elif s.in_[ isa.FUNC ] == 0b001000: s.out.value = isa.JR
        elif s.in_[ isa.FUNC ] == 0b000000: s.out.value = isa.SLL
        elif s.in_[ isa.FUNC ] == 0b000010: s.out.value = isa.SRL
        elif s.in_[ isa.FUNC ] == 0b000011: s.out.value = isa.SRA
        elif s.in_[ isa.FUNC ] == 0b000100: s.out.value = isa.SLLV
        elif s.in_[ isa.FUNC ] == 0b000110: s.out.value = isa.SRLV
        elif s.in_[ isa.FUNC ] == 0b000111: s.out.value = isa.SRAV
        elif s.in_[ isa.FUNC ] == 0b100011: s.out.value = isa.SUBU
        elif s.in_[ isa.FUNC ] == 0b100100: s.out.value = isa.AND
        elif s.in_[ isa.FUNC ] == 0b100101: s.out.value = isa.OR
        elif s.in_[ isa.FUNC ] == 0b100110: s.out.value = isa.XOR
        elif s.in_[ isa.FUNC ] == 0b100111: s.out.value = isa.NOR
        elif s.in_[ isa.FUNC ] == 0b101010: s.out.value = isa.SLT
        elif s.in_[ isa.FUNC ] == 0b101011: s.out.value = isa.SLTU
        elif s.in_[ isa.FUNC ] == 0b001001: s.out.value = isa.JALR
        else: raise DecodeException( s.in_ )
      elif   s.in_[ isa.OP ]   == 0b001100: s.out.value = isa.ANDI
      elif   s.in_[ isa.OP ]   == 0b001110: s.out.value = isa.XORI
      elif   s.in_[ isa.OP ]   == 0b001010: s.out.value = isa.SLTI
      elif   s.in_[ isa.OP ]   == 0b001011: s.out.value = isa.SLTIU
      elif   s.in_[ isa.OP ]   == 0b011100: s.out.value = isa.MUL
      elif   s.in_[ isa.OP ]   == 0b100111:
        if   s.in_[ isa.FUNC ] == 0b000101: s.out.value = isa.DIV
        elif s.in_[ isa.FUNC ] == 0b000111: s.out.value = isa.DIVU
        elif s.in_[ isa.FUNC ] == 0b000110: s.out.value = isa.REM
        elif s.in_[ isa.FUNC ] == 0b001000: s.out.value = isa.REMU
        else: raise DecodeException( s.in_ )
      elif   s.in_[ isa.OP ] == 0b100001:   s.out.value = isa.LH
      elif   s.in_[ isa.OP ] == 0b100101:   s.out.value = isa.LHU
      elif   s.in_[ isa.OP ] == 0b100000:   s.out.value = isa.LB
      elif   s.in_[ isa.OP ] == 0b100100:   s.out.value = isa.LBU
      elif   s.in_[ isa.OP ] == 0b101001:   s.out.value = isa.SH
      elif   s.in_[ isa.OP ] == 0b101000:   s.out.value = isa.SB
      elif   s.in_[ isa.OP ] == 0b000010:   s.out.value = isa.J
      elif   s.in_[ isa.OP ] == 0b000011:   s.out.value = isa.JAL
      elif   s.in_[ isa.OP ] == 0b000100:   s.out.value = isa.BEQ
      elif   s.in_[ isa.OP ] == 0b000110:   s.out.value = isa.BLEZ
      elif   s.in_[ isa.OP ] == 0b000111:   s.out.value = isa.BGTZ
      elif   s.in_[ isa.OP ] == 0b000001:
        if   s.in_[isa.RT] == 0b00000:      s.out.value = isa.BLTZ
        elif s.in_[isa.RT] == 0b00001:      s.out.value = isa.BGEZ
        else: raise DecodeException( s.in_ )
      else:   raise DecodeException( s.in_ )

#-------------------------------------------------------------------------
# DecodeException
#-------------------------------------------------------------------------
class DecodeException( Exception ):
  def __init__( self, inst ):
    msg = "Unknown opcode encountered: " +  inst_bits( inst )
    Exception.__init__(self, msg)


#-------------------------------------------------------------------------
# inst_bits
#-------------------------------------------------------------------------
def inst_bits( inst ):
  x = "{:032b}".format( inst.uint() )
  return "0b{}_{}_{}_{}_{}_{}".format(
            x[0:6], x[6:11], x[11:16], x[16:21], x[21:26], x[26:32]
          )

