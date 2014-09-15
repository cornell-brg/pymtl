#=======================================================================
# IntDivIterRTL.py
#=======================================================================
# Python division when the result is expected to be negative, rounds it
# towards negative infinity as opposed to positive infinity. We use the
# division operator and cast it to an integer to get the right behavior.

#from __future__ import division
from new_pymtl  import *

from new_pmlib  import InValRdyBundle, OutValRdyBundle
from muldiv_msg import BitStructIndex

#-----------------------------------------------------------------------
# IntDivIterRTL
#-----------------------------------------------------------------------
class IntDivIterRTL( Model ):

  idx = BitStructIndex()

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    msgIdx= BitStructIndex()

    s.in_ = InValRdyBundle ( s.idx.length )
    s.out = OutValRdyBundle( 32 )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.ctrl  = IntDivIterCtrl()
    s.dpath = IntDivIterDpath()

    s.connect( s.in_,      s.ctrl.in_  )
    s.connect( s.out,      s.ctrl.out  )
    s.connect( s.in_,      s.dpath.in_ )
    s.connect( s.out,      s.dpath.out )
    s.connect( s.ctrl.c2d, s.dpath.c2d )

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):

    counter = s.ctrl.c2d.counter.uint()
    return "{} ({:2d} {}) {}".format( s.in_, counter, s.dpath.a_reg, s.out )

