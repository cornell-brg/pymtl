#=========================================================================
# Lab 2 - ParcProc5stStall
#=========================================================================
# parc processor 5 stage stalling pipeline

from   new_pymtl import *
from   new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle
import new_pmlib

import ParcISA as isa

from ParcProc5stStallCtrl  import ParcProc5stStallCtrl
from ParcProc5stStallDpath import ParcProc5stStallDpath
import new_pmlib.mem_msgs as mem_msgs
#import plab2_proc_v1.mem_msgs as mem_msgs

#-------------------------------------------------------------------------
# parc processor 5 stage stalling pipeline
#-------------------------------------------------------------------------

class ParcProc5stStall( Model ):

  def __init__( s, reset_vector = 0 ):

    s.reset_vector = reset_vector
    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    mreq  = mem_msgs.MemReqParams ( 32, 32 )
    mresp = mem_msgs.MemRespParams( 32 )

    # TestProcManager Interface

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Instruction Memory Request Port

    s.imemreq = OutValRdyBundle( mreq.nbits )

    # Instruction Memory Response Port

    s.imemresp = InValRdyBundle( mresp.nbits )

    # Data Memory Request Port

    s.dmemreq = OutValRdyBundle( mreq.nbits )

    # Data Memory Response Port

    s.dmemresp = InValRdyBundle( mresp.nbits )

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    s.ctrl  = ParcProc5stStallCtrl  ( )
    s.dpath = ParcProc5stStallDpath ( reset_vector = s.reset_vector )

    # Connect ctrl

    s.connect( s.ctrl.go,           s.go           )
    s.connect( s.ctrl.num_insts,    s.num_insts    )
    s.connect( s.ctrl.imemreq_val,  s.imemreq.val  )
    s.connect( s.ctrl.imemreq_rdy,  s.imemreq.rdy  )
    s.connect( s.ctrl.dmemreq_val,  s.dmemreq.val  )
    s.connect( s.ctrl.dmemreq_rdy,  s.dmemreq.rdy  )
    s.connect( s.ctrl.dmemresp_val, s.dmemresp.val )
    s.connect( s.ctrl.dmemresp_rdy, s.dmemresp.rdy )

    # Connect dpath

    s.connect( s.dpath.status,       s.status       )
    s.connect( s.dpath.stats_en,     s.stats_en     )
    s.connect( s.dpath.imemreq_msg,  s.imemreq.msg  )
    s.connect( s.dpath.imemresp_val, s.imemresp.val )
    s.connect( s.dpath.imemresp_rdy, s.imemresp.rdy )
    s.connect( s.dpath.imemresp_msg, s.imemresp.msg )
    s.connect( s.dpath.dmemreq_msg,  s.dmemreq.msg  )
    s.connect( s.dpath.dmemresp_msg, s.dmemresp.msg )

    # Connect control signals (ctrl -> dpath)

    s.connect( s.ctrl.pc_mux_sel_P,         s.dpath.pc_mux_sel_P        )
    s.connect( s.ctrl.pc_reg_wen_P,         s.dpath.pc_reg_wen_P        )
    s.connect( s.ctrl.pc_bypass_mux_sel_P,  s.dpath.pc_bypass_mux_sel_P )
    s.connect( s.ctrl.pipe_en_F,            s.dpath.pipe_en_F           )
    s.connect( s.ctrl.pipe_en_D,            s.dpath.pipe_en_D           )
    s.connect( s.ctrl.drop_resp_F,          s.dpath.drop_resp_F         )
    s.connect( s.ctrl.imemresp_rdy_F,       s.dpath.imemresp_rdy_F      )
    s.connect( s.ctrl.op0_mux_sel_D,        s.dpath.op0_mux_sel_D       )
    s.connect( s.ctrl.op1_mux_sel_D,        s.dpath.op1_mux_sel_D       )
    s.connect( s.ctrl.muldiv_fn_D,          s.dpath.muldiv_fn_D         )
    s.connect( s.ctrl.muldivreq_val_D,      s.dpath.muldivreq_val_D     )
    s.connect( s.ctrl.pipe_en_X,            s.dpath.pipe_en_X           )
    s.connect( s.ctrl.alu_fn_X,             s.dpath.alu_fn_X            )
    s.connect( s.ctrl.execute_mux_sel_X,    s.dpath.execute_mux_sel_X   )
    s.connect( s.ctrl.muldivresp_rdy_X,     s.dpath.muldivresp_rdy_X    )
    s.connect( s.ctrl.dmemreq_type_X,       s.dpath.dmemreq_type_X      )
    s.connect( s.ctrl.dmemreq_len_X,        s.dpath.dmemreq_len_X       )
    s.connect( s.ctrl.pipe_en_M,            s.dpath.pipe_en_M           )
    s.connect( s.ctrl.dmemresp_sel_M,       s.dpath.dmemresp_sel_M      )
    s.connect( s.ctrl.wb_mux_sel_M,         s.dpath.wb_mux_sel_M        )
    s.connect( s.ctrl.pipe_en_W,            s.dpath.pipe_en_W           )
    s.connect( s.ctrl.cp0_status_wen_W,     s.dpath.cp0_status_wen_W    )
    s.connect( s.ctrl.cp0_stats_wen_W,      s.dpath.cp0_stats_wen_W     )
    s.connect( s.ctrl.rf_wen_W,             s.dpath.rf_wen_W            )
    s.connect( s.ctrl.rf_waddr_W,           s.dpath.rf_waddr_W          )

    # Connect status signals (ctrl <- dpath)

    s.connect( s.ctrl.imemresp_val_F,       s.dpath.imemresp_val_F      )
    s.connect( s.ctrl.inst_D,               s.dpath.inst_D              )
    s.connect( s.ctrl.muldivreq_rdy_D,      s.dpath.muldivreq_rdy_D     )
    s.connect( s.ctrl.br_cond_eq_X,         s.dpath.br_cond_eq_X        )
    s.connect( s.ctrl.br_cond_zero_X,       s.dpath.br_cond_zero_X      )
    s.connect( s.ctrl.br_cond_neg_X,        s.dpath.br_cond_neg_X       )
    s.connect( s.ctrl.muldivresp_val_X,     s.dpath.muldivresp_val_X    )
    s.connect( s.ctrl.stats_en,             s.dpath.stats_en            )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    #print(s.dpath.imemresp_msg)
    #print("snoop imemresp")
    #print(s.dpath.snoop_unit_F.in_.msg)
    
    #print(s.ctrl.pipe_decode_ctrl_D.inst.value == isa.MTC0) 
    #print(s.dpath.status)
    #print(s.dpath.res_reg_W.out)
    #print(s.dpath.wb_mux_M.out)
    #print(s.ctrl.cp0_status_wen_W)
    #print("imul_msg")
    #print(s.dpath.muldiv_X.in_.msg)
    #print("mul_in")
    #print(s.dpath.muldiv_X.out.msg)#intMul.in_.msg) 

    # Transactions in the pipeline

    # P stage

    if   s.ctrl.go_bit.value and not s.ctrl.imemreq_rdy.value:
      P_str = "{:^8s}".format( '#' )
    elif ( s.ctrl.go_bit.value and s.ctrl.pipe_ctrl_F.pstall.value
           and not s.ctrl.pipe_ctrl_F.psquash.value ) :
      P_str = "{:^8s}".format( '#' )
    elif s.ctrl.go_bit.value:
      P_str = "{:^8x}".format( s.imemreq.msg[34:66].value.uint() )
    else:
      P_str = "{:^8s}".format( ' ' )

    # F stage

    if not s.ctrl.pipe_ctrl_F.pipereg_val.value:
      F_str = "{:^8s}".format( ' ' )
    elif s.ctrl.pipe_ctrl_F.nsquash.value:
      F_str = "{:^8s}".format( '-' )
    elif s.ctrl.pipe_ctrl_F.pstall.value:
      F_str = "{:^8s}".format( '#' )
    else:
      F_str = "{:^8x}".format( s.dpath.pc_reg_F.out.value.uint() )

    # D stage

    if not s.ctrl.pipe_ctrl_D.pipereg_val.value:
      D_str = "{:^5s}".format( ' ' )
    elif s.ctrl.pipe_ctrl_D.nsquash.value:
      D_str = "{:^5s}".format( '-' )
    elif s.ctrl.pipe_ctrl_D.pstall.value:
      D_str = "{:^5s}".format( '#' )
    else:
      D_str = "{:^5s}".format(
         isa.inst_to_str[s.ctrl.pipe_decode_ctrl_D.inst.value.uint()] )

    # X stage

    if not s.ctrl.pipe_ctrl_X.pipereg_val.value:
      X_str = "{:^5s}".format( ' ' )
    elif s.ctrl.pipe_ctrl_X.nsquash.value:
      X_str = "{:^5s}".format( '-' )
    elif s.ctrl.pipe_ctrl_X.pstall.value:
      X_str = "{:^5s}".format( '#' )
    else:
      X_str = "{:^5s}".format(
         isa.inst_to_str[s.ctrl.inst_X.value.uint()] )

    # M stage

    if not s.ctrl.pipe_ctrl_M.pipereg_val.value:
      M_str = "{:^5s}".format( ' ' )
    elif s.ctrl.pipe_ctrl_M.nsquash.value:
      M_str = "{:^5s}".format( '-' )
    elif s.ctrl.pipe_ctrl_M.pstall.value:
      M_str = "{:^5s}".format( '#' )
    else:
      M_str = "{:^5s}".format(
         isa.inst_to_str[s.ctrl.inst_M.value.uint()] )

    # W stage

    if not s.ctrl.pipe_ctrl_W.pipereg_val.value:
      W_str = "{:^5s}".format( ' ' )
    elif s.ctrl.pipe_ctrl_W.nsquash.value:
      W_str = "{:^5s}".format( '-' )
    elif s.ctrl.pipe_ctrl_W.pstall.value:
      W_str = "{:^5s}".format( '#' )
    else:
      W_str = "{:^5s}".format(
         isa.inst_to_str[s.ctrl.inst_W.value.uint()] )

    pipeline_str = ( P_str + "|" + F_str + "|" + D_str + "|"
                   + X_str + "|" + M_str + "|"
                   + W_str )

    #return hex(s.dpath.alu_X.in0.value.uint())
    #return str(s.dpath.rf.line_trace())
    return pipeline_str
