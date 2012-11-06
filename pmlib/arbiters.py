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

  def __init__(self, nreqs ):

    self.nreqs        = nreqs

    # Interface Ports

    self.reqs         = InPort  (nreqs)
    self.grants       = OutPort (nreqs)

    # priority enable

    self.priority_en  = Wire( 1     )

    # priority register

    self.priority_reg = m = pmlib.regs.RegEnRst( nreqs,
                              reset_value = 1 )
    connect({
      m.en           : self.priority_en,
      m.in_[1:nreqs] : self.grants[0:nreqs-1],
      m.in_[0]       : self.grants[nreqs-1]
    })

  @combinational
  def comb(self):

    nreqs = self.nreqs

    kills        = Bits( 2*nreqs + 1 )
    priority_int = Bits( 2*nreqs )
    reqs_int     = Bits( 2*nreqs )
    grants_int   = Bits( 2*nreqs )

    kills[0] = 1;
    priority_int[0:nreqs]       = self.priority_reg.out.value
    priority_int[nreqs:2*nreqs] = 0
    reqs_int[0:nreqs]           = self.reqs.value
    reqs_int[nreqs:2*nreqs]     = self.reqs.value

    for i in range(2*nreqs):

      if priority_int[i]:
        grants_int[i] = reqs_int[i]
      else:
        grants_int[i] = ~kills[i] & reqs_int[i]

      if priority_int[i]:
        kills[i+1] = grants_int[i]
      else:
        kills[i+1] = kills[i] | grants_int[i]

    for i in range( nreqs ):
      self.grants[i].value = grants_int[i] | grants_int[nreqs+i]

    self.priority_en.value = ( self.grants.value != 0 )

  def line_trace(self):
    return "{:04b} | {:04b}".format( self.reqs.value.uint, self.grants.value.uint )

#-------------------------------------------------------------------------
# Round Robin Arbiter with Enable
#-------------------------------------------------------------------------
# Round Robin Arbiter model with an enable bit. When the aribter enable bit
# is set high, the arbitration takes place else the arbitration is
# disabled.

class RoundRobinArbiterEn(Model):

  def __init__(self, nreqs ):

    # Local Constants

    ARB    = 1
    NO_ARB = 0

    # Interface Ports

    self.en         = InPort  ( 1 )
    self.reqs       = InPort  ( nreqs )
    self.grants     = OutPort ( nreqs )

    # reqs_mux

    self.reqs_mux   = m = pmlib.muxes.Mux2( nreqs )
    connect({
      m.in_[NO_ARB] : 0,
      m.in_[ARB]    : self.reqs,
      m.sel         : self.en
    })

    # round robin arbiter

    self.rr_arbiter = RoundRobinArbiter( nreqs )

    connect( self.rr_arbiter.reqs,   self.reqs_mux.out )
    connect( self.rr_arbiter.grants, self.grants       )

  def line_trace(self):
    return "{:04b} | {:04b}".format( self.reqs.value.uint, self.grants.value.uint )
