#=========================================================================
# SorterRTLStruct
#=========================================================================

from pymtl  import *
from pmlib  import regs
from MaxMin import MaxMin

class SorterRTLStruct( Model ):

  def __init__( self ):

    self.in_ = [ InPort(16)   for x in range(4) ]
    self.out = [ OutPort(16)  for x in range(4) ]

    #---------------------------------------------------------------------
    # Stage A->B pipeline registers
    #---------------------------------------------------------------------

    self.reg_AB = [ regs.Reg(16) for x in range(4) ]
    connect( self.reg_AB[0].in_, self.in_[0] )
    connect( self.reg_AB[1].in_, self.in_[1] )
    connect( self.reg_AB[2].in_, self.in_[2] )
    connect( self.reg_AB[3].in_, self.in_[3] )

    #---------------------------------------------------------------------
    # Stage B combinational logic
    #---------------------------------------------------------------------

    self.cmp_B0 = m = MaxMin()
    connect({
      m.in0 : self.reg_AB[0].out,
      m.in1 : self.reg_AB[1].out,
    })

    self.cmp_B1 = m = MaxMin()
    connect({
      m.in0 : self.reg_AB[2].out,
      m.in1 : self.reg_AB[3].out,
    })

    #---------------------------------------------------------------------
    # Stage B->C pipeline registers
    #---------------------------------------------------------------------

    self.reg_BC = [ regs.Reg(16) for x in range(4) ]
    connect( self.reg_BC[0].in_, self.cmp_B0.min )
    connect( self.reg_BC[1].in_, self.cmp_B0.max )
    connect( self.reg_BC[2].in_, self.cmp_B1.min )
    connect( self.reg_BC[3].in_, self.cmp_B1.max )

    #---------------------------------------------------------------------
    # Stage C combinational logic
    #---------------------------------------------------------------------

    self.cmp_C0 = m = MaxMin()
    connect({
      m.in0 : self.reg_BC[0].out,
      m.in1 : self.reg_BC[2].out,
    })

    self.cmp_C1 = m = MaxMin()
    connect({
      m.in0 : self.reg_BC[1].out,
      m.in1 : self.reg_BC[3].out,
    })

    self.cmp_C2 = m = MaxMin()
    connect({
      m.in0 : self.cmp_C0.max,
      m.in1 : self.cmp_C1.min,
    })

    # Connect to output ports

    connect( self.cmp_C0.min, self.out[0] )
    connect( self.cmp_C2.min, self.out[1] )
    connect( self.cmp_C2.max, self.out[2] )
    connect( self.cmp_C1.max, self.out[3] )

