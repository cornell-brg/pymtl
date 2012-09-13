#=========================================================================
# Crossbar
#=========================================================================
# Implementation of crossbar to route inputs to outputs

from pymtl import *
from mux import *

#-------------------------------------------------------------------------
# Crossbar
#-------------------------------------------------------------------------

class Crossbar( Model ):

  def __init__( self, nbits = 1, num_ports = 2 ):

    self.in_ = [ InPort( nbits ) for x in xrange( num_ports ) ]
    self.sel = [ InPort( 1 ) for x in xrange( num_ports ) ]
    self.out = [ OutPort( nbits ) for x in xrange( num_ports ) ]

    self.mux = [ Mux( nbits, num_ports ) for x in xrange( num_ports ) ]

    for i in range( num_ports ):
      connect( self.sel[i], self.mux[i].sel )
      connect( self.out[i], self.mux[i].out )
      for j in range( num_ports ):
        connect( self.in_[i], self.mux[j].in_[i] )
      
    

# def line_trace( self ):
#   return "{:04x} {:04x} {:01x} () {:04x}" \
#     .format( self.in_[0].value.uint, self.in_[1].value.uint,
#              self.sel.value.uint, self.out.value.uint )
