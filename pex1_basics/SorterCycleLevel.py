import sys
sys.path.append('..')
from pymtl import *

class SorterCycleLevel( Model ):

  def __init__( self ):

    self.in_ = [ InPort( 16 )  for x in range(4) ]
    self.out = [ OutPort( 16 ) for x in range(4) ]
    self.delay0 = 4*[0]
    self.delay1 = 4*[0]

  @posedge_clk
  def seq_logic( self ):

    self.delay1 = self.delay0

    self.delay0 = [ x.value for x in self.in_ ]
    self.delay0.sort()

    for i, value in enumerate( self.delay1 ):
      self.out[i].value = value

  def line_trace( self ):
    inputs  = [ x.value for x in self.in_ ]
    outputs = [ x.value for x in self.out ]
    return "in: {0}  out: {1}".format( inputs, outputs )

