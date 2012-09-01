#=========================================================================
# GCD
#=========================================================================

from pymtl import *

class GcdDpath (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits=16 ):

    # in/out ports

    s.in_A      = InPort( nbits )
    s.in_B      = InPort( nbits )
    s.out       = OutPort( nbits )

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = InPort( 2 )
    s.a_reg_en  = InPort( 1 )
    s.b_mux_sel = InPort( 1 )
    s.b_reg_en  = InPort( 1 )

    # Status signals (dpath -> ctrl)

    s.is_b_zero = OutPort( 1 )
    s.is_a_lt_b = OutPort( 1 )

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    s.sub_out   = Wire( nbits )
    s.b_reg_out = Wire( nbits )

    # A mux

    s.a_mux = m = Mux3( nbits )
    connect({
      m.sel : s.a_mux_sel,
      m.in0 : s.in_A,
      m.in1 : s.sub_out,
      m.in2 : s.b_reg_out,
    })

    # A register

    s.a_reg = m = Reg( nbits )
    connect({
      m.en    : s.a_reg_en,
      m.in_   : s.a_mux.out,
    })

    # B mux

    s.b_mux = m = Mux2( nbits )
    connect({
      m.sel : s.b_mux_sel,
      m.in0 : s.a_reg.out,
      m.in1 : s.in_B,
    })

    # B register

    s.b_reg = m = Reg( nbits )
    connect({
      m.en    : s.b_reg_en,
      m.in_   : s.b_mux.out,
      m.out   : s.b_reg_out,
    })

    # Zero compare

    s.b_zero = m = CmpZero( nbits )
    connect({
      m.in_ : s.b_mux.out,
      m.out : s.is_b_zero,
    })

    # Less-than comparator

    s.a_lt_b = m = CmpLT( nbits )
    connect({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.is_a_lt_b
    })

    # Subtractor

    s.sub = m = Subtractor( nbits )
    connect({
      m.in0 : s.a_reg.out,
      m.in1 : s.b_reg.out,
      m.out : s.sub_out,
    })

    # Connect to output port

    s.sub.out <> s.out

