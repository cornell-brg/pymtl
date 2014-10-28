#=======================================================================
# ParcProc5stStallCtrl.py
#=======================================================================
# parc processor 5 stage stalling pipeline control unit

from pymtl import *
from new_pmlib import Mux

from new_pmlib.PipeCtrl         import PipeCtrl
from ParcProc5stStallDecodeCtrl import ParcProc5stStallDecodeCtrl

import ParcISA as isa

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------

# Control Signal Bus Width

CS_WIDTH = 46            # TODO: this should really be 45!

# Control Signal Bus Definition

RS_EN        = slice( 44, 45 )  # 1
RS_RADDR     = slice( 39, 44 )  # 5
RT_EN        = slice( 38, 39 )  # 1
RT_RADDR     = slice( 33, 38 )  # 5
RF_WEN       = slice( 32, 33 )  # 1
RF_WADDR     = slice( 27, 32 )  # 5
OP0_MUX_SEL  = slice( 25, 27 )  # 2
OP1_MUX_SEL  = slice( 23, 25 )  # 2
ALU_FN       = slice( 19, 23 )  # 4
MD_EN        = slice( 18, 19 )  # 1
MD_FN        = slice( 15, 18 )  # 3
EX_MUX_SEL   = slice( 14, 15 )  # 1
MEM_REQ_EN   = slice( 13, 14 )  # 1
MEM_REQ_TYPE = slice( 12, 13 )  # 1
MEM_REQ_LEN  = slice( 10, 12 )  # 2
MEM_RESP_SEL = slice(  7, 10 )  # 3
WB_MUX_SEL   = slice(  6,  7 )  # 1
CPR_WEN      = slice(  5,  6 )  # 1
CPR_WADDR    = slice(  0,  5 )  # 5


# Control Signal Value Encoding

UNOP     =  0
X        =  0

NVAL     =  0
VAL      =  1

MEM_LW   =  0
MEM_SW   =  1

PC_PC4   =  0
PC_BR    =  1
PC_JAL   =  2
PC_JR    =  3

BYTE     =  1
HWORD    =  2
UBYTE    =  3
UHWORD   =  4
WORD     =  0

