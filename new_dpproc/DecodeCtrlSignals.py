#=========================================================================
# ParcV1 Control Signal Decoder
#=========================================================================

from new_pymtl import *

import ParcISA as isa

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

X        = 0

ALU_ADD  =  0
ALU_SUB  =  1
ALU_OR   =  2
ALU_SLL  =  3
ALU_SLT  =  4
ALU_SLTU =  5
ALU_AND  =  6
ALU_XOR  =  7
ALU_NOR  =  8
ALU_SRL  =  9
ALU_SRA  = 10

RD0_RF   = 0
RD0_16   = 1

RD1_RF   = 0
RD1_ZEXT = 1
RD1_SEXT = 2

WR_ALU   = 0
WR_MEM   = 1
WR_PC4   = 2

MEM_LW   = 0
MEM_SW   = 1

PC_PC4   = 0
PC_BR    = 1
PC_JAL   = 2
PC_JR    = 3

#-------------------------------------------------------------------------
# Control Signal Decoder
#-------------------------------------------------------------------------

class DecodeCtrlSignals( Model ):

  def __init__( s ):

    s.inst_bits     = InPort( 32 )
    s.inst_type     = InPort(  8 )
    # Register File
    s.rd_addr0      = OutPort( 5 )
    s.rd_addr1      = OutPort( 5 )
    s.rf_wen        = OutPort( 1 )
    s.rf_waddr      = OutPort( 5 )
    # ALU
    s.alu_fn        = OutPort( 4 )
    # Muxes
    s.op0_mux_sel   = OutPort( 1 )
    s.op1_mux_sel   = OutPort( 2 )
    s.wb_mux_sel    = OutPort( 2 )
    # Mem
    s.mreq_type     = OutPort( 1 )
    # PC
    s.pc_mux_sel    = OutPort( 2 )
    # CP0
    s.cpr_wen       = OutPort( 1 )

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Decode Logic
    #---------------------------------------------------------------------

    @s.combinational
    def decode_ctrl_logic():
      # NOP
      if   s.inst_type.value == isa.NOP:
        s.alu_fn.value       = X
        s.rd_addr0.value     = X
        s.rd_addr1.value     = X
        s.rf_wen.value       = X
        s.rf_waddr.value     = X
        s.op0_mux_sel.value  = X
        s.op1_mux_sel.value  = X
        s.wb_mux_sel.value   = X
        s.mreq_type.value    = X
        s.cpr_wen.value      = X
        s.pc_mux_sel.value   = PC_PC4

      # ADDU
      elif s.inst_type.value == isa.ADDU:
        s.alu_fn.value       = ALU_ADD
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = s.inst_bits[ isa.RT ].value
        s.rf_wen.value       = 1
        s.rf_waddr.value     = s.inst_bits[ isa.RD ].value
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_RF
        s.wb_mux_sel.value   = WR_ALU
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # ADDIU
      elif s.inst_type.value == isa.ADDIU:
        s.alu_fn.value       = ALU_ADD
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = X
        s.rf_wen.value       = 1
        s.rf_waddr.value     = s.inst_bits[ isa.RT ].value
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_SEXT
        s.wb_mux_sel.value   = WR_ALU
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # ORI
      elif s.inst_type.value == isa.ORI:
        s.alu_fn.value       = ALU_OR
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = X
        s.rf_wen.value       = 1
        s.rf_waddr.value     = s.inst_bits[ isa.RT ].value
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_ZEXT
        s.wb_mux_sel.value   = WR_ALU
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # LUI
      elif s.inst_type.value == isa.LUI:
        s.alu_fn.value       = ALU_SLL
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = X
        s.rf_wen.value       = 1
        s.rf_waddr.value     = s.inst_bits[ isa.RT ].value
        s.op0_mux_sel.value  = RD0_16
        s.op1_mux_sel.value  = RD1_ZEXT
        s.wb_mux_sel.value   = WR_ALU
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # LW
      elif s.inst_type.value == isa.LW:
        s.alu_fn.value       = ALU_ADD
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = X
        s.rf_wen.value       = 1
        s.rf_waddr.value     = s.inst_bits[ isa.RT ].value
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_SEXT
        s.wb_mux_sel.value   = WR_MEM
        s.mreq_type.value    = MEM_LW
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # SW
      elif s.inst_type.value == isa.SW:
        s.alu_fn.value       = ALU_ADD
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = s.inst_bits[ isa.RT ].value
        s.rf_wen.value       = 0
        s.rf_waddr.value     = X
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_SEXT
        s.wb_mux_sel.value   = X
        s.mreq_type.value    = MEM_SW
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_PC4

      # BNE
      elif s.inst_type.value == isa.BNE:
        s.alu_fn.value       = ALU_SUB
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = s.inst_bits[ isa.RT ].value
        s.rf_wen.value       = 0
        s.rf_waddr.value     = X
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = RD1_RF
        s.wb_mux_sel.value   = X
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_BR

      # JAL
      elif s.inst_type.value == isa.JAL:
        s.alu_fn.value       = X
        s.rd_addr0.value     = X
        s.rd_addr1.value     = X
        s.rf_wen.value       = 1
        s.rf_waddr.value     = 31
        s.op0_mux_sel.value  = X
        s.op1_mux_sel.value  = X
        s.wb_mux_sel.value   = WR_PC4
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_JAL

      # JR
      elif s.inst_type.value == isa.JR:
        s.alu_fn.value       = X
        s.rd_addr0.value     = s.inst_bits[ isa.RS ].value
        s.rd_addr1.value     = X
        s.rf_wen.value       = 0
        s.rf_waddr.value     = X
        s.op0_mux_sel.value  = RD0_RF
        s.op1_mux_sel.value  = X
        s.wb_mux_sel.value   = X
        s.mreq_type.value    = X
        s.cpr_wen.value      = 0
        s.pc_mux_sel.value   = PC_JR

      # MTC0
      elif s.inst_type.value == isa.MTC0:
        s.alu_fn.value       = X
        s.rd_addr0.value     = X
        s.rd_addr1.value     = s.inst_bits[ isa.RT ].value
        s.rf_wen.value       = 0
        s.rf_waddr.value     = X
        s.op0_mux_sel.value  = X
        s.op1_mux_sel.value  = RD1_RF
        s.wb_mux_sel.value   = X
        s.mreq_type.value    = X
        s.cpr_wen.value      = 1
        s.pc_mux_sel.value   = PC_PC4

      # Unsupported Inst Type
      else:
        assert False
