#=========================================================================
# SorterRTL
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

from pex_regincr.Register import *
from MaxMin import *

class SorterRTL( Model ):

  def __init__( self ):

    self.in_ = [ InPort(16)   for x in range(4) ]
    self.out = [ OutPort(16)  for x in range(4) ]

    #---------------------------------------------------------------------
    # Stage A->B pipeline registers
    #---------------------------------------------------------------------

    self.reg_AB = [ Register(16) for x in range(4) ]
    connect( self.in_[0], self.reg_AB[0].in_ )
    connect( self.in_[1], self.reg_AB[1].in_ )
    connect( self.in_[2], self.reg_AB[2].in_ )
    connect( self.in_[3], self.reg_AB[3].in_ )

    #---------------------------------------------------------------------
    # Stage B combinational logic
    #---------------------------------------------------------------------

    self.cmp_B0 = MaxMin()
    connect( self.reg_AB[0].out, self.cmp_B0.in0 )
    connect( self.reg_AB[1].out, self.cmp_B0.in1 )

    self.cmp_B1 = MaxMin()
    connect( self.reg_AB[2].out, self.cmp_B1.in0 )
    connect( self.reg_AB[3].out, self.cmp_B1.in1 )

    #---------------------------------------------------------------------
    # Stage B->C pipeline registers
    #---------------------------------------------------------------------

    self.reg_BC = [ Register(16) for x in range(4) ]

    connect( self.cmp_B0.min, self.reg_BC[0].in_ )
    connect( self.cmp_B0.max, self.reg_BC[1].in_ )

    connect( self.cmp_B1.min, self.reg_BC[2].in_ )
    connect( self.cmp_B1.max, self.reg_BC[3].in_ )

    #---------------------------------------------------------------------
    # Stage C combinational logic
    #---------------------------------------------------------------------

    self.cmp_C0 = MaxMin()
    connect( self.reg_BC[0].out, self.cmp_C0.in0 )
    connect( self.reg_BC[2].out, self.cmp_C0.in1 )

    self.cmp_C1 = MaxMin()
    connect( self.reg_BC[1].out, self.cmp_C1.in0 )
    connect( self.reg_BC[3].out, self.cmp_C1.in1 )

    self.cmp_C2 = MaxMin()
    connect( self.cmp_C0.max, self.cmp_C2.in0 )
    connect( self.cmp_C1.min, self.cmp_C2.in1 )

    # Connect to output ports

    connect( self.cmp_C0.min, self.out[0] )
    connect( self.cmp_C2.min, self.out[1] )
    connect( self.cmp_C2.max, self.out[2] )
    connect( self.cmp_C1.max, self.out[3] )

  def line_trace( self ):
    inputs  = [ x.value for x in self.in_ ]
    outputs = [ x.value for x in self.out ]
    return "in: {0}  out: {1}".format( inputs, outputs )