#-----------------------------------------------------------------------
# IntDivIterDpath
#-----------------------------------------------------------------------
class IntDivIterDpath( Model ):

  idx = BitStructIndex()

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    msgIdx = BitStructIndex()

    s.in_  = InValRdyBundle ( s.idx.length )
    s.out  = OutValRdyBundle( 32 )

    s.c2d  = DpathBundle()

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    #-------------------------------------------------------------------
    # pre_flop_comb_logic
    #-------------------------------------------------------------------

    s.counter_mux_out = Wire( 5 )

    s.div_sign_next   = Wire( 1 )
    s.rem_sign_next   = Wire( 1 )
    s.rem_sign        = Wire( 1 )

    s.unsigned_a      = Wire( 32 )
    s.unsigned_b      = Wire( 32 )

    s.a_mux_out       = Wire( 65 )
    s.b_in            = Wire( 65 )

    s.a               = Wire( 32 )
    s.b               = Wire( 32 )

    @s.combinational
    def pre_flop_comb_logic():

      # TODO: temporary inference when RHS is a slice of width > 1!
      #a = s.in_.msg[ s.idx.arg_A ]
      #b = s.in_.msg[ s.idx.arg_B ]
      s.a.value = s.in_.msg[ s.idx.arg_A ]
      s.b.value = s.in_.msg[ s.idx.arg_B ]

      # Counter Mux

      if   s.c2d.cntr_mux_sel == op_load:
        s.counter_mux_out.value = 31
      elif s.c2d.cntr_mux_sel == op_next:
        s.counter_mux_out.value = s.counter_reg - 1
      else:
        s.counter_mux_out.value = 0

      s.c2d.counter.value = s.counter_reg

      # Sign of Result

      s.div_sign_next.value = s.a[31] ^ s.b[31]
      s.rem_sign_next.value = s.a[31]

      s.c2d.div_sign.value  = s.div_sign_reg
      s.c2d.rem_sign.value  = s.rem_sign_reg

      # Unsigned Operands

      if s.a[31] & s.c2d.is_op_signed: s.unsigned_a.value = ~s.a + 1
      else:                            s.unsigned_a.value =  s.a

      if s.b[31] & s.c2d.is_op_signed: s.unsigned_b.value = ~s.b + 1
      else:                            s.unsigned_b.value =  s.b

      # Operand Muxes

      if   s.c2d.a_mux_sel == op_load: s.a_mux_out.value = s.unsigned_a
      elif s.c2d.a_mux_sel == op_next: s.a_mux_out.value = s.sub_mux_out
      else:                            s.a_mux_out.value = 0

      s.b_in.value = concat( Bits(1,0), s.unsigned_b, Bits(32,0) )

    #-------------------------------------------------------------------
    # sequential_logic
    #-------------------------------------------------------------------

    s.counter_reg  = Wire(  5 )
    s.div_sign_reg = Wire(  1 )
    s.rem_sign_reg = Wire(  1 )
    s.a_reg        = Wire( 65 )
    s.b_reg        = Wire( 65 )

    @s.posedge_clk
    def sequential_logic():

      if s.c2d.sign_en:
        s.div_sign_reg.next = s.div_sign_next
        s.rem_sign_reg.next = s.rem_sign_next

      if s.c2d.a_en:
        s.a_reg.next = s.a_mux_out

      if s.c2d.b_en:
        s.b_reg.next = s.b_in

      s.counter_reg.next = s.counter_mux_out

    #-------------------------------------------------------------------
    # post_flop_comb_logic
    #-------------------------------------------------------------------

    s.a_shift_out = Wire( 65 )
    s.sub_out     = Wire( 65 )
    s.sub_mux_out = Wire( 65 )

    s.div_mux_out = Wire( 32 )
    s.rem_mux_out = Wire( 32 )

    @s.combinational
    def post_flop_comb_logic():

      # Operand Shifter

      s.a_shift_out.value = s.a_reg << 1

      # Subtractor

      s.sub_out.value = s.a_shift_out - s.b_reg;

      if   s.c2d.sub_mux_sel == sub_next:
        s.sub_mux_out.value = concat( s.sub_out[1:65], Bits(1,1) )
      elif s.c2d.sub_mux_sel == sub_old:
        s.sub_mux_out.value = s.a_shift_out
      else:
        s.sub_mux_out.value = 0

      # Sign of Difference (was result negative?)

      s.c2d.diff_msb.value = s.sub_out[64]

      # Signed Result Muxes

      if   s.c2d.div_sign_mux_sel == sign_u:
        s.div_mux_out.value =  s.a_reg[0:32]
      elif s.c2d.div_sign_mux_sel == sign_s:
        s.div_mux_out.value = ~s.a_reg[0:32] + 1
      else:
        s.div_mux_out.value = 0

      if   s.c2d.rem_sign_mux_sel == sign_u:
        s.rem_mux_out.value =  s.a_reg[32:64]
      elif s.c2d.rem_sign_mux_sel == sign_s:
        s.rem_mux_out.value = ~s.a_reg[32:64] + 1
      else:
        s.rem_mux_out.value = 0

      # Final Result

      if s.c2d.result_mux_sel: s.out.msg.value = s.div_mux_out
      else:                    s.out.msg.value = s.rem_mux_out

