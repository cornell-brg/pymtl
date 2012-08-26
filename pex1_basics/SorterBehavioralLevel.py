#=========================================================================
# SorterBehavioralLevel
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

class SorterBehavioralLevel( Model ):

  def __init__( self ):
    self.in_ = [ InPort( 16 )  for x in range(4) ]
    self.out = [ OutPort( 16 ) for x in range(4) ]

  @posedge_clk
  def seq_logic( self ):

    values = [ x.value for x in self.in_ ]
    values.sort()
    for i, value in enumerate( values ):
      self.out[i].value = value

  def line_trace( self ):
    inputs  = [ x.value for x in self.in_ ]
    outputs = [ x.value for x in self.out ]
    return "in: {0}  out: {1}".format( inputs, outputs )

