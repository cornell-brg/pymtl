#==============================================================================
# arbiters.py
#==============================================================================
# This file contains a collection of various arbiter implementations.
#
# Based on the vc-Arbiters implementation

from pymtl     import *
from pclib.rtl import Mux, RegEnRst

#------------------------------------------------------------------------------
# RoundRobinArbiter
#------------------------------------------------------------------------------
class RoundRobinArbiter( Model ):

  def __init__(s, nreqs ):

    s.nreqs   = nreqs
    s.nreqsX2 = nreqs * 2

    # Interface Ports

    s.reqs   = InPort ( nreqs )
    s.grants = OutPort( nreqs )

  #----------------------------------------------------------------------------
  # elaborate_logic
  #----------------------------------------------------------------------------
  def elaborate_logic( s ):

    # priority enable

    s.priority_en = Wire( 1 )

    # priority register

    s.priority_reg = m = RegEnRst( s.nreqs, reset_value = 1 )
    s.connect( s.priority_reg.en, s.priority_en )

    s.connect_dict({
      m.en             : s.priority_en,
      m.in_[1:s.nreqs] : s.grants[0:s.nreqs-1],
      m.in_[0]         : s.grants[s.nreqs-1]
    })

    s.kills        = Wire( 2*s.nreqs + 1 )
    s.priority_int = Wire( 2*s.nreqs )
    s.reqs_int     = Wire( 2*s.nreqs )
    s.grants_int   = Wire( 2*s.nreqs )

    #--------------------------------------------------------------------------
    # comb
    #--------------------------------------------------------------------------
    @s.combinational
    def comb():

      s.kills[0].value = 1

      s.priority_int[      0:s.nreqs  ].value = s.priority_reg.out
      s.priority_int[s.nreqs:s.nreqsX2].value = 0
      s.reqs_int    [      0:s.nreqs  ].value = s.reqs
      s.reqs_int    [s.nreqs:s.nreqsX2].value = s.reqs

      # Calculate the kill chain
      for i in range( s.nreqsX2 ):

        # Set internal grants
        if s.priority_int[i].value:
          s.grants_int[i].value = s.reqs_int[i]
        else:
          s.grants_int[i].value = ~s.kills[i] & s.reqs_int[i]

        # Set kill signals
        if s.priority_int[i].value:
          s.kills[i+1].value = s.grants_int[i]
        else:
          s.kills[i+1].value = s.kills[i] | s.grants_int[i]

      # Assign the output ports
      for i in range( s.nreqs ):
        s.grants[i].value = s.grants_int[i] | s.grants_int[s.nreqs+i]

      # Set the priority enable
      s.priority_en.value = ( s.grants != 0 )


  #----------------------------------------------------------------------------
  # line_trace
  #----------------------------------------------------------------------------
  def line_trace(s):
    return "{} | {}".format( s.reqs, s.grants )

#------------------------------------------------------------------------------
# RoundRobinArbiterEn
#------------------------------------------------------------------------------
# Round Robin Arbiter model with an enable bit. When the aribter enable bit
# is set high, the arbitration takes place else the arbitration is
# disabled.
class RoundRobinArbiterEn( Model ):

  def __init__( s, nreqs ):

    s.nreqs = nreqs

    # Interface Ports

    s.en         = InPort  ( 1 )
    s.reqs       = InPort  ( nreqs )
    s.grants     = OutPort ( nreqs )

  def elaborate_logic( s ):

    ARB    = 1
    NO_ARB = 0

    # Request Mux

    s.reqs_mux   = m = Mux( s.nreqs, nports=2 )
    s.connect_dict({
      m.in_[NO_ARB] : 0,
      m.in_[ARB]    : s.reqs,
      m.sel         : s.en
    })

    ## round robin arbiter

    s.rr_arbiter = RoundRobinArbiter( s.nreqs )

    s.connect( s.rr_arbiter.reqs,   s.reqs_mux.out )
    s.connect( s.rr_arbiter.grants, s.grants       )

  def line_trace(s):
    return "{} | {}".format( s.reqs, s.grants )