#-----------------------------------------------------------------------
# IntDivIterCtrl
#-----------------------------------------------------------------------
class IntDivIterCtrl( Model ):

  idx = BitStructIndex()

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    msgIdx= BitStructIndex()

    s.in_ = InValRdyBundle ( s.idx.length )
    s.out = OutValRdyBundle( 32 )

    s.c2d = CtrlBundle()

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    IDLE = 0
    CALC = 1
    SIGN = 2

    #-------------------------------------------------------------------
    # state_update
    #-------------------------------------------------------------------

    fn_nbits = s.idx.muldiv_op.stop - s.idx.muldiv_op.start

    s.state  = Wire( 2 )
    s.fn_reg = Wire( fn_nbits )

    @s.posedge_clk
    def state_update():

      if s.reset:
        s.state.next = IDLE
      else:
        if s.fn_en:
          s.fn_reg.next = s.in_.msg[ s.idx.muldiv_op ]
        s.state.next = s.state_next


    #-------------------------------------------------------------------
    # state_update
    #-------------------------------------------------------------------

    s.state_next = Wire( 2 )

    @s.combinational
    def state_update():

      s.state_next.value = s.state

      if   s.state == IDLE and s.divreq_go:
        s.state_next.value = CALC

      elif s.state == CALC and s.is_calc_done:
        s.state_next.value = SIGN

      elif s.state == SIGN and s.divresp_go:
        s.state_next.value = IDLE

    #-------------------------------------------------------------------
    # set_outputs
    #-------------------------------------------------------------------

    s.fn           = Wire( fn_nbits )
    s.fn_en        = Wire( 1 )
    s.divreq_go    = Wire( 1 )
    s.divresp_go   = Wire( 1 )
    s.is_calc_done = Wire( 1 )

    @s.combinational
    def set_outputs():

      #                                divreq divresp sign a  b   fn cntr,    a
      #                                rdy    val     en   en en  en mux_sel, mux_sel
      if s.state == IDLE: cs = concat( y,     n,      y,   y, y,  y, op_load, op_load )
      if s.state == CALC: cs = concat( n,     n,      n,   y, n,  n, op_next, op_next )
      if s.state == SIGN: cs = concat( n,     y,      n,   n, n,  n, op_x,    op_x    )

      # Function

      if cs[5]: s.fn.value = s.in_.msg[ s.idx.muldiv_op ]
      else:     s.fn.value = s.fn_reg

      # Signal Parsing

      s.in_.rdy.value              = cs[7]
      s.out.val.value              = cs[6]
      s.c2d.sign_en.value          = cs[5]
      s.c2d.a_en.value             = cs[4]
      s.c2d.b_en.value             = cs[3]
      s.fn_en.value                = cs[2]
      s.c2d.cntr_mux_sel.value     = cs[1]
      s.c2d.is_op_signed.value     = s.fn == s.idx.DIV_OP or s.fn == s.idx.REM_OP
      s.c2d.a_mux_sel.value        = cs[0]
      s.c2d.sub_mux_sel.value      = s.c2d.diff_msb
      s.c2d.div_sign_mux_sel.value = s.c2d.div_sign and s.c2d.is_op_signed
      s.c2d.rem_sign_mux_sel.value = s.c2d.rem_sign and s.c2d.is_op_signed
      s.c2d.result_mux_sel.value   = s.fn == s.idx.DIV_OP or s.fn == s.idx.DIVU_OP

      # Transition Triggers

      s.divreq_go.value     = s.in_.val and s.in_.rdy
      s.divresp_go.value    = s.out.val and s.out.rdy
      s.is_calc_done.value  = s.c2d.counter == 0

#-----------------------------------------------------------------------
# Control Constants
#-----------------------------------------------------------------------

n        = Bits( 1, 0 )
y        = Bits( 1, 1 )

op_x     = Bits( 1, 0 )
op_load  = Bits( 1, 0 )
op_next  = Bits( 1, 1 )

sub_x    = Bits( 1, 0 )
sub_next = Bits( 1, 0 )
sub_old  = Bits( 1, 1 )

sign_x   = Bits( 1, 0 )
sign_u   = Bits( 1, 0 )
sign_s   = Bits( 1, 1 )

#-----------------------------------------------------------------------
# CtrlDpathBundle
#-----------------------------------------------------------------------
class CtrlDpathBundle( PortBundle ):

  def __init__( s ):

    # Status signals (dpath -> ctrl)

    s.counter              = InPort( 5 )
    s.div_sign             = InPort( 1 )
    s.rem_sign             = InPort( 1 )
    s.diff_msb             = InPort( 1 )

    # Control signals (ctrl -> dpath)

    s.sign_en              = OutPort( 1 )
    s.a_en                 = OutPort( 1 )
    s.b_en                 = OutPort( 1 )
    s.cntr_mux_sel         = OutPort( 1 )
    s.is_op_signed         = OutPort( 1 )
    s.a_mux_sel            = OutPort( 1 )
    s.sub_mux_sel          = OutPort( 1 )
    s.div_sign_mux_sel     = OutPort( 1 )
    s.rem_sign_mux_sel     = OutPort( 1 )
    s.result_mux_sel       = OutPort( 1 )

CtrlBundle, DpathBundle = create_PortBundles( CtrlDpathBundle )
