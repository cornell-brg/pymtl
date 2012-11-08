#=========================================================================
# Crossbar
#=========================================================================

from pymtl import *
import pmlib

class Crossbar ( Model ):

  @capture_args
  def __init__( self, nports, nbits ):

    self.nports = nports

    self.in_ = [ InPort  ( nbits )  for x in range( nports ) ]
    self.out = [ OutPort ( nbits )  for x in range( nports ) ]
    self.sel = [ InPort  ( 1 )      for x in range( nports ) ]

  @combinational
  def comb_logic( self ):

    for i in range( self.nports ):
      sel = self.sel[ i ].value.uint
      self.out[i].value = self.in_[ sel ].value

  def line_trace( self ):
    s = ''
    for i in xrange( self.nports ):
      s += "{:04x} ".format( self.in_[i].value.uint )
    for i in xrange( self.nports ):
      s += "{:01x} ".format( self.sel[i].value.uint )
    s += "()"
    for i in xrange( self.nports ):
      s += " {:04x}".format( self.out[i].value.uint )
    return s

