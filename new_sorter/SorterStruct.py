#=========================================================================
# SorterRTLStruct
#=========================================================================

from pymtl  import *
import new_pmlib

from MinMax import MinMax

class SorterStruct( Model ):

  def __init__( s ):

    s.in_ = [ InPort  ( 16 ) for x in range(4) ]
    s.out = [ OutPort ( 16 ) for x in range(4) ]

  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Stage A->B pipeline registers
    #---------------------------------------------------------------------

    s.reg_AB = [ new_pmlib.regs.Reg(16) for x in range(4) ]
    s.connect( s.reg_AB[0].in_, s.in_[0] )
    s.connect( s.reg_AB[1].in_, s.in_[1] )
    s.connect( s.reg_AB[2].in_, s.in_[2] )
    s.connect( s.reg_AB[3].in_, s.in_[3] )

    #---------------------------------------------------------------------
    # Stage B combinational logic
    #---------------------------------------------------------------------

    s.cmp_B0 = m = MinMax()
    s.connect_dict({
      m.in0 : s.reg_AB[0].out,
      m.in1 : s.reg_AB[1].out,
    })

    s.cmp_B1 = m = MinMax()
    s.connect_dict({
      m.in0 : s.reg_AB[2].out,
      m.in1 : s.reg_AB[3].out,
    })

    #---------------------------------------------------------------------
    # Stage B->C pipeline registers
    #---------------------------------------------------------------------

    s.reg_BC = [ new_pmlib.regs.Reg(16) for x in range(4) ]
    s.connect( s.reg_BC[0].in_, s.cmp_B0.min )
    s.connect( s.reg_BC[1].in_, s.cmp_B0.max )
    s.connect( s.reg_BC[2].in_, s.cmp_B1.min )
    s.connect( s.reg_BC[3].in_, s.cmp_B1.max )

    #---------------------------------------------------------------------
    # Stage C combinational logic
    #---------------------------------------------------------------------

    s.cmp_C0 = m = MinMax()
    s.connect_dict({
      m.in0 : s.reg_BC[0].out,
      m.in1 : s.reg_BC[2].out,
    })

    s.cmp_C1 = m = MinMax()
    s.connect_dict({
      m.in0 : s.reg_BC[1].out,
      m.in1 : s.reg_BC[3].out,
    })

    s.cmp_C2 = m = MinMax()
    s.connect_dict({
      m.in0 : s.cmp_C0.max,
      m.in1 : s.cmp_C1.min,
    })

    # Connect to output ports

    s.connect( s.cmp_C0.min, s.out[0] )
    s.connect( s.cmp_C2.min, s.out[1] )
    s.connect( s.cmp_C2.max, s.out[2] )
    s.connect( s.cmp_C1.max, s.out[3] )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} {} {} () {} {} {} {}" \
      .format( s.in_[0], s.in_[1],
               s.in_[2], s.in_[3],
               s.out[0], s.out[1],
               s.out[2], s.out[3] )

