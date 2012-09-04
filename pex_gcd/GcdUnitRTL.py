#=========================================================================
# GcdUnitRTL
#=========================================================================

from pymtl import *
import pmlib

class GcdUnitDpath (Model):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Ports
    #---------------------------------------------------------------------

    # Interface ports

    s.in_msg_a  = InPort  (32)
    s.in_msg_b  = InPort  (32)
    s.out_msg   = OutPort (32)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = InPort  (2)
    s.a_reg_en  = InPort  (1)
    s.b_mux_sel = InPort  (1)
    s.b_reg_en  = InPort  (1)

    # Status signals (dpath -> ctrl)

    s.is_b_zero = OutPort (1)
    s.is_a_lt_b = OutPort (1)

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    s.sub_out   = Wire(32)
    s.b_reg_out = Wire(32)

    # A mux

    s.a_mux = m = pmlib.muxes.Mux3(32)
    connect({
      m.sel : s.a_mux_sel,
      m.in0 : s.in_msg_a,
      m.in1 : s.sub_out,
      m.in2 : s.b_reg_out,
    })

    # A register

    s.a_reg = m = pmlib.regs.RegEn(32)
    connect({
      m.en    : s.a_reg_en,
      m.in_   : s.a_mux.out,
    })

    # B mux

    s.b_mux = m = pmlib.muxes.Mux2(32)
    connect({
      m.sel : s.b_mux_sel,
      m.in0 : s.a_reg.out,
      m.in1 : s.in_msg_b,
    })

    # B register

    s.b_reg = m = pmlib.regs.RegEn(32)
    connect({
      m.en    : s.b_reg_en,
      m.in_   : s.b_mux.out,
      m.out   : s.b_reg_out,
    })

    # Zero compare

    s.b_zero = m = pmlib.arith.ZeroComparator(32)
    connect({
      m.in_ : s.b_reg.out,
      m.out : s.is_b_zero,
    })

    # Less-than comparator

    s.a_lt_b = m = pmlib.arith.LtComparator(32)
    connect({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.is_a_lt_b
    })

    # Subtractor

    s.sub = m = pmlib.arith.Subtractor(32)
    connect({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.sub_out,
    })

    # Connect to output port

    connect( s.sub.out, s.out_msg )

#=========================================================================
# GCD Control
#=========================================================================

class GcdUnitCtrl (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s ):

    # Interface ports

    s.in_val    = InPort  (1)
    s.in_rdy    = OutPort (1)

    s.out_val   = OutPort (1)
    s.out_rdy   = InPort  (1)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = OutPort (2)
    s.a_reg_en  = OutPort (1)
    s.b_mux_sel = OutPort (1)
    s.b_reg_en  = OutPort (1)

    # Status signals (dpath -> ctrl)

    s.is_b_zero = InPort  (1)
    s.is_a_lt_b = InPort  (1)

    # State element

    s.STATE_IDLE = 0
    s.STATE_CALC = 1
    s.STATE_DONE = 2

    s.state = pmlib.regs.RegRst( 2, reset_value = s.STATE_IDLE )

  #-----------------------------------------------------------------------
  # State transitions
  #-----------------------------------------------------------------------

  @combinational
  def state_transitions( s ):

    current_state = s.state.out.value
    next_state    = s.state.out.value

    # Transistions out of IDLE state

    if ( current_state == s.STATE_IDLE ):
      if ( s.in_val.value and s.in_rdy.value ):
        next_state = s.STATE_CALC

    # Transistions out of CALC state

    if ( current_state == s.STATE_CALC ):
      if ( not s.is_a_lt_b.value and s.is_b_zero.value ):
        next_state = s.STATE_DONE

    # Transistions out of DONE state

    if ( current_state == s.STATE_DONE ):
      if ( s.out_val.value and s.out_rdy.value ):
        next_state = s.STATE_IDLE

    s.state.in_.value = next_state

  #-----------------------------------------------------------------------
  # State outputs
  #-----------------------------------------------------------------------

  @combinational
  def state_outputs( s ):

    current_state = s.state.out.value

    # In IDLE state we simply wait for inputs to arrive and latch them in

    if current_state == s.STATE_IDLE:
      s.in_rdy.value    = 1
      s.out_val.value   = 0
      s.a_mux_sel.value = 0
      s.a_reg_en.value  = 1
      s.b_mux_sel.value = 1
      s.b_reg_en.value  = 1

    # In CALC state we iteratively swap/sub to calculate GCD

    elif current_state == s.STATE_CALC:

      swap = s.is_a_lt_b.value
      done = not s.is_a_lt_b.value and s.is_b_zero.value

      s.in_rdy.value    = 0
      s.out_val.value   = 0
      s.a_mux_sel.value = 2 if swap else 1
      s.a_reg_en.value  = not done
      s.b_mux_sel.value = 0
      s.b_reg_en.value  = swap and not done

    # In DONE state we simply wait for output transaction to occur

    elif current_state == s.STATE_DONE:
      s.in_rdy.value    = 0
      s.out_val.value   = 1
      s.a_mux_sel.value = 0
      s.a_reg_en.value  = 0
      s.b_mux_sel.value = 0
      s.b_reg_en.value  = 0

#=========================================================================
# GCD Unit
#=========================================================================

class GcdUnitRTL (Model):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Declare ports and wires
    #---------------------------------------------------------------------

    s.in_msg  = InPort  (64)
    s.in_val  = InPort  (1 )
    s.in_rdy  = OutPort (1 )

    s.out_msg = OutPort (32)
    s.out_val = OutPort (1 )
    s.out_rdy = InPort  (1 )

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    s.dpath = GcdUnitDpath()
    s.ctrl  = GcdUnitCtrl()

    # Connect input interface to dpath/ctrl

    connect( s.in_msg[ 0:32], s.dpath.in_msg_a  )
    connect( s.in_msg[32:64], s.dpath.in_msg_b  )

    connect( s.in_val,        s.ctrl.in_val )
    connect( s.in_rdy,        s.ctrl.in_rdy )

    # Connect dpath/ctrl to output interface

    connect( s.dpath.out_msg, s.out_msg     )
    connect( s.ctrl.out_val,  s.out_val     )
    connect( s.ctrl.out_rdy,  s.out_rdy     )

    # Connect ports with the same name in dpath and ctrl

    connect_auto( s.dpath, s.ctrl )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    out_str = \
      pmlib.valrdy.valrdy_to_str( self.out_msg.value,
        self.out_val.value, self.out_rdy.value )

    state_str = "? "
    if self.ctrl.state.out.value == self.ctrl.STATE_IDLE:
      state_str = "I "
    if self.ctrl.state.out.value == self.ctrl.STATE_CALC:
      if self.ctrl.is_a_lt_b.value:
        state_str = "Cs"
      else:
        state_str = "C-"
    if self.ctrl.state.out.value == self.ctrl.STATE_DONE:
      state_str = "D "

    return "{} ({} {} {}) {}" \
        .format( in_str, self.dpath.a_reg.out.value,
                 self.dpath.b_reg.out.value, state_str, out_str )

