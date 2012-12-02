#=========================================================================
# Crossbar
#=========================================================================
# This class implements a parameterized "nxn" square crossbar switch.
# conceptually a cross bar with "n" inputs & "n" outputs allows each input
# to traverse the switch and cross over to any of the output without any
# intermediate stages given the select control signals. We can model the
# cross bar by having "n" output muxes based on the number of output ports
# with the select control lines.
#
# Interface
# ---------
#
# nbits  : bitwidth of each port
# nports : parameter for number of ports in the square "nxn" crossbar
# in_    : list of input ports
# sel    : list of select control lines for each output mux
# out    : list of output ports

from   pymtl import *
import pmlib
import math

class Crossbar3 ( Model ):

  def __init__( self, nports=3, nbits=16 ):

    # Local Constant

    self.nports = nports

    sel_nbits   = int( math.ceil( math.log( nports, 2 ) ) )

    # Interface Ports

    self.in0    = InPort  ( nbits )
    self.in1    = InPort  ( nbits )
    self.in2    = InPort  ( nbits )
    self.out0   = OutPort ( nbits )
    self.out1   = OutPort ( nbits )
    self.out2   = OutPort ( nbits )
    self.sel0   = InPort  ( sel_nbits )
    self.sel1   = InPort  ( sel_nbits )
    self.sel2   = InPort  ( sel_nbits )

  @combinational
  def comb_logic( self ):

    if self.sel0.value == 0:
      self.out0.value = self.in0.value
    if self.sel0.value == 1:
      self.out0.value = self.in1.value
    if self.sel0.value == 2:
      self.out0.value = self.in2.value

    if self.sel1.value == 0:
      self.out1.value = self.in0.value
    if self.sel1.value == 1:
      self.out1.value = self.in1.value
    if self.sel1.value == 2:
      self.out1.value = self.in2.value

    if self.sel2.value == 0:
      self.out2.value = self.in0.value
    if self.sel2.value == 1:
      self.out2.value = self.in1.value
    if self.sel2.value == 2:
      self.out2.value = self.in2.value

  def line_trace( self ):
    s = ''
    #for i in xrange( self.nports ):
    #  s += "{:04x} ".format( self.in_[i].value.uint )
    #s += "( "
    #for i in xrange( self.nports ):
    #  s += "{:01x} ".format( self.sel[i].value.uint )
    #s += ")"
    #for i in xrange( self.nports ):
    #  s += " {:04x}".format( self.out[i].value.uint )
    return s

