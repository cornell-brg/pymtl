#=========================================================================
# SorterRTL
#=========================================================================
# A register-transfer-level model explicitly represents state elements
# with posedge_clk concurrent blocks and uses combinational concurrent
# blocks to model how data transfers between state elements.

from new_pymtl import *

class SorterRTL( Model ):

  def __init__( s ):

    # Ports

    s.in_ = [ InPort  ( 16 ) for x in range(4) ]
    s.out = [ OutPort ( 16 ) for x in range(4) ]

  def elaborate_logic( s ):

    # Wires

    s.reg_AB = [ Wire ( 16 ) for x in range(4) ]

    s.B0_max = Wire ( 16 )
    s.B0_min = Wire ( 16 )
    s.B1_max = Wire ( 16 )
    s.B1_min = Wire ( 16 )

    s.reg_BC = [ Wire ( 16 ) for x in range(4) ]

    s.C0_max = Wire ( 16 )
    s.C0_min = Wire ( 16 )
    s.C1_max = Wire ( 16 )
    s.C1_min = Wire ( 16 )
    s.C2_max = Wire ( 16 )
    s.C2_min = Wire ( 16 )

    #---------------------------------------------------------------------
    # Stage A->B pipeline registers
    #---------------------------------------------------------------------

    @s.posedge_clk
    def reg_ab():

      s.reg_AB[0].next = s.in_[0]
      s.reg_AB[1].next = s.in_[1]
      s.reg_AB[2].next = s.in_[2]
      s.reg_AB[3].next = s.in_[3]

    #---------------------------------------------------------------------
    # Stage B combinational logic
    #---------------------------------------------------------------------

    @s.combinational
    def stage_b():

      if s.reg_AB[0] >= s.reg_AB[1]:
        s.B0_max.value = s.reg_AB[0]
        s.B0_min.value = s.reg_AB[1]
      else:
        s.B0_max.value = s.reg_AB[1]
        s.B0_min.value = s.reg_AB[0]

      if s.reg_AB[2] >= s.reg_AB[3]:
        s.B1_max.value = s.reg_AB[2]
        s.B1_min.value = s.reg_AB[3]
      else:
        s.B1_max.value = s.reg_AB[3]
        s.B1_min.value = s.reg_AB[2]

    #---------------------------------------------------------------------
    # Stage B->C pipeline registers
    #---------------------------------------------------------------------

    @s.posedge_clk
    def reg_bc():

      s.reg_BC[0].next = s.B0_min
      s.reg_BC[1].next = s.B0_max

      s.reg_BC[2].next = s.B1_min
      s.reg_BC[3].next = s.B1_max

    #---------------------------------------------------------------------
    # Stage C combinational logic
    #---------------------------------------------------------------------

    @s.combinational
    def stage_c():

      if s.reg_BC[0] >= s.reg_BC[2]:
        s.C0_max.value = s.reg_BC[0]
        s.C0_min.value = s.reg_BC[2]
      else:
        s.C0_max.value = s.reg_BC[2]
        s.C0_min.value = s.reg_BC[0]

      if s.reg_BC[1] >= s.reg_BC[3]:
        s.C1_max.value = s.reg_BC[1]
        s.C1_min.value = s.reg_BC[3]
      else:
        s.C1_max.value = s.reg_BC[3]
        s.C1_min.value = s.reg_BC[1]

      if s.C0_max >= s.C1_min:
        s.C2_max.value = s.C0_max
        s.C2_min.value = s.C1_min
      else:
        s.C2_max.value = s.C1_min
        s.C2_min.value = s.C0_max

      # Connect to output ports

      s.out[0].value = s.C0_min
      s.out[1].value = s.C2_min
      s.out[2].value = s.C2_max
      s.out[3].value = s.C1_max

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} {} {} () {} {} {} {}" \
      .format( s.in_[0], s.in_[1],
               s.in_[2], s.in_[3],
               s.out[0], s.out[1],
               s.out[2], s.out[3] )

