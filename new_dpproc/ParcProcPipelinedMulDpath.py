#=========================================================================
# Lab 2 - ParcProc5stBypassDpath
#=========================================================================
# parc processor 5 stage bypassing pipeline control unit

from new_pymtl           import *
from muldiv.muldiv_msg   import BitStructIndex as md_msg
from muldiv.IntMulDivRTL import IntMulDivRTL
from new_pmlib           import RegisterFile
from ALU                 import ALU
from SnoopUnit           import SnoopUnit
from misc_units          import BranchTarget
from misc_units          import JumpTarget

import new_pmlib
import ParcISA as isa

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

CONSTANT_0  =  0
CONSTANT_16 = 16

# Control Signal Value Encoding

X           =  0

RD0_BYP_RF  =  0
RD0_BYP_X   =  1
RD0_BYP_M   =  2
RD0_BYP_W   =  3

RD0_RF      =  0
RD0_16      =  1
RD0_0       =  2
RD0_SH      =  3

RD1_BYP_RF  =  0
RD1_BYP_X   =  1
RD1_BYP_M   =  2
RD1_BYP_W   =  3

RD1_RF      =  0
RD1_ZEXT    =  1
RD1_SEXT    =  2
RD1_PC4     =  3

ALU_X       =  0
MD_X        =  1

MEM_EN      =  1

MEM_LW      =  0
MEM_SW      =  1

WR_ALU      =  0
WR_MEM      =  1

PC_PC4      =  0
PC_BR       =  1
PC_JAL      =  2
PC_JR       =  3

BYTE        =  1
HWORD       =  2
UBYTE       =  3
UHWORD      =  4
WORD        =  0

