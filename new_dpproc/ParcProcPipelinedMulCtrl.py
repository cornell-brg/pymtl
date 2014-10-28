#=======================================================================
# ParcProc5stBypassCtrl.py
#=======================================================================
# parc processor 5 stage bypassing pipeline control unit

from pymtl import *
from pclib import Mux

from pclib.PipeCtrl          import PipeCtrl
from ParcProc5stBypassDecodeCtrl import ParcProc5stBypassDecodeCtrl
from ParcProc5stBypassDecodeCtrl import md_mul

import ParcISA as isa

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------

# Control Signal Bus Width

CS_WIDTH = 46            # TODO: this should really be 45!

# Control Signal Bus Definition

RS_EN        = slice( 45, 46 )  # 1
RS_RADDR     = slice( 40, 45 )  # 5
RT_EN        = slice( 39, 40 )  # 1
RT_RADDR     = slice( 34, 39 )  # 5
RF_WEN       = slice( 33, 34 )  # 1
RF_WADDR     = slice( 28, 33 )  # 5
OP0_MUX_SEL  = slice( 26, 28 )  # 2
OP1_MUX_SEL  = slice( 24, 26 )  # 2
ALU_FN       = slice( 20, 24 )  # 4
MD_EN        = slice( 19, 20 )  # 1
MD_FN        = slice( 16, 19 )  # 3
EX_MUX_SEL   = slice( 15, 16 )  # 1
MEM_REQ_EN   = slice( 14, 15 )  # 1
MEM_REQ_TYPE = slice( 13, 14 )  # 1
MEM_REQ_LEN  = slice( 11, 13 )  # 2
MEM_RESP_SEL = slice(  8, 11 )  # 3
WB_MUX_SEL   = slice(  7,  8 )  # 1
CPR_WEN      = slice(  6,  7 )  # 1
CPR_WADDR    = slice(  1,  6 )  # 5
CP2_WEN      = slice(  0,  1 )  # 1

# Control Signal Value Encoding

UNOP        =  0
X           =  0

NVAL        =  0
VAL         =  1

MEM_LW      =  0
MEM_SW      =  1

PC_PC4      =  0
PC_BR       =  1
PC_JAL      =  2
PC_JR       =  3

BYTE        =  1
HWORD       =  2
UBYTE       =  3
UHWORD      =  4
WORD        =  0

RD0_BYP_RF  =  0
RD0_BYP_X   =  1
RD0_BYP_M   =  2
RD0_BYP_W   =  3

RD1_BYP_RF  =  0
RD1_BYP_X   =  1
RD1_BYP_M   =  2
RD1_BYP_W   =  3

