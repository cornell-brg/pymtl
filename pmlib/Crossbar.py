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

class Crossbar ( Model ):

  def __init__( self, nports, nbits ):

    # Local Constant

    self.nports = nports

    sel_nbits   = int( math.ceil( math.log( nports, 2 ) ) )

    # Interface Ports

    self.in_    = [ InPort  ( nbits )     for x in range( nports ) ]
    self.out    = [ OutPort ( nbits )     for x in range( nports ) ]
    self.sel    = [ InPort  ( sel_nbits ) for x in range( nports ) ]

  @combinational
  def comb_logic( self ):

    for i in range( self.nports ):
      sel = self.sel[ i ].value.uint
      self.out[i].value = self.in_[ sel ].value

  def line_trace( self ):
    s = ''
    for i in xrange( self.nports ):
      s += "{:04x} ".format( self.in_[i].value.uint )
    s += "( "
    for i in xrange( self.nports ):
      s += "{:01x} ".format( self.sel[i].value.uint )
    s += ")"
    for i in xrange( self.nports ):
      s += " {:04x}".format( self.out[i].value.uint )
    return s

