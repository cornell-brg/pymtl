import sys
sys.path.append('..')
from pymtl import *

from Register import *
from MaxMin import *

class SorterRTL( Model ):

  def __init__( self ):

    self.in_ = [ InPort( 16 )  for x in range(4) ]
    self.out = [ OutPort( 16 ) for x in range(4) ]
    self.rs1 = [ Register(16) for x in range(4) ]
    self.rs2 = [ Register(16) for x in range(4) ]
    self.cmp = [ MaxMin() for x in range(5) ]

    # Inputs to Stage1 Registers
    connect( self.in_[0], self.rs1[0].in_ )
    connect( self.in_[1], self.rs1[1].in_ )
    connect( self.in_[2], self.rs1[2].in_ )
    connect( self.in_[3], self.rs1[3].in_ )
    # Stage1 Registers to Stage1 MaxMin Modules
    connect( self.rs1[0].out, self.cmp[0].in0 )
    connect( self.rs1[1].out, self.cmp[0].in1 )
    connect( self.rs1[2].out, self.cmp[1].in0 )
    connect( self.rs1[3].out, self.cmp[1].in1 )
    # Stage1 MaxMin Modules to Stage2 Registers
    connect( self.cmp[0].min, self.rs2[0].in_ )
    connect( self.cmp[0].max, self.rs2[1].in_ )
    connect( self.cmp[1].min, self.rs2[2].in_ )
    connect( self.cmp[1].max, self.rs2[3].in_ )
    # Stage2 Registers to Stage2 MaxMin Modules
    connect( self.rs2[0].out, self.cmp[2].in0 )
    connect( self.rs2[2].out, self.cmp[2].in1 )
    connect( self.rs2[1].out, self.cmp[3].in0 )
    connect( self.rs2[3].out, self.cmp[3].in1 )
    # Stage2 MaxMin Modules to Last MaxMin Module
    connect( self.cmp[2].max, self.cmp[4].in0 )
    connect( self.cmp[3].min, self.cmp[4].in1 )
    # Stage2 MaxMin Modules to Outputs
    connect( self.cmp[2].min, self.out[0] )
    connect( self.cmp[4].min, self.out[1] )
    connect( self.cmp[4].max, self.out[2] )
    connect( self.cmp[3].max, self.out[3] )


  def line_trace( self ):
    inputs  = [ x.value for x in self.in_ ]
    outputs = [ x.value for x in self.out ]
    return "in: {0}  out: {1}".format( inputs, outputs )
