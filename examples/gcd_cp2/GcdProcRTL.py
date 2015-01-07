#=========================================================================
# GcdProcRTL
#=========================================================================

from __future__ import print_function

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import Mux, regs, arith

# Constants

y = Bits(1, 1)
n = Bits(1, 0)

a_mux_sel_in  = Bits(2, 0)
a_mux_sel_sub = Bits(2, 1)
a_mux_sel_b   = Bits(2, 2)
a_mux_sel_x   = Bits(2, 0)

b_mux_sel_a   = Bits(1, 0)
b_mux_sel_in  = Bits(1, 1)
b_mux_sel_x   = Bits(1, 0)
    
A_MUX_SEL_NBITS = 2
A_MUX_SEL_IN    = 0
A_MUX_SEL_SUB   = 1
A_MUX_SEL_B     = 2
A_MUX_SEL_C     = 3
A_MUX_SEL_X     = 0

B_MUX_SEL_NBITS = 1
B_MUX_SEL_A     = 0
B_MUX_SEL_IN    = 1
B_MUX_SEL_X     = 0

#=========================================================================
# GCD Co-Proc RTL Datapath
#=========================================================================
class GcdProcDpath( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s, cpu_ifc_types ):

    s.cpu_ifc_req  = InValRdyBundle ( cpu_ifc_types.req  )
    s.cpu_ifc_resp = OutValRdyBundle( cpu_ifc_types.resp )

    size = cpu_ifc_types.req.data
    print( size, type(size) )
    
    s.cs      = InPort ( CtrlSignals()   )
    s.ss      = OutPort( StatusSignals() )

    # Interface wires

    s.in_msg_a  = Wire(size)
    s.in_msg_b  = Wire(size)
    s.out_msg   = Wire(size)

    #-----------------------------------------------------------------------
    # Connectivity and Logic
    #-----------------------------------------------------------------------
    print( s.cpu_ifc_req.msg.data.nbits )
    print( s.in_msg_a.nbits )
    s.connect( s.cpu_ifc_req.msg.data , s.in_msg_a ) 
    s.connect( s.cpu_ifc_req.msg.data , s.in_msg_b ) 
    s.connect( s.cpu_ifc_resp.msg.data, s.out_msg  ) 
   
    #---------------------------------------------------------------------
    # Datapath Structural Composition
    #---------------------------------------------------------------------

    s.sub_out   = Wire(size)
    s.b_reg_out = Wire(size)

    # A mux

    s.a_mux = m = Mux( size, 4 )
    s.connect_dict({
      m.sel                  : s.cs.a_mux_sel,
      m.in_[ A_MUX_SEL_IN  ] : s.in_msg_a,
      m.in_[ A_MUX_SEL_SUB ] : s.sub_out,
      m.in_[ A_MUX_SEL_B   ] : s.b_reg_out,
      m.in_[ A_MUX_SEL_C   ] : s.b_reg_out,
    })

    # A register

    s.a_reg = m = regs.RegEn(size)
    s.connect_dict({
      m.en    : s.cs.a_reg_en,
      m.in_   : s.a_mux.out,
    })

    # B mux

    s.b_mux = m = Mux( size, 2 )
    s.connect_dict({
      m.sel                 : s.cs.b_mux_sel,
      m.in_[ B_MUX_SEL_A  ] : s.a_reg.out,
      m.in_[ B_MUX_SEL_IN ] : s.in_msg_b,
    })

    # B register

    s.b_reg = m = regs.RegEn(size)
    s.connect_dict({
      m.en    : s.cs.b_reg_en,
      m.in_   : s.b_mux.out,
      m.out   : s.b_reg_out,
    })


    # Zero compare

    s.b_zero = m = arith.ZeroComparator(size)
    s.connect_dict({
      m.in_ : s.b_reg.out,
      m.out : s.ss.is_b_zero,
    })

    # Less-than comparator

    s.a_lt_b = m = arith.LtComparator(size)
    s.connect_dict({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.ss.is_a_lt_b
    })

    # Subtractor

    s.sub = m = arith.Subtractor(size)
    s.connect_dict({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.sub_out,
    })

    # connect to output port

    s.connect( s.sub.out, s.out_msg )
  
  def elaborate_logic( s ):
    pass

