#=========================================================================
# arbiters
#=========================================================================
# This file contains a collection of various arbiter implementations.
#
# Note: Ported from pex_dac subproject which is based on the vc-Arbiters
# implementation

from   pymtl import *
import pmlib

#-------------------------------------------------------------------------
# Round Robin Arbiter
#-------------------------------------------------------------------------

class RoundRobinArbiter(Model):

  @capture_args
  def __init__(s, nreqs ):

    s.nreqs        = nreqs
    s.nreqsX2       = nreqs * 2

    # Interface Ports

    s.reqs         = InPort  (nreqs)
    s.grants       = OutPort (nreqs)

    # priority enable

    s.priority_en  = Wire( 1     )

    # priority register

    s.priority_reg = m = pmlib.regs.RegEnRst( nreqs,
                              reset_value = 1 )
    connect({
      m.en           : s.priority_en,
      m.in_[1:nreqs] : s.grants[0:nreqs-1],
      m.in_[0]       : s.grants[nreqs-1]
    })

    s.kills        = Wire( 2*s.nreqs + 1 )
    s.priority_int = Wire( 2*s.nreqs )
    s.reqs_int     = Wire( 2*s.nreqs )
    s.grants_int   = Wire( 2*s.nreqs )

  @combinational
  def comb(s):

    #2x_nreqs = 2 * s.nreqs

    s.kills[0].value                        = 1
    s.priority_int[0:s.nreqs].value         = s.priority_reg.out.value
    s.priority_int[s.nreqs:s.nreqsX2].value = 0
    #s.priority_int[s.nreqs:2*s.nreqs].value = 0
    s.reqs_int[0:s.nreqs].value             = s.reqs.value
    s.reqs_int[s.nreqs:s.nreqsX2].value     = s.reqs.value
    #s.reqs_int[s.nreqs:2*s.nreqs].value     = s.reqs.value

    for i in range(s.nreqsX2):
    #for i in range(2*s.nreqs):

      if s.priority_int[i].value:
        s.grants_int[i].value = s.reqs_int[i].value
      else:
        s.grants_int[i].value = ~s.kills[i].value & s.reqs_int[i].value

      if s.priority_int[i].value:
        s.kills[i+1].value = s.grants_int[i].value
      else:
        s.kills[i+1].value = s.kills[i].value | s.grants_int[i].value

    for i in range( s.nreqs ):
      s.grants[i].value = s.grants_int[i].value | s.grants_int[s.nreqs+i].value

    s.priority_en.value = ( s.grants.value != 0 )

  def line_trace(s):
    return "{:04b} | {:04b}".format( s.reqs.value.uint, s.grants.value.uint )

#-------------------------------------------------------------------------
# Round Robin Arbiter with Enable
#-------------------------------------------------------------------------
# Round Robin Arbiter model with an enable bit. When the aribter enable bit
# is set high, the arbitration takes place else the arbitration is
# disabled.

class RoundRobinArbiterEn(Model):

  @capture_args
  def __init__(s, nreqs ):

    # Local Constants

    ARB    = 1
    NO_ARB = 0

    # Interface Ports

    s.en         = InPort  ( 1 )
    s.reqs       = InPort  ( nreqs )
    s.grants     = OutPort ( nreqs )

    # reqs_mux

    s.reqs_mux   = m = pmlib.muxes.Mux2( nreqs )
    connect({
      m.in_[NO_ARB] : 0,
      m.in_[ARB]    : s.reqs,
      m.sel         : s.en
    })

    # round robin arbiter

    s.rr_arbiter = RoundRobinArbiter( nreqs )

    connect( s.rr_arbiter.reqs,   s.reqs_mux.out )
    connect( s.rr_arbiter.grants, s.grants       )

  def line_trace(s):
    return "{:04b} | {:04b}".format( s.reqs.value.uint, s.grants.value.uint )
