#=========================================================================
# Muxes
#=========================================================================
# Asserting that a select value is out of range is not currently
# translatable.

from pymtl import *
import math

#-------------------------------------------------------------------------
# Equivalent to Verilog's $clog2, takes the ceiling of the log of number
#-------------------------------------------------------------------------

def clog2( n ):
  return int( math.ceil( math.log( n, 2 ) ) )

#-------------------------------------------------------------------------
# Mux
#-------------------------------------------------------------------------

class Mux( Model ):

  def __init__( self, nbits = 1, num_ports = 2 ):

    self.in_ = [ InPort( nbits ) for x in xrange( num_ports ) ]
    self.sel = InPort  ( clog2( num_ports ) )
    self.out = OutPort ( nbits )
    self.num_ports = num_ports

  @combinational
  def comb_logic( self ):
    assert self.sel.value < self.num_ports

    for i in range( self.num_ports ):
      if self.sel.value == i:
        self.out.value = self.in_[i].value

  def line_trace( self ):
    string = ""
    for i in range( self.num_ports ):
      string = string + "{:04x} " .format( self.in_[i].value.uint )
    string = string + "{:01x} () {:04x}" \
      .format( self.sel.value.uint, self.out.value.uint )
    return string