#=========================================================================
# GCD Unit RTL Control
#=========================================================================
class GcdProcCtrl( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s, cpu_ifc_types ):
    
    s.cpu_ifc_req  = InValRdyBundle  ( cpu_ifc_types.req  )
    s.cpu_ifc_resp = OutValRdyBundle ( cpu_ifc_types.resp  )
    
    s.ss      = InPort( StatusSignals() )
    s.cs      = OutPort ( CtrlSignals() )
    
    # Interface ports

    s.in_val    = Wire (1)
    s.in_rdy    = Wire (1)

    s.out_val   = Wire (1)
    s.out_rdy   = Wire (1)

    # State element

    s.STATE_IDLE = 0
    s.STATE_LOAD = 1
    s.STATE_CALC = 2
    s.STATE_DONE = 3

    s.state = regs.RegRst( 2, reset_value = s.STATE_IDLE )
    s.ctrl_msg = Wire(cpu_ifc_types.req.ctrl_msg)

  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):
    
    s.connect( s.cpu_ifc_req.msg.ctrl_msg, s.ctrl_msg ) 
    s.connect( s.cpu_ifc_req.val,  s.in_val  ) 
    s.connect( s.cpu_ifc_req.rdy,  s.in_rdy  ) 
    s.connect( s.cpu_ifc_resp.val, s.out_val ) 
    s.connect( s.cpu_ifc_resp.rdy, s.out_rdy ) 

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
          next_state = s.STATE_LOAD
      
      # Transistions out of CALC state
      if ( curr_state == s.STATE_LOAD ):
        if ( s.in_val and s.in_rdy ):
          if ( s.ctrl_msg == 0 ):
            next_state = s.STATE_CALC

      # Transistions out of CALC state

      if ( curr_state == s.STATE_CALC ):
        if ( not s.ss.is_a_lt_b and s.ss.is_b_zero ):
          next_state = s.STATE_DONE

      # Transistions out of DONE state

      if ( curr_state == s.STATE_DONE ):
        if ( s.out_val and s.out_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    s.ctrl_signals = Wire(5)
    s.a_reg_en     = Wire(1)
    s.b_reg_en     = Wire(1)
    s.swap         = Wire(1)
    s.done         = Wire(1)

    @s.combinational
    def state_to_ctrl():

      current_state = s.state.out
      
      s.a_reg_en = y if s.ctrl_msg == 1 else n
      s.b_reg_en = y if s.ctrl_msg == 2 else n
        
      s.swap = s.ss.is_a_lt_b
      s.done = not s.ss.is_a_lt_b and s.ss.is_b_zero
      if current_state == s.STATE_CALC:
        s.a_reg_en = y if not s.done else n
        s.b_reg_en = y if not s.done else n
      #                                                         a_mux_sel   a_reg_en     b_mux_sel  b_reg_en
      if   current_state == s.STATE_IDLE:        cs = concat(a_mux_sel_in , s.a_reg_en, b_mux_sel_in, s.b_reg_en)
      elif current_state == s.STATE_LOAD:        cs = concat(a_mux_sel_in , s.a_reg_en, b_mux_sel_in, s.b_reg_en)
      elif current_state == s.STATE_CALC:
        if s.swap:                               cs = concat(a_mux_sel_b  , s.a_reg_en, b_mux_sel_a , s.b_reg_en)
        else:                                    cs = concat(a_mux_sel_sub, s.a_reg_en, b_mux_sel_x ,          n)
      elif current_state == s.STATE_DONE:        cs = concat(a_mux_sel_x  ,          n, b_mux_sel_x ,          n)
      
      s.ctrl_signals.value = cs
      
      s.in_rdy.value  = current_state == s.STATE_IDLE or current_state == s.STATE_LOAD
      s.out_val.value = current_state == s.STATE_DONE
      
      s.cs.a_mux_sel.value = s.ctrl_signals[3:5]
      s.cs.a_reg_en .value = s.ctrl_signals[2]
      s.cs.b_mux_sel.value = s.ctrl_signals[1]
      s.cs.b_reg_en .value = s.ctrl_signals[0]
      
#=========================================================================
# GCD Unit RTL Model
#=========================================================================
class GcdProcRTL( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s, cpu_ifc_types ):

    s.cpu_ifc_req  = InValRdyBundle ( cpu_ifc_types.req  )
    s.cpu_ifc_resp = OutValRdyBundle( cpu_ifc_types.resp )
    
    #---------------------------------------------------------------------
    # Connectivity and Logic
    #---------------------------------------------------------------------
    
    # connect input/output ports with datapath and control logic

    s.dpath = GcdProcDpath( cpu_ifc_types )
    s.ctrl  = GcdProcCtrl( cpu_ifc_types )

    s.connect( s.cpu_ifc_req , s.dpath.cpu_ifc_req  )
    s.connect( s.cpu_ifc_resp, s.dpath.cpu_ifc_resp )
    s.connect( s.cpu_ifc_req , s.ctrl.cpu_ifc_req   )
    s.connect( s.cpu_ifc_resp, s.ctrl.cpu_ifc_resp  )

    # connect status/control signals

    s.connect( s.dpath.ss, s.ctrl.ss )
    s.connect( s.ctrl.cs, s.dpath.cs )

  #-----------------------------------------------------------------------
  # Line Tracing
  #-----------------------------------------------------------------------
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I "
    if s.ctrl.state.out == s.ctrl.STATE_LOAD:
      state_str = "L "
    if s.ctrl.state.out == s.ctrl.STATE_CALC:
      if s.ctrl.ss.is_a_lt_b:
        state_str = "Cs"
      else:
        state_str = "C-"
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "D "

    return "{} ({} {} {}) {}" \
        .format( str(s.cpu_ifc_req.msg), s.dpath.a_reg.out,
                 s.dpath.b_reg.out, state_str, s.cpu_ifc_resp.msg )

  def elaborate_logic( s ):
    pass

#------------------------------------------------------------------------------
# CtrlSignals
#------------------------------------------------------------------------------
class CtrlSignals( BitStructDefinition ):
  def __init__( s ):

    s.a_mux_sel = BitField  (A_MUX_SEL_NBITS)
    s.a_reg_en  = BitField  (1)
    s.b_mux_sel = BitField  (B_MUX_SEL_NBITS)
    s.b_reg_en  = BitField  (1)

#------------------------------------------------------------------------------
# StatusSignals
#------------------------------------------------------------------------------
class StatusSignals( BitStructDefinition ):

  def __init__(s):

    s.is_b_zero = BitField (1)
    s.is_a_lt_b = BitField (1)