#-----------------------------------------------------------------------
# ParcProc5stStallCtrl
#-----------------------------------------------------------------------
class ParcProc5stStallCtrl( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    #-------------------------------------------------------------------
    # Interface Ports
    #-------------------------------------------------------------------

    # TestProcManager go signal

    s.go                   = InPort  ( 1  )

    s.imemreq_val          = OutPort ( 1  )
    s.imemreq_rdy          = InPort  ( 1  )
    s.dmemreq_val          = OutPort ( 1  )
    s.dmemreq_rdy          = InPort  ( 1  )
    s.dmemresp_val         = InPort  ( 1  )
    s.dmemresp_rdy         = OutPort ( 1  )
    s.num_insts            = OutPort ( 32 )

    #-------------------------------------------------------------------
    # Control Signals (ctrl -> dpath)
    #-------------------------------------------------------------------

    s.pc_mux_sel_P         = OutPort ( 2 )
    s.pc_reg_wen_P         = OutPort ( 1 )
    s.pc_bypass_mux_sel_P  = OutPort ( 1 )

    s.pipe_en_F            = OutPort ( 1 )
    s.drop_resp_F          = OutPort ( 1 )
    s.imemresp_rdy_F       = OutPort ( 1 )

    s.pipe_en_D            = OutPort ( 1 )
    s.op0_mux_sel_D        = OutPort ( 2 )
    s.op1_mux_sel_D        = OutPort ( 2 )
    s.muldiv_fn_D          = OutPort ( 3 )
    s.muldivreq_val_D      = OutPort ( 1 )

    s.pipe_en_X            = OutPort ( 1 )
    s.alu_fn_X             = OutPort ( 4 )
    s.execute_mux_sel_X    = OutPort ( 1 )
    s.muldivresp_rdy_X     = OutPort ( 1 )
    s.dmemreq_type_X       = OutPort ( 1 )
    s.dmemreq_len_X        = OutPort ( 2 )

    s.pipe_en_M            = OutPort ( 1 )
    s.wb_mux_sel_M         = OutPort ( 1 )
    s.dmemresp_sel_M       = OutPort ( 3 )

    s.pipe_en_W            = OutPort ( 1 )
    s.cp0_status_wen_W     = OutPort ( 1 )
    s.cp0_stats_wen_W      = OutPort ( 1 )
    s.rf_wen_W             = OutPort ( 1 )
    s.rf_waddr_W           = OutPort ( 5 )

    #-------------------------------------------------------------------
    # Status Signals  (ctrl <- dpath)
    #-------------------------------------------------------------------

    s.imemresp_val_F       = InPort ( 1  )
    s.inst_D               = InPort ( 32 )
    s.muldivreq_rdy_D      = InPort ( 1  )
    s.br_cond_eq_X         = InPort ( 1  )
    s.br_cond_zero_X       = InPort ( 1  )
    s.br_cond_neg_X        = InPort ( 1  )
    s.muldivresp_val_X     = InPort ( 1  )
    s.stats_en             = InPort ( 1  )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    #-------------------------------------------------------------------
    # P Stage
    #-------------------------------------------------------------------

    # branch/jump resolutions

    s.branch_X_taken    = Wire( 1 )
    s.jmp_D_taken       = Wire( 1 )
    s.jmp_reg_D_taken   = Wire( 1 )

    # pc_reg_full_P bit

    s.pc_reg_full_P     = Wire( 1 )

    s.imemreq_enq_val_P = Wire( 1 )
    s.imemreq_enq_rdy_P = Wire( 1 )

    s.go_bit            = Wire( 1 )
    s.valid_next_F      = Wire( 1 )

    #-------------------------------------------------------------------
    # F stage
    #-------------------------------------------------------------------

    # pipe_ctrl_F

    s.pipe_ctrl_F = PipeCtrl()

    s.connect( s.pipe_ctrl_F.pvalid,     s.valid_next_F )
    s.connect( s.pipe_ctrl_F.pipereg_en, s.pipe_en_F    )
    s.connect( s.pipe_ctrl_F.psquash,    s.drop_resp_F  )

    #-------------------------------------------------------------------
    # D stage
    #-------------------------------------------------------------------

    # pipe_ctrl_D

    s.pipe_ctrl_D = PipeCtrl()

    s.connect( s.pipe_ctrl_D.pvalid,     s.pipe_ctrl_F.nvalid  )
    s.connect( s.pipe_ctrl_D.pstall,     s.pipe_ctrl_F.nstall  )
    s.connect( s.pipe_ctrl_D.psquash,    s.pipe_ctrl_F.nsquash )
    s.connect( s.pipe_ctrl_D.pipereg_en, s.pipe_en_D           )

    s.pipe_decode_ctrl_D = ParcProc5stStallDecodeCtrl()

    s.decode_inst_mux = Mux( 32, 2 )

    s.connect( s.decode_inst_mux.in_[NVAL], UNOP                      )
    s.connect( s.decode_inst_mux.in_[VAL],  s.inst_D                  )
    s.connect( s.decode_inst_mux.sel,       s.pipe_ctrl_D.pipereg_val )

    s.connect( s.pipe_decode_ctrl_D.inst_bits, s.decode_inst_mux.out )


    #-------------------------------------------------------------------
    # X stage
    #-------------------------------------------------------------------

    # pipe_ctrl_X

    s.pipe_ctrl_X = PipeCtrl()

    s.connect( s.pipe_ctrl_X.pvalid,     s.pipe_ctrl_D.nvalid  )
    s.connect( s.pipe_ctrl_X.pstall,     s.pipe_ctrl_D.nstall  )
    s.connect( s.pipe_ctrl_X.psquash,    s.pipe_ctrl_D.nsquash )
    s.connect( s.pipe_ctrl_X.pipereg_en, s.pipe_en_X           )

    s.pipe_cs_X = Wire( CS_WIDTH )
    s.inst_X    = Wire( 8 )

    #-------------------------------------------------------------------
    # M stage
    #-------------------------------------------------------------------

    # pipe_ctrl_M

    s.pipe_ctrl_M = PipeCtrl()

    s.connect( s.pipe_ctrl_M.pvalid,     s.pipe_ctrl_X.nvalid  )
    s.connect( s.pipe_ctrl_M.pstall,     s.pipe_ctrl_X.nstall  )
    s.connect( s.pipe_ctrl_M.psquash,    s.pipe_ctrl_X.nsquash )
    s.connect( s.pipe_ctrl_M.pipereg_en, s.pipe_en_M           )

    s.pipe_cs_M = Wire( CS_WIDTH )
    s.inst_M    = Wire( 8 )

    #-------------------------------------------------------------------
    # W stage
    #-------------------------------------------------------------------

    # pipe_ctrl_W

    s.pipe_ctrl_W = PipeCtrl()

    s.connect( s.pipe_ctrl_W.pvalid,     s.pipe_ctrl_M.nvalid  )
    s.connect( s.pipe_ctrl_W.pstall,     s.pipe_ctrl_M.nstall  )
    s.connect( s.pipe_ctrl_W.psquash,    s.pipe_ctrl_M.nsquash )
    s.connect( s.pipe_ctrl_W.pipereg_en, s.pipe_en_W           )

    s.pipe_cs_W = Wire( CS_WIDTH )
    s.inst_W    = Wire( 8 )

    #-------------------------------------------------------------------
    # Pipeline Start
    #-------------------------------------------------------------------
    # go_bit register at the start of P stage and pc_reg_full_P bit
    # calculations

    s.do_deq    = Wire( 1 )
    s.do_enq    = Wire( 1 )
    s.do_bypass = Wire( 1 )

    @s.posedge_clk
    def seq_P():

      # go_bit or pipeline valid bit in P stage

      if   s.reset.value:
        s.go_bit.next = 0
      elif s.go.value:
        s.go_bit.next = s.go.value
      else:
        s.go_bit.next = s.go_bit.value

      if   s.reset.value:
        s.pc_reg_full_P.next = 1
      elif s.do_deq:
        s.pc_reg_full_P.next = 0
      elif s.do_enq and not s.do_bypass:
        s.pc_reg_full_P.next = 1
      else:
        s.pc_reg_full_P.next = s.pc_reg_full_P.value

    #-------------------------------------------------------------------
    # P Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_P():

      # pc_mux_sel logic

      if   s.branch_X_taken.value:
        s.pc_mux_sel_P.value = PC_BR
      elif s.jmp_D_taken.value:
        s.pc_mux_sel_P.value = PC_JAL
      elif s.jmp_reg_D_taken.value:
        s.pc_mux_sel_P.value = PC_JR
      else:
        s.pc_mux_sel_P.value = PC_PC4

      # imemreq_enq_val

      s.imemreq_enq_val_P.value = ( s.go_bit.value
                    and (   s.pipe_ctrl_F.psquash.value
                    or  (    not s.pipe_ctrl_F.psquash.value
                         and not s.pipe_ctrl_F.pstall.value ) ) )

      # pc_bypass_mux_sel

      s.pc_bypass_mux_sel_P.value = ( s.go_bit.value and
                                         not s.pc_reg_full_P.value )

      # pc_reg_wen_P

      s.pc_reg_wen_P.value = ( s.go_bit.value and
                                  ( not s.pc_reg_full_P.value and
                                    s.imemreq_enq_val_P.value ) )

      # imemreq_enq_rdy_P

      s.imemreq_enq_rdy_P.value = not s.pc_reg_full_P.value

      # imemreq_val

      s.imemreq_val.value =  ( s.go_bit.value and
                                  ( s.pc_reg_full_P.value or
                                  ( not s.pc_reg_full_P.value and
                                    s.imemreq_enq_val_P.value ) ) )

      # next valid bit for F stage

      s.valid_next_F.value = ( s.imemreq_val.value and
                                  s.imemreq_rdy.value )

      # pc_reg_full_P calculations

      s.do_deq.value    = s.imemreq_rdy       and s.imemreq_val
      s.do_enq.value    = s.imemreq_enq_rdy_P and s.imemreq_enq_val_P
      s.do_bypass.value = ~s.pc_reg_full_P    and s.do_deq and s.do_enq

    #-------------------------------------------------------------------
    # F <- P
    #-------------------------------------------------------------------

    # pass no control signals

    #-------------------------------------------------------------------
    # F Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_F():

      # osquash signal

      s.pipe_ctrl_F.osquash.value = 0

      # ostall signal

      s.pipe_ctrl_F.ostall.value = ( not s.imemresp_val_F.value and
                                        s.pipe_ctrl_F.pipereg_val.value )

      # imemresp_rdy calculations

      if s.pipe_ctrl_F.pipereg_val.value and not s.pipe_ctrl_F.nstall.value:
        s.imemresp_rdy_F.value = 1
      else:
        s.imemresp_rdy_F.value = 0

    #-------------------------------------------------------------------
    # D <- F
    #-------------------------------------------------------------------

    @s.posedge_clk
    def seq_D():

      if s.reset.value:
        s.num_insts.next   = 0
      else:
        if s.pipe_ctrl_D.pipe_go.value and s.stats_en.value:
          s.num_insts.next = s.num_insts.value + 1

    #-------------------------------------------------------------------
    # D Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_D():

      # idempotent control signals

      s.op0_mux_sel_D.value = s.pipe_decode_ctrl_D.cs[ OP0_MUX_SEL ].value
      s.op1_mux_sel_D.value = s.pipe_decode_ctrl_D.cs[ OP1_MUX_SEL ].value
      s.muldiv_fn_D.value   = s.pipe_decode_ctrl_D.cs[ MD_FN ].value

      # ostall

      data_hazard_stall_X =  \
        ( s.pipe_ctrl_D.pipereg_val.value and
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ].value
              and s.pipe_ctrl_X.pipereg_val.value
              and s.pipe_cs_X[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                    ==  s.pipe_cs_X[ RF_WADDR ].value )
              and ( s.pipe_cs_X[ RF_WADDR ].value != 0 ) )
          or
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ].value
              and s.pipe_ctrl_X.pipereg_val.value
              and s.pipe_cs_X[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                    ==  s.pipe_cs_X[ RF_WADDR ].value )
              and ( s.pipe_cs_X[ RF_WADDR ].value != 0 ) )

          )
        )

      data_hazard_stall_M =  \
        ( s.pipe_ctrl_D.pipereg_val.value and
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ].value
              and s.pipe_ctrl_M.pipereg_val.value
              and s.pipe_cs_M[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                    ==  s.pipe_cs_M[ RF_WADDR ].value )
              and ( s.pipe_cs_M[ RF_WADDR ].value != 0 ) )
          or
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ].value
              and s.pipe_ctrl_M.pipereg_val.value
              and s.pipe_cs_M[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                    ==  s.pipe_cs_M[ RF_WADDR ].value )
              and ( s.pipe_cs_M[ RF_WADDR ].value != 0 ) )

          )
        )

      data_hazard_stall_W =  \
        ( s.pipe_ctrl_D.pipereg_val.value and
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ].value
              and s.pipe_ctrl_W.pipereg_val.value
              and s.pipe_cs_W[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                    ==  s.pipe_cs_W[ RF_WADDR ].value )
              and ( s.pipe_cs_W[ RF_WADDR ].value != 0 ) )
          or
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ].value
              and s.pipe_ctrl_W.pipereg_val.value
              and s.pipe_cs_W[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                    ==  s.pipe_cs_W[ RF_WADDR ].value )
              and ( s.pipe_cs_W[ RF_WADDR ].value != 0 ) )

          )
        )

      data_hazard_stall = \
        (   data_hazard_stall_X
         or data_hazard_stall_M
         or data_hazard_stall_W
        )

      struct_hazard_mult_X = \
        (     s.pipe_ctrl_D.pipereg_val.value
          and not s.muldivreq_rdy_D.value
          and s.pipe_decode_ctrl_D.cs[ MD_EN ].value
        )

      # aggregate stall signal

      s.pipe_ctrl_D.ostall.value = \
      ( data_hazard_stall or struct_hazard_mult_X )

      # osquash signal

      s.jmp_reg_D_taken.value = \
      (
        s.pipe_ctrl_D.pipereg_val.value and
        (    ( s.pipe_decode_ctrl_D.inst.value == isa.JALR )
          or ( s.pipe_decode_ctrl_D.inst.value == isa.JR   )
        )
      )

      s.jmp_D_taken.value = \
      (
        s.pipe_ctrl_D.pipereg_val.value and
        (    ( s.pipe_decode_ctrl_D.inst.value == isa.JAL )
          or ( s.pipe_decode_ctrl_D.inst.value == isa.J   )
        )
      )

      s.pipe_ctrl_D.osquash.value = ( ( s.jmp_D_taken.value or
                                           s.jmp_reg_D_taken.value )
                                       and not s.pipe_ctrl_D.ostall.value )

      # muldivreq_val_D calculations

      if (    s.pipe_ctrl_D.pipereg_val.value
          and not s.pipe_ctrl_D.nstall.value
          and not data_hazard_stall
          and s.pipe_decode_ctrl_D.cs[ MD_EN ].value ):
        s.muldivreq_val_D.value = 1
      else:
        s.muldivreq_val_D.value = 0

      # no architectural state modifications

    #-------------------------------------------------------------------
    # X <- D
    #-------------------------------------------------------------------
    # control signal register at the start of X stage

    @s.posedge_clk
    def seq_DX():

      if s.pipe_ctrl_X.pipereg_en.value:
        s.pipe_cs_X.next = s.pipe_decode_ctrl_D.cs.value
        s.inst_X.next    = s.pipe_decode_ctrl_D.inst.value
      else:
        s.pipe_cs_X.next = s.pipe_cs_X.value
        s.inst_X.next    = s.inst_X.value

    #-------------------------------------------------------------------
    # X Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_X():

      # idempotent control signals

      s.alu_fn_X.value          = s.pipe_cs_X[ ALU_FN ].value
      s.execute_mux_sel_X.value = s.pipe_cs_X[ EX_MUX_SEL ].value
      s.dmemreq_type_X.value    = s.pipe_cs_X[ MEM_REQ_TYPE ].value
      s.dmemreq_len_X.value     = s.pipe_cs_X[ MEM_REQ_LEN  ].value

      # osquash signal

      bne_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BNE )
          and not s.br_cond_eq_X.value
        )
      )

      beq_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BEQ )
          and s.br_cond_eq_X.value
        )
      )

      blez_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BLEZ )
          and ( s.br_cond_zero_X.value or s.br_cond_neg_X.value )
        )
      )

      bgtz_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BGTZ )
          and not ( s.br_cond_zero_X.value or s.br_cond_neg_X.value )
        )
      )

      bltz_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BLTZ )
          and s.br_cond_neg_X.value
        )
      )

      bgez_taken = \
      (
        (
              s.pipe_ctrl_X.pipereg_val.value
          and ( s.inst_X.value == isa.BGEZ )
          and ( s.br_cond_zero_X.value or not s.br_cond_neg_X.value )
        )
      )

      s.branch_X_taken.value = \
      (
            bne_taken
        or  beq_taken
        or  blez_taken
        or  bgtz_taken
        or  bltz_taken
        or  bgez_taken
      )

      s.pipe_ctrl_X.osquash.value = (   s.branch_X_taken.value
                                       and not s.pipe_ctrl_X.ostall.value )

      # muldivresp_rdy calculations

      if (    s.pipe_ctrl_X.pipereg_val.value
          and not s.pipe_ctrl_X.nstall.value
          and s.pipe_cs_X[ MD_EN ].value ):
        s.muldivresp_rdy_X.value = 1
      else:
        s.muldivresp_rdy_X.value = 0
      # ostall signal

      muldiv_busy_stall_X = \
        ( s.pipe_ctrl_X.pipereg_val.value
          and not s.muldivresp_val_X.value
          and s.pipe_cs_X[ MD_EN ].value
        )

      dmemreq_busy_stall_X = \
        ( s.pipe_ctrl_X.pipereg_val.value
          and not s.dmemreq_rdy.value
          and s.pipe_cs_X[ MEM_REQ_EN].value
        )

      s.pipe_ctrl_X.ostall.value  \
      = ( dmemreq_busy_stall_X or muldiv_busy_stall_X )


      # dmemreq_val calculations

      if (    s.pipe_ctrl_X.pipereg_val.value
          and not s.pipe_ctrl_X.nstall.value
          and s.pipe_cs_X[ MEM_REQ_EN ].value ):
        s.dmemreq_val.value = 1
      else:
        s.dmemreq_val.value = 0

    #-------------------------------------------------------------------
    # M <- X
    #-------------------------------------------------------------------
    # control signal register at the start of M stage

    @s.posedge_clk
    def seq_XM():

      if s.pipe_ctrl_M.pipereg_en.value:
        s.pipe_cs_M.next = s.pipe_cs_X.value
        s.inst_M.next    = s.inst_X.value
      else:
        s.pipe_cs_M.next = s.pipe_cs_M.value
        s.inst_M.next    = s.inst_M.value

    #-------------------------------------------------------------------
    # M Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_M():

      # idempotent control signals

      s.wb_mux_sel_M.value   = s.pipe_cs_M[ WB_MUX_SEL ].value
      s.dmemresp_sel_M.value = s.pipe_cs_M[ MEM_RESP_SEL ].value

      # osquash signal

      s.pipe_ctrl_M.osquash.value = 0

      # ostall signal

      s.pipe_ctrl_M.ostall.value  = (  s.pipe_ctrl_M.pipereg_val.value
                                  and not s.dmemresp_val.value
                                  and s.pipe_cs_M[ MEM_REQ_EN].value  )

      # dmemresp_rdy calculations

      if (    s.pipe_ctrl_M.pipereg_val.value
          and not s.pipe_ctrl_M.nstall.value
          and s.pipe_cs_M[ MEM_REQ_EN].value ):
        s.dmemresp_rdy.value = 1
      else:
        s.dmemresp_rdy.value = 0

    #-------------------------------------------------------------------
    # W <- M
    #-------------------------------------------------------------------
    # control signal register at the start of W stage

    @s.posedge_clk
    def seq_MW():

      if s.pipe_ctrl_W.pipereg_en.value:
        s.pipe_cs_W.next = s.pipe_cs_M.value
        s.inst_W.next    = s.inst_M.value
      else:
        s.pipe_cs_W.next = s.pipe_cs_W.value
        s.inst_W.next    = s.inst_W.value

    #-------------------------------------------------------------------
    # W Stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_W():

      # idempotent control signals

      s.rf_waddr_W.value = s.pipe_cs_W[ RF_WADDR ].value

      # osquash signal

      s.pipe_ctrl_W.osquash.value = 0

      # ostall signal

      s.pipe_ctrl_W.ostall.value  = 0

      # architectural state modifications

      if s.pipe_ctrl_W.pipe_go.value:

        s.cp0_status_wen_W.value = \
        (
               s.pipe_cs_W[ CPR_WEN ].value
          and  s.pipe_cs_W[ CPR_WADDR].value == 1
        )

        s.cp0_stats_wen_W.value = \
        (
               s.pipe_cs_W[ CPR_WEN ].value
          and  s.pipe_cs_W[ CPR_WADDR].value == 10
        )

        s.rf_wen_W.value = s.pipe_cs_W[ RF_WEN ].value

      else:
        s.cp0_status_wen_W.value = 0
        s.cp0_stats_wen_W.value  = 0
        s.rf_wen_W.value = 0