#-----------------------------------------------------------------------
# ParcProcPipelinedMulCtrl
#-----------------------------------------------------------------------
class ParcProcPipelinedMulCtrlTest( Model ):

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

    s.to_cp2_val           = OutPort ( 1  )
    s.to_cp2_rdy           = InPort  ( 1  )
    s.from_cp2_val         = InPort  ( 1  )
    s.from_cp2_rdy         = OutPort ( 1  )

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
    s.op0_byp_mux_sel_D    = OutPort ( 2 )
    s.op1_mux_sel_D        = OutPort ( 2 )
    s.op1_byp_mux_sel_D    = OutPort ( 2 )
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
    s.wb_mux_W_sel         = OutPort ( 1 )

    s.rf_wen_W             = OutPort[2]( 1 )
    s.rf_waddr_W           = OutPort[2]( 5 )

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
    s.cp2_go_D             = InPort ( 1  )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

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
                    and (    not s.pipe_ctrl_F.psquash.value
                         and not s.pipe_ctrl_F.pstall.value ) )

      # pc_bypass_mux_sel

      s.pc_bypass_mux_sel_P.value = ( s.go_bit.value and
                                    ( s.pipe_ctrl_F.psquash.value
                                      or not s.pc_reg_full_P.value ))

      # pc_reg_wen_P

      s.pc_reg_wen_P.value = ( s.go_bit.value and
                             (          s.pipe_ctrl_F.psquash.value
                               or ( not s.pc_reg_full_P.value and
                                    s.imemreq_enq_val_P.value ) ) )

      # imemreq_enq_rdy_P

      s.imemreq_enq_rdy_P.value = not s.pc_reg_full_P.value

      # imemreq_val

      s.imemreq_val.value =  ( s.go_bit.value and
                               (  ( s.pc_reg_full_P.value and
                                    not s.pipe_ctrl_F.pstall )
                               or ( s.pipe_ctrl_F.psquash and 
                                    not s.pipe_ctrl_F.pstall )
                               or ( not s.pc_reg_full_P.value and
                                    s.imemreq_enq_val_P.value )
                             ))

      # next valid bit for F stage

      s.valid_next_F.value = ( s.imemreq_val.value and
                                  s.imemreq_rdy.value )

      # pc_reg_full_P calculations

      s.do_deq.value    = s.imemreq_rdy       and s.imemreq_val
      s.do_enq.value    = s.imemreq_enq_rdy_P and \
                         (s.imemreq_enq_val_P or s.pipe_ctrl_F.psquash)
      s.do_bypass.value = ~s.pc_reg_full_P    and s.do_deq and s.do_enq

    #-------------------------------------------------------------------
    # F <- P
    #-------------------------------------------------------------------

    # pass no control signals

    #-------------------------------------------------------------------
    # F Stage
    #-------------------------------------------------------------------

    s.pipe_ctrl_F = PipeCtrl()

    s.connect( s.pipe_ctrl_F.pvalid,     s.valid_next_F )
    s.connect( s.pipe_ctrl_F.pipereg_en, s.pipe_en_F    )

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

      # drop response
      s.drop_resp_F.value = s.pipe_ctrl_F.psquash and s.pipe_ctrl_F.pipereg_val

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

    # pipe_ctrl_D

    s.pipe_ctrl_D = PipeCtrl()

    s.connect( s.pipe_ctrl_D.pvalid,     s.pipe_ctrl_F.nvalid  )
    s.connect( s.pipe_ctrl_D.pstall,     s.pipe_ctrl_F.nstall  )
    s.connect( s.pipe_ctrl_D.psquash,    s.pipe_ctrl_F.nsquash )
    s.connect( s.pipe_ctrl_D.pipereg_en, s.pipe_en_D           )

    s.pipe_decode_ctrl_D = ParcProc5stBypassDecodeCtrl()

    s.decode_inst_mux = Mux( 32, 2 )

    s.connect( s.decode_inst_mux.in_[NVAL], UNOP                      )
    s.connect( s.decode_inst_mux.in_[VAL],  s.inst_D                  )
    s.connect( s.decode_inst_mux.sel,       s.pipe_ctrl_D.pipereg_val )

    s.connect( s.pipe_decode_ctrl_D.inst_bits, s.decode_inst_mux.out )

    s.enable_x_stage_D = Wire( 1 )

    @s.combinational
    def comb_D():

      # coprocessor 2

      s.to_cp2_val.value = s.pipe_decode_ctrl_D.cs[ CP2_WEN ]

      # idempotent control signals

      s.op0_mux_sel_D.value = s.pipe_decode_ctrl_D.cs[ OP0_MUX_SEL ].value
      s.op1_mux_sel_D.value = s.pipe_decode_ctrl_D.cs[ OP1_MUX_SEL ].value
      s.muldiv_fn_D.value   = s.pipe_decode_ctrl_D.cs[ MD_FN ].value

      # bypass rs/op0

      rs_bypass_X = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RS_EN ].value
                      and s.pipe_ctrl_X.pipereg_val.value
                      and s.pipe_cs_X[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                            == s.pipe_cs_X[ RF_WADDR ].value)
                      and s.pipe_cs_X[ RF_WADDR ].value != 0 )

      rs_bypass_M = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RS_EN ].value
                      and s.pipe_ctrl_M.pipereg_val.value
                      and s.pipe_cs_M[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                            == s.pipe_cs_M[ RF_WADDR ].value)
                      and s.pipe_cs_M[ RF_WADDR ].value != 0 )

      rs_bypass_W = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RS_EN ].value
                      and s.pipe_ctrl_W.pipereg_val.value
                      and s.pipe_cs_W[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                            == s.pipe_cs_W[ RF_WADDR ].value)
                      and s.pipe_cs_W[ RF_WADDR ].value != 0 )

      if   rs_bypass_X: s.op0_byp_mux_sel_D.value = RD0_BYP_X
      elif rs_bypass_M: s.op0_byp_mux_sel_D.value = RD0_BYP_M
      elif rs_bypass_W: s.op0_byp_mux_sel_D.value = RD0_BYP_W
      else:             s.op0_byp_mux_sel_D.value = RD0_BYP_RF

      # bypass rt/op1

      rt_bypass_X = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RT_EN ].value
                      and s.pipe_ctrl_X.pipereg_val.value
                      and s.pipe_cs_X[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                            == s.pipe_cs_X[ RF_WADDR ].value)
                      and s.pipe_cs_X[ RF_WADDR ].value != 0 )

      rt_bypass_M = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RT_EN ].value
                      and s.pipe_ctrl_M.pipereg_val.value
                      and s.pipe_cs_M[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                            == s.pipe_cs_M[ RF_WADDR ].value)
                      and s.pipe_cs_M[ RF_WADDR ].value != 0 )

      rt_bypass_W = (     s.pipe_ctrl_D.pipereg_val.value
                      and s.pipe_decode_ctrl_D.cs[ RT_EN ].value
                      and s.pipe_ctrl_W.pipereg_val.value
                      and s.pipe_cs_W[ RF_WEN ].value
                      and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                            == s.pipe_cs_W[ RF_WADDR ].value)
                      and s.pipe_cs_W[ RF_WADDR ].value != 0 )

      if   rt_bypass_X: s.op1_byp_mux_sel_D.value = RD1_BYP_X
      elif rt_bypass_M: s.op1_byp_mux_sel_D.value = RD1_BYP_M
      elif rt_bypass_W: s.op1_byp_mux_sel_D.value = RD1_BYP_W
      else:             s.op1_byp_mux_sel_D.value = RD1_BYP_RF
      # ostall

      is_inst_X_Load = ( s.inst_X.value == isa.LB
                      or s.inst_X.value == isa.LBU
                      or s.inst_X.value == isa.LH
                      or s.inst_X.value == isa.LHU
                      or s.inst_X.value == isa.LW )

      is_inst_X_mfc2 = s.inst_X.value == isa.MFC2
      
      data_hazard_stall_X =  \
        ( s.pipe_ctrl_D.pipereg_val.value and
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ].value
              and s.pipe_ctrl_X.pipereg_val.value
              and s.pipe_cs_X[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                    ==  s.pipe_cs_X[ RF_WADDR ].value )
              and s.pipe_cs_X[ RF_WADDR ].value != 0
              and (is_inst_X_Load or is_inst_X_mfc2 ))
          or
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ].value
              and s.pipe_ctrl_X.pipereg_val.value
              and s.pipe_cs_X[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                    ==  s.pipe_cs_X[ RF_WADDR ].value )
              and s.pipe_cs_X[ RF_WADDR ].value != 0
              and (is_inst_X_Load or is_inst_X_mfc2))
          )
        )

      data_hazard_stall_Y =  \
        ( s.pipe_ctrl_D.pipereg_val.value and
        # read-after-write rs
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ]
              and s.scoreboard_Y[ s.pipe_decode_ctrl_D.cs[ RS_RADDR ] ]
            )
          or
        # read-after-write rt
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ]
              and s.scoreboard_Y[ s.pipe_decode_ctrl_D.cs[ RT_RADDR ] ]
            )
          or
        # write-after-write rf
            (     s.pipe_decode_ctrl_D.cs[ RF_WEN ]
              and s.scoreboard_Y[ s.pipe_decode_ctrl_D.cs[ RF_WADDR ] ]
            )
          )
        )

      is_inst_M_mfc2 = s.inst_M.value == isa.MFC2

      data_hazard_stall_M = \
        ( s.pipe_ctrl_D.pipereg_val.value and
          ( (     s.pipe_decode_ctrl_D.cs[ RS_EN ].value
              and s.pipe_ctrl_M.pipereg_val.value
              and s.pipe_cs_M[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RS_RADDR ].value
                    ==  s.pipe_cs_M[ RF_WADDR ].value )
              and s.pipe_cs_M[ RF_WADDR ].value != 0
              and is_inst_M_mfc2 )
          or
            (     s.pipe_decode_ctrl_D.cs[ RT_EN ].value
              and s.pipe_ctrl_M.pipereg_val.value
              and s.pipe_cs_M[ RF_WEN ].value
              and ( s.pipe_decode_ctrl_D.cs[ RT_RADDR ].value
                    ==  s.pipe_cs_M[ RF_WADDR ].value )
              and s.pipe_cs_M[ RF_WADDR ].value != 0
              and is_inst_M_mfc2)
          )
        )

      data_hazard_stall = \
        (   data_hazard_stall_X
         or data_hazard_stall_Y
         or data_hazard_stall_M
        )

      struct_hazard_mult_X = (
        s.pipe_ctrl_D.pipereg_val.value and (
        # Multiplier Unit
        ( not s.muldivreq_rdy_D.value
          and s.pipe_decode_ctrl_D.cs[ MD_EN ].value
        ) or
        # Coprocessor Write (mtc2)
        ( not s.to_cp2_rdy
          and s.to_cp2_val
        )))

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

      # don't enable X stage if this is a multiply, use Y stage instead

      #s.enable_x_stage_D.value = s.pipe_ctrl_D.nvalid
      s.enable_x_stage_D.value = s.pipe_ctrl_D.nvalid and \
          s.pipe_decode_ctrl_D.cs[ MD_FN ] != md_mul

      # no architectural state modifications

    #-------------------------------------------------------------------
    # X <- D
    #-------------------------------------------------------------------
    # control signal register at the start of X stage

    s.cp2_go_X = Wire( 1 )

    @s.posedge_clk
    def seq_DX():

      if s.pipe_ctrl_X.pipereg_en.value:
        s.pipe_cs_X.next = s.pipe_decode_ctrl_D.cs.value
        s.inst_X.next    = s.pipe_decode_ctrl_D.inst.value
        s.cp2_go_X.next  = s.to_cp2_val and s.cp2_go_D
      else:
        s.pipe_cs_X.next = s.pipe_cs_X.value
        s.inst_X.next    = s.inst_X.value
        s.cp2_go_X.next  = s.cp2_go_X

    #-------------------------------------------------------------------
    # Y Stage
    #-------------------------------------------------------------------

    s.pipe_val_Y    = Wire[4]( 1 )
    s.pipe_cs_Y     = Wire[4]( CS_WIDTH )
    s.scoreboard_Y  = Wire( 32 )

    @s.posedge_clk
    def seq_Y():

      cp2_stall_X = \
        ( s.pipe_ctrl_X.pipereg_val
          and not s.from_cp2_rdy
          and s.cp2_go_X
        )
      #if not WB stall
      if True:

        s.pipe_val_Y[0].next = s.mul_enq
        s.pipe_val_Y[1].next = s.pipe_val_Y[0]
        s.pipe_val_Y[2].next = s.pipe_val_Y[1]
        s.pipe_val_Y[3].next = s.pipe_val_Y[2]

        s.pipe_cs_Y[0].next = s.pipe_decode_ctrl_D.cs if s.mul_enq else 0
        s.pipe_cs_Y[1].next = s.pipe_cs_Y[0]
        s.pipe_cs_Y[2].next = s.pipe_cs_Y[1]
        s.pipe_cs_Y[3].next = s.pipe_cs_Y[2]

        if       s.mul_enq and not s.mul_deq:
          s.scoreboard_Y[ s.mul_enq_waddr ].next = 1
        elif not s.mul_enq and     s.mul_deq:
          s.scoreboard_Y[ s.mul_deq_waddr ].next = 0
        elif     s.mul_enq and     s.mul_deq and not s.scoreboard_hzd:
          s.scoreboard_Y[ s.mul_enq_waddr ].next = 1
          s.scoreboard_Y[ s.mul_deq_waddr ].next = 0

    s.mul_enq        = Wire( 1 )
    s.mul_enq_waddr  = Wire( 5 )
    s.scoreboard_hzd = Wire( 1 )

    @s.combinational
    def comb_Y1():
      s.mul_enq.value = s.muldivreq_val_D  and s.muldivreq_rdy_D and \
                        s.pipe_decode_ctrl_D.cs[ MD_FN ] == md_mul

      s.mul_enq_waddr.value  = s.pipe_decode_ctrl_D.cs[ RF_WADDR ]
      s.scoreboard_hzd.value = s.mul_enq_waddr == s.mul_deq_waddr

    s.mul_deq       = Wire( 1 )
    s.mul_deq_waddr = Wire( 5 )

    @s.combinational
    def comb_Y3():

      s.mul_deq.value = s.muldivresp_val_X and s.muldivresp_rdy_X and \
                        s.pipe_val_Y[3]

      s.mul_deq_waddr.value = s.pipe_cs_Y[3][ RF_WADDR ]
      s.rf_waddr_W[1].value = s.pipe_cs_Y[3][ RF_WADDR ]
      s.rf_wen_W  [1].value = s.pipe_val_Y[3]  and \
                              s.muldivresp_val_X and s.muldivresp_rdy_X

    #-------------------------------------------------------------------
    # X Stage
    #-------------------------------------------------------------------

    s.pipe_ctrl_X = PipeCtrl()

    #s.connect( s.pipe_ctrl_X.pvalid,     s.pipe_ctrl_D.nvalid  )
    s.connect( s.pipe_ctrl_X.pvalid,     s.enable_x_stage_D    )
    s.connect( s.pipe_ctrl_X.pstall,     s.pipe_ctrl_D.nstall  )
    s.connect( s.pipe_ctrl_X.psquash,    s.pipe_ctrl_D.nsquash )
    s.connect( s.pipe_ctrl_X.pipereg_en, s.pipe_en_X           )

    s.pipe_cs_X = Wire( CS_WIDTH )
    s.inst_X    = Wire( 8 )

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

      # ostall signal

      cp2_busy_stall_X = \
        ( s.pipe_ctrl_X.pipereg_val
          and not s.from_cp2_rdy
          and s.cp2_go_X
        )

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
      = ( dmemreq_busy_stall_X or
          muldiv_busy_stall_X  or
          cp2_busy_stall_X )

      # muldivresp_rdy calculations

      s.muldivresp_rdy_X.value = not s.pipe_ctrl_X.nstall \
                                 or  s.pipe_val_Y[3]

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

    # pipe_ctrl_M

    s.pipe_ctrl_M = PipeCtrl()

    s.connect( s.pipe_ctrl_M.pvalid,     s.pipe_ctrl_X.nvalid  )
    s.connect( s.pipe_ctrl_M.pstall,     s.pipe_ctrl_X.nstall  )
    s.connect( s.pipe_ctrl_M.psquash,    s.pipe_ctrl_X.nsquash )
    s.connect( s.pipe_ctrl_M.pipereg_en, s.pipe_en_M           )

    s.pipe_cs_M = Wire( CS_WIDTH )
    s.inst_M    = Wire( 8 )

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

    # pipe_ctrl_W

    s.pipe_ctrl_W = PipeCtrl()

    s.connect( s.pipe_ctrl_W.pvalid,     s.pipe_ctrl_M.nvalid  )
    s.connect( s.pipe_ctrl_W.pstall,     s.pipe_ctrl_M.nstall  )
    s.connect( s.pipe_ctrl_W.psquash,    s.pipe_ctrl_M.nsquash )
    s.connect( s.pipe_ctrl_W.pipereg_en, s.pipe_en_W           )

    s.pipe_cs_W = Wire( CS_WIDTH )
    s.inst_W    = Wire( 8 )

    @s.combinational
    def comb_W():

      # idempotent control signals

      s.rf_waddr_W[0].value = s.pipe_cs_W[ RF_WADDR ].value

      # osquash signal

      s.pipe_ctrl_W.osquash.value = 0

      is_inst_W_mfc2 = s.inst_W == isa.MFC2

      s.pipe_ctrl_W.ostall.value  = \
          ( is_inst_W_mfc2 and not s.from_cp2_val and
            s.pipe_ctrl_W.pipereg_val)

      #s.from_cp2_rdy.value = is_inst_W_mfc2
      s.wb_mux_W_sel.value = is_inst_W_mfc2
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

        s.from_cp2_rdy.value = is_inst_W_mfc2

        s.rf_wen_W[0].value = s.pipe_cs_W[ RF_WEN ].value

      else:
        s.from_cp2_rdy.value = 0
        s.cp0_status_wen_W.value = 0
        s.cp0_stats_wen_W.value  = 0
        s.rf_wen_W[0].value = 0