#-------------------------------------------------------------------------
# ParcProcPipelinedMulDpath
#-------------------------------------------------------------------------
class ParcProcPipelinedMulDpath( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, reset_vector ):

    s.reset_vector = reset_vector
    s.mreq  = new_pmlib.mem_msgs.MemReqParams( 32, 32 )
    s.mresp = new_pmlib.mem_msgs.MemRespParams( 32 )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # TestProcManager status signal

    s.status               = OutPort ( 32 )
    s.stats_en             = OutPort ( 1  )

    # Instruction memory request and response ports

    s.imemreq_msg          = OutPort ( s.mreq.nbits  )

    s.imemresp_val         = InPort  ( 1 )
    s.imemresp_rdy         = OutPort ( 1 )
    s.imemresp_msg         = InPort  ( s.mresp.nbits )

    # Data memory request and response ports

    s.dmemreq_msg          = OutPort ( s.mreq.nbits  )
    s.dmemresp_msg         = InPort  ( s.mresp.nbits )

    s.to_cp2_msg           = OutPort ( 5+32 )
    s.from_cp2_msg         = OutPort ( 32 )

    #---------------------------------------------------------------------
    # Control Signals (ctrl -> dpath)
    #---------------------------------------------------------------------

    s.pc_mux_sel_P         = InPort ( 2 )
    s.pc_reg_wen_P         = InPort ( 1 )
    s.pc_bypass_mux_sel_P  = InPort ( 1 )

    s.pipe_en_F            = InPort ( 1 )
    s.drop_resp_F          = InPort ( 1 )
    s.imemresp_rdy_F       = InPort ( 1 )

    s.pipe_en_D            = InPort ( 1 )
    s.op0_mux_sel_D        = InPort ( 2 )
    s.op0_byp_mux_sel_D    = InPort ( 2 )
    s.op1_mux_sel_D        = InPort ( 2 )
    s.op1_byp_mux_sel_D    = InPort ( 2 )
    s.muldiv_fn_D          = InPort ( 3 )
    s.muldivreq_val_D      = InPort ( 1 )

    s.pipe_en_X            = InPort ( 1 )
    s.alu_fn_X             = InPort ( 4 )
    s.execute_mux_sel_X    = InPort ( 1 )
    s.muldivresp_rdy_X     = InPort ( 1 )
    s.dmemreq_type_X       = InPort ( 1 )
    s.dmemreq_len_X        = InPort ( 2 )

    s.pipe_en_M            = InPort ( 1 )
    s.wb_mux_sel_M         = InPort ( 1 )
    s.dmemresp_sel_M       = InPort ( 3 )

    s.pipe_en_W            = InPort ( 1 )
    s.cp0_status_wen_W     = InPort ( 1 )
    s.cp0_stats_wen_W      = InPort ( 1 )

    s.rf_wen_W             = InPort[2]( 1 )
    s.rf_waddr_W           = InPort[2]( 5 )
    s.wb_mux_W_sel         = InPort ( 1 )
    

    #---------------------------------------------------------------------
    # Status Signals  (ctrl <- dpath)
    #---------------------------------------------------------------------

    s.imemresp_val_F       = OutPort ( 1  )
    s.muldivreq_rdy_D      = OutPort ( 1  )
    s.inst_D               = OutPort ( 32 )
    s.br_cond_eq_X         = OutPort ( 1  )
    s.br_cond_zero_X       = OutPort ( 1  )
    s.br_cond_neg_X        = OutPort ( 1  )
    s.muldivresp_val_X     = OutPort ( 1  )
    s.cp2_go_D             = OutPort ( 1  )

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # P Stage
    #---------------------------------------------------------------------

    # inputs to pc_mux_P

    s.pc_plus_4_F      = Wire( 32 )
    s.pc_br_tgt_X      = Wire( 32 )
    s.pc_jmp_tgt_D     = Wire( 32 )
    s.pc_jmp_reg_tgt_D = Wire( 32 )

    # pc_mux_P

    s.pc_mux_P = new_pmlib.Mux( 32, 4 )

    s.connect( s.pc_mux_P.in_[PC_PC4], s.pc_plus_4_F      )
    s.connect( s.pc_mux_P.in_[PC_BR],  s.pc_br_tgt_X      )
    s.connect( s.pc_mux_P.in_[PC_JAL], s.pc_jmp_tgt_D     )
    s.connect( s.pc_mux_P.in_[PC_JR],  s.pc_jmp_reg_tgt_D )
    s.connect( s.pc_mux_P.sel,         s.pc_mux_sel_P     )

    # pc_reg_P

    s.pc_reg_P = new_pmlib.regs.RegEnRst( 32,
                                         reset_value = s.reset_vector )

    s.connect( s.pc_reg_P.en,  s.pc_reg_wen_P )
    s.connect( s.pc_reg_P.in_, s.pc_mux_P.out )

    # pc_bypass_mux_P

    s.pc_bypass_mux_P = new_pmlib.Mux( 32, 2 )

    s.connect( s.pc_bypass_mux_P.in_[0], s.pc_reg_P.out        )
    s.connect( s.pc_bypass_mux_P.in_[1], s.pc_mux_P.out        )
    s.connect( s.pc_bypass_mux_P.sel,    s.pc_bypass_mux_sel_P )

    s.connect( s.pc_bypass_mux_P.out,
             s.imemreq_msg[ s.mreq.addr_slice ] )

    #---------------------------------------------------------------------
    # F Stage
    #---------------------------------------------------------------------

    # pc_reg_F

    s.pc_reg_F = new_pmlib.regs.RegEn( 32 )

    s.connect( s.pc_reg_F.in_, s.pc_bypass_mux_P.out )
    s.connect( s.pc_reg_F.en,  s.pipe_en_F           )

    # pc_incr_F

    s.pc_incr_F = new_pmlib.arith.Incrementer( 32, 4 )

    s.connect( s.pc_incr_F.in_, s.pc_reg_F.out  )
    s.connect( s.pc_incr_F.out, s.pc_plus_4_F   )

    # snoop_unit_F

    s.snoop_unit_F = SnoopUnit( 32 )

    s.connect( s.snoop_unit_F.drop,    s.drop_resp_F                        )
    s.connect( s.snoop_unit_F.in_.val, s.imemresp_val                       )
    s.connect( s.snoop_unit_F.in_.rdy, s.imemresp_rdy                       )
    s.connect( s.snoop_unit_F.in_.msg, s.imemresp_msg[ s.mresp.data_slice ] )
    s.connect( s.snoop_unit_F.out.val, s.imemresp_val_F                     )
    s.connect( s.snoop_unit_F.out.rdy, s.imemresp_rdy_F                     )

    #---------------------------------------------------------------------
    # D Stage
    #---------------------------------------------------------------------

    # bypass wires

    s.op_byp_X = Wire(32)
    s.op_byp_M = Wire(32)
    s.op_byp_W = Wire(32)

    # pc_plus_4_D

    s.pc_plus4_D = new_pmlib.regs.RegEn( 32 )

    s.connect( s.pc_plus4_D.in_, s.pc_incr_F.out )
    s.connect( s.pc_plus4_D.en,  s.pipe_en_D     )

    # ir_reg_D

    s.ir_reg_D = new_pmlib.regs.RegEn( 32 )

    s.connect( s.ir_reg_D.in_,  s.snoop_unit_F.out.msg )
    s.connect( s.ir_reg_D.en,   s.pipe_en_D           )
    s.connect( s.ir_reg_D.out,  s.inst_D              )

    # register file

    s.rf = RegisterFile( nbits      = 32,
                         nregs      = 32,
                         rd_ports   = 2,
                         wr_ports   = 2,
                         const_zero = True )

    s.connect( s.rf.rd_addr[0], s.ir_reg_D.out[ isa.RS ] )
    s.connect( s.rf.rd_addr[1], s.ir_reg_D.out[ isa.RT ] )

    # zext

    s.zext_D = new_pmlib.arith.ZeroExtender( in_nbits = 16, out_nbits = 32 )

    s.connect( s.zext_D.in_, s.ir_reg_D.out[ isa.IMM ] )

    # sext

    s.sext_D = new_pmlib.arith.SignExtender( in_nbits = 16, out_nbits = 32 )

    s.connect( s.sext_D.in_, s.ir_reg_D.out[ isa.IMM ] )

    # zext shamt

    s.shamt_D = new_pmlib.arith.ZeroExtender( in_nbits = 5, out_nbits = 32 )

    s.connect( s.shamt_D.in_, s.ir_reg_D.out[ isa.SHAMT ] )

    # op0_byp_mux

    s.op0_byp_mux_D = new_pmlib.Mux( 32, 4 )

    s.connect( s.op0_byp_mux_D.in_[RD0_BYP_RF], s.rf.rd_data[0]     )
    s.connect( s.op0_byp_mux_D.in_[RD0_BYP_X ], s.op_byp_X          )
    s.connect( s.op0_byp_mux_D.in_[RD0_BYP_M ], s.op_byp_M          )
    s.connect( s.op0_byp_mux_D.in_[RD0_BYP_W ], s.op_byp_W          )
    s.connect( s.op0_byp_mux_D.sel,             s.op0_byp_mux_sel_D )

    # op0_mux

    s.op0_mux_D = new_pmlib.Mux( 32, 4 )

    s.connect( s.op0_mux_D.in_[RD0_16],  CONSTANT_16            )
    s.connect( s.op0_mux_D.in_[RD0_RF],  s.op0_byp_mux_D.out )
    s.connect( s.op0_mux_D.in_[RD0_0],   CONSTANT_0             )
    s.connect( s.op0_mux_D.in_[RD0_SH],  s.shamt_D.out       )
    s.connect( s.op0_mux_D.sel,          s.op0_mux_sel_D     )

    # op1_byp_mux

    s.op1_byp_mux_D = new_pmlib.Mux( 32, 4 )

    s.connect( s.op1_byp_mux_D.in_[RD1_BYP_RF], s.rf.rd_data[1]     )
    s.connect( s.op1_byp_mux_D.in_[RD1_BYP_X ], s.op_byp_X          )
    s.connect( s.op1_byp_mux_D.in_[RD1_BYP_M ], s.op_byp_M          )
    s.connect( s.op1_byp_mux_D.in_[RD1_BYP_W ], s.op_byp_W          )
    s.connect( s.op1_byp_mux_D.sel,             s.op1_byp_mux_sel_D )

    # op1_mux

    s.op1_mux_D = new_pmlib.Mux( 32, 4 )

    s.connect( s.op1_mux_D.in_[RD1_SEXT], s.sext_D.out        )
    s.connect( s.op1_mux_D.in_[RD1_ZEXT], s.zext_D.out        )
    s.connect( s.op1_mux_D.in_[RD1_RF],   s.op1_byp_mux_D.out )
    s.connect( s.op1_mux_D.in_[RD1_PC4],  s.pc_plus4_D.out    )
    s.connect( s.op1_mux_D.sel,           s.op1_mux_sel_D     )

    # branch_target_D

    s.br_tgt_D = BranchTarget( 32 )

    s.connect( s.br_tgt_D.pc_4,  s.pc_plus4_D.out        )
    s.connect( s.br_tgt_D.imm,   s.ir_reg_D.out[isa.IMM] )

    # jump_target_D

    s.jmp_tgt_D = JumpTarget( 32 )

    s.connect( s.jmp_tgt_D.pc_4, s.pc_plus4_D.out        )
    s.connect( s.jmp_tgt_D.tgt,  s.ir_reg_D.out[isa.TGT] )
    s.connect( s.jmp_tgt_D.out,  s.pc_jmp_tgt_D          )

    # jump register target s.connection

    s.connect( s.pc_jmp_reg_tgt_D, s.op0_byp_mux_D.out )

    # coprocessor 2 interface

    s.connect( s.to_cp2_msg[32:37], s.ir_reg_D.out[isa.RD] )  # addr
    s.connect( s.to_cp2_msg[ 0:32], s.op1_byp_mux_D.out    )  # data

    @s.combinational
    def cp2_go():
      s.cp2_go_D.value = 0

    #---------------------------------------------------------------------
    # X Stage
    #---------------------------------------------------------------------

    # br_tgt_X

    s.br_tgt_reg_X = new_pmlib.regs.RegEn( 32 )

    s.connect( s.br_tgt_reg_X.in_, s.br_tgt_D.out )
    s.connect( s.br_tgt_reg_X.en,  s.pipe_en_X    )
    s.connect( s.br_tgt_reg_X.out, s.pc_br_tgt_X  )

    # wdata_X

    s.wdata_reg_X   = new_pmlib.regs.RegEn( 32 )

    s.connect( s.wdata_reg_X.in_, s.op1_byp_mux_D.out )
    s.connect( s.wdata_reg_X.en,  s.pipe_en_X         )

    # op0_reg_X

    s.op0_reg_X = new_pmlib.regs.RegEn( 32 )

    s.connect( s.op0_reg_X.in_, s.op0_mux_D.out )
    s.connect( s.op0_reg_X.en,  s.pipe_en_X     )

    # op1_reg_X

    s.op1_reg_X = new_pmlib.regs.RegEn( 32 )

    s.connect( s.op1_reg_X.in_, s.op1_mux_D.out )
    s.connect( s.op1_reg_X.en,  s.pipe_en_X     )

    # alu_X

    s.alu_X = ALU( nbits = 32 )

    s.connect( s.alu_X.sel, s.alu_fn_X      )
    s.connect( s.alu_X.in0, s.op0_reg_X.out )
    s.connect( s.alu_X.in1, s.op1_reg_X.out )

    # muldiv_X

    s.muldiv_X = IntMulDivRTL( mult_nstages=4 )

    s.connect( s.muldiv_X.in_.val,                     s.muldivreq_val_D )
    s.connect( s.muldiv_X.in_.rdy,                     s.muldivreq_rdy_D )
    s.connect( s.muldiv_X.in_.msg[ md_msg.muldiv_op ], s.muldiv_fn_D     )
    s.connect( s.muldiv_X.in_.msg[ md_msg.arg_A     ], s.op0_mux_D.out   )
    s.connect( s.muldiv_X.in_.msg[ md_msg.arg_B     ], s.op1_mux_D.out   )

    # br_cond_eq

    s.zero_res_cmp_X = new_pmlib.arith.ZeroComparator( 32 )

    s.connect( s.zero_res_cmp_X.in_, s.alu_X.out    )
    s.connect( s.zero_res_cmp_X.out, s.br_cond_eq_X )

    # br_cond_zero

    s.zero_cmp_X = new_pmlib.arith.ZeroComparator( 32 )

    s.connect( s.zero_cmp_X.in_, s.op0_reg_X.out  )
    s.connect( s.zero_cmp_X.out, s.br_cond_zero_X )

    # br_cond_neg

    s.connect( s.br_cond_neg_X, s.op0_reg_X.out[31] )

    # dmemreq_msg

    s.connect( s.alu_X.out,       s.dmemreq_msg[ s.mreq.addr_slice ] )
    s.connect( s.dmemreq_type_X,  s.dmemreq_msg[ s.mreq.type_slice ] )
    s.connect( s.dmemreq_len_X,   s.dmemreq_msg[ s.mreq.len_slice  ] )
    s.connect( s.wdata_reg_X.out, s.dmemreq_msg[ s.mreq.data_slice ] )

    # ex_mux_X

    s.ex_mux_X = new_pmlib.Mux( 32, 2 )

    s.connect( s.ex_mux_X.in_[0], s.alu_X.out         )
    s.connect( s.ex_mux_X.in_[1], s.muldiv_X.out.msg  )
    s.connect( s.ex_mux_X.sel,    s.execute_mux_sel_X )
    s.connect( s.ex_mux_X.out,    s.op_byp_X          )

    # muldivresp - val/rdy s.connections

    s.connect( s.muldiv_X.out.val, s.muldivresp_val_X )
    s.connect( s.muldiv_X.out.rdy, s.muldivresp_rdy_X )

    #---------------------------------------------------------------------
    # M Stage
    #---------------------------------------------------------------------

    # alu_out_reg_M

    s.alu_out_reg_M = new_pmlib.regs.RegEn( 32 )

    s.connect( s.alu_out_reg_M.in_, s.ex_mux_X.out   )
    s.connect( s.alu_out_reg_M.en,  s.pipe_en_M      )

    # dmemresp_data

    s.dmemresp_data_M = Wire( 32 )

    s.connect( s.dmemresp_data_M, s.dmemresp_msg[ s.mresp.data_slice ] )

    # byte extraction

    s.dmemresp_byte_M = new_pmlib.arith.SignExtender( in_nbits=8, out_nbits=32 )

    s.connect( s.dmemresp_byte_M.in_, s.dmemresp_data_M[0:8] )

    # ubyte extraction

    s.dmemresp_ubyte_M = new_pmlib.arith.ZeroExtender( in_nbits=8, out_nbits=32 )

    s.connect( s.dmemresp_ubyte_M.in_, s.dmemresp_data_M[0:8] )

    # hword extraction

    s.dmemresp_hword_M = new_pmlib.arith.SignExtender( in_nbits=16, out_nbits=32 )

    s.connect( s.dmemresp_hword_M.in_, s.dmemresp_data_M[0:16] )

    # uhword extraction

    s.dmemresp_uhword_M = new_pmlib.arith.ZeroExtender( in_nbits=16, out_nbits=32 )

    s.connect( s.dmemresp_uhword_M.in_, s.dmemresp_data_M[0:16] )

    # dmemresp_mux_M

    s.dmemresp_mux_M = new_pmlib.Mux( 32, 8 )

    s.connect( s.dmemresp_mux_M.in_[WORD],   s.dmemresp_data_M        )
    s.connect( s.dmemresp_mux_M.in_[BYTE],   s.dmemresp_byte_M.out    )
    s.connect( s.dmemresp_mux_M.in_[UBYTE],  s.dmemresp_ubyte_M.out   )
    s.connect( s.dmemresp_mux_M.in_[HWORD],  s.dmemresp_hword_M.out   )
    s.connect( s.dmemresp_mux_M.in_[UHWORD], s.dmemresp_uhword_M.out  )
    s.connect( s.dmemresp_mux_M.sel,         s.dmemresp_sel_M         )

    # wb_mux_M

    s.wb_mux_M = new_pmlib.Mux( 32, 2 )

    s.connect( s.wb_mux_M.in_[WR_ALU], s.alu_out_reg_M.out  )
    s.connect( s.wb_mux_M.in_[WR_MEM], s.dmemresp_mux_M.out )
    s.connect( s.wb_mux_M.sel,         s.wb_mux_sel_M       )
    s.connect( s.wb_mux_M.out,         s.op_byp_M           )

    #---------------------------------------------------------------------
    # W Stage
    #---------------------------------------------------------------------

    # res_reg_w
    s.write_back_W = Wire( 32 )
    s.res_reg_W = new_pmlib.regs.RegEn( 32 )

    s.wb_mux_W  = new_pmlib.Mux( 32, 2 )
    s.connect( s.res_reg_W.out, s.wb_mux_W.in_[0] )
    s.connect( s.from_cp2_msg,  s.wb_mux_W.in_[1] )
    s.connect( s.wb_mux_W_sel,  s.wb_mux_W.sel    )
    s.connect( s.write_back_W,  s.wb_mux_W.out    )

    s.connect( s.res_reg_W.in_, s.wb_mux_M.out  )
    s.connect( s.res_reg_W.en,  s.pipe_en_W     )

    s.connect( s.rf.wr_en,      s.rf_wen_W  [0]    )
    s.connect( s.rf.wr_addr,    s.rf_waddr_W[0]    )
    s.connect( s.rf.wr_data,    s.wb_mux_W.out     )
    s.connect( s.rf.wr_en2,     s.rf_wen_W  [1]    )
    s.connect( s.rf.wr_addr2,   s.rf_waddr_W[1]    )
    s.connect( s.rf.wr_data2,   s.muldiv_X.out.msg )

    s.connect( s.wb_mux_W.out, s.op_byp_W      )

    # cp0_status_reg_W

    s.cp0_status_reg_W = new_pmlib.regs.RegEn( 32 )

    s.connect( s.cp0_status_reg_W.in_, s.res_reg_W.out    )
    s.connect( s.cp0_status_reg_W.en,  s.cp0_status_wen_W )
    s.connect( s.cp0_status_reg_W.out, s.status           )

    # cp0_stats_reg_W

    s.cp0_stats_reg_W = new_pmlib.regs.RegEn( 32 )

    s.connect( s.cp0_stats_reg_W.in_,    s.res_reg_W.out   )
    s.connect( s.cp0_stats_reg_W.en,     s.cp0_stats_wen_W )
    s.connect( s.cp0_stats_reg_W.out[0], s.stats_en        )
