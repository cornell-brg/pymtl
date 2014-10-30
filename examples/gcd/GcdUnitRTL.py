#=========================================================================
# GcdUnitRTL
#=========================================================================

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import Mux, RegEn, RegRst, arith

# Constants

A_MUX_SEL_NBITS = 2
A_MUX_SEL_IN    = 0
A_MUX_SEL_SUB   = 1
A_MUX_SEL_B     = 2
A_MUX_SEL_X     = 0

B_MUX_SEL_NBITS = 1
B_MUX_SEL_A     = 0
B_MUX_SEL_IN    = 1
B_MUX_SEL_X     = 0

#=========================================================================
# GCD Unit RTL Datapath
#=========================================================================
class GcdUnitDpath( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s ):

    # Interface ports

    s.in_msg_a  = InPort  (32)
    s.in_msg_b  = InPort  (32)
    s.out_msg   = OutPort (32)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = InPort  (A_MUX_SEL_NBITS)
    s.a_reg_en  = InPort  (1)
    s.b_mux_sel = InPort  (B_MUX_SEL_NBITS)
    s.b_reg_en  = InPort  (1)

    # Status signals (dpath -> ctrl)

    s.is_b_zero = OutPort (1)
    s.is_a_lt_b = OutPort (1)

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Datapath Structural Composition
    #---------------------------------------------------------------------

    s.sub_out   = Wire(32)
    s.b_reg_out = Wire(32)

    # A mux

    s.a_mux = m = Mux( 32, 3 )
    s.connect_dict({
      m.sel                  : s.a_mux_sel,
      m.in_[ A_MUX_SEL_IN  ] : s.in_msg_a,
      m.in_[ A_MUX_SEL_SUB ] : s.sub_out,
      m.in_[ A_MUX_SEL_B   ] : s.b_reg_out,
    })

    # A register

    s.a_reg = m = RegEn(32)
    s.connect_dict({
      m.en    : s.a_reg_en,
      m.in_   : s.a_mux.out,
    })

    # B mux

    s.b_mux = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                 : s.b_mux_sel,
      m.in_[ B_MUX_SEL_A  ] : s.a_reg.out,
      m.in_[ B_MUX_SEL_IN ] : s.in_msg_b,
    })

    # B register

    s.b_reg = m = RegEn(32)
    s.connect_dict({
      m.en    : s.b_reg_en,
      m.in_   : s.b_mux.out,
      m.out   : s.b_reg_out,
    })

    # Zero compare

    s.b_zero = m = arith.ZeroComparator(32)
    s.connect_dict({
      m.in_ : s.b_reg.out,
      m.out : s.is_b_zero,
    })

    # Less-than comparator

    s.a_lt_b = m = arith.LtComparator(32)
    s.connect_dict({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.is_a_lt_b
    })

    # Subtractor

    s.sub = m = arith.Subtractor(32)
    s.connect_dict({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.sub_out,
    })

    # connect to output port

    s.connect( s.sub.out, s.out_msg )

#=========================================================================
# GCD Unit RTL Control
#=========================================================================
class GcdUnitCtrl( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s ):

    # Interface ports

    s.in_val    = InPort  (1)
    s.in_rdy    = OutPort (1)

    s.out_val   = OutPort (1)
    s.out_rdy   = InPort  (1)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = OutPort (A_MUX_SEL_NBITS)
    s.a_reg_en  = OutPort (1)
    s.b_mux_sel = OutPort (1)
    s.b_reg_en  = OutPort (1)

    # Status signals (dpath -> ctrl)

    s.is_b_zero = InPort  (B_MUX_SEL_NBITS)
    s.is_a_lt_b = InPort  (1)

    # State element

    s.STATE_IDLE = 0
    s.STATE_CALC = 1
    s.STATE_DONE = 2

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state = s.state.out
      next_state = s.state.out

      # Transistions out of IDLE state

      if ( curr_state == s.STATE_IDLE ):
        if ( s.in_val and s.in_rdy ):
          next_state = s.STATE_CALC

      # Transistions out of CALC state

      if ( curr_state == s.STATE_CALC ):
        if ( not s.is_a_lt_b and s.is_b_zero ):
          next_state = s.STATE_DONE

      # Transistions out of DONE state

      if ( curr_state == s.STATE_DONE ):
        if ( s.out_val and s.out_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      current_state = s.state.out

      # In IDLE state we simply wait for inputs to arrive and latch them

      if current_state == s.STATE_IDLE:
        s.in_rdy.value    = 1
        s.out_val.value   = 0
        s.a_mux_sel.value = A_MUX_SEL_IN
        s.a_reg_en.value  = 1
        s.b_mux_sel.value = B_MUX_SEL_IN
        s.b_reg_en.value  = 1

      # In CALC state we iteratively swap/sub to calculate GCD

      elif current_state == s.STATE_CALC:

        swap = s.is_a_lt_b
        done = not s.is_a_lt_b and s.is_b_zero

        s.in_rdy.value    = 0
        s.out_val.value   = 0
        s.a_mux_sel.value = A_MUX_SEL_B if swap else A_MUX_SEL_SUB
        s.a_reg_en.value  = not done
        s.b_mux_sel.value = B_MUX_SEL_A
        s.b_reg_en.value  = swap and not done

      # In DONE state we simply wait for output transaction to occur

      elif current_state == s.STATE_DONE:
        s.in_rdy.value    = 0
        s.out_val.value   = 1
        s.a_mux_sel.value = A_MUX_SEL_X
        s.a_reg_en.value  = 0
        s.b_mux_sel.value = B_MUX_SEL_X
        s.b_reg_en.value  = 0


#=========================================================================
# GCD Unit RTL Model
#=========================================================================
class GcdUnitRTL( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s ):

    s.in_ = InValRdyBundle ( 64 )
    s.out = OutValRdyBundle( 32 )

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.dpath = GcdUnitDpath()
    s.ctrl  = GcdUnitCtrl()

    # connect input interface to dpath/ctrl

    s.connect( s.in_.msg[ 0:32], s.dpath.in_msg_a  )
    s.connect( s.in_.msg[32:64], s.dpath.in_msg_b  )

    s.connect( s.in_.val,        s.ctrl.in_val )
    s.connect( s.in_.rdy,        s.ctrl.in_rdy )

    # connect dpath/ctrl to output interface

    s.connect( s.dpath.out_msg, s.out.msg     )
    s.connect( s.ctrl.out_val,  s.out.val     )
    s.connect( s.ctrl.out_rdy,  s.out.rdy     )

    # connect status/control signals

    s.connect( s.dpath.a_mux_sel, s.ctrl.a_mux_sel )
    s.connect( s.dpath.a_reg_en,  s.ctrl.a_reg_en  )
    s.connect( s.dpath.b_mux_sel, s.ctrl.b_mux_sel )
    s.connect( s.dpath.b_reg_en,  s.ctrl.b_reg_en  )
    s.connect( s.dpath.is_b_zero, s.ctrl.is_b_zero )
    s.connect( s.dpath.is_a_lt_b, s.ctrl.is_a_lt_b )

  #-----------------------------------------------------------------------
  # Line Tracing
  #-----------------------------------------------------------------------
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I "
    if s.ctrl.state.out == s.ctrl.STATE_CALC:
      if s.ctrl.is_a_lt_b:
        state_str = "Cs"
      else:
        state_str = "C-"
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "D "

    return "{} ({} {} {}) {}" \
        .format( s.in_, s.dpath.a_reg.out,
                 s.dpath.b_reg.out, state_str, s.out )

