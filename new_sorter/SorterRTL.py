#=========================================================================
# SorterRTL
#=========================================================================
# A register-transfer-level model explicitly represents state elements
# with posedge_clk concurrent blocks and uses combinational concurrent
# blocks to model how data transfers between state elements.

from pymtl import *

class SorterRTL( Model ):

  def __init__( self ):

    # Ports

    self.in_ = [ InPort  ( 16 ) for x in range(4) ]
    self.out = [ OutPort ( 16 ) for x in range(4) ]

    # Wires

    self.reg_AB = [ Wire ( 16 ) for x in range(4) ]

    self.B0_max = Wire ( 16 )
    self.B0_min = Wire ( 16 )
    self.B1_max = Wire ( 16 )
    self.B1_min = Wire ( 16 )

    self.reg_BC = [ Wire ( 16 ) for x in range(4) ]

    self.C0_max = Wire ( 16 )
    self.C0_min = Wire ( 16 )
    self.C1_max = Wire ( 16 )
    self.C1_min = Wire ( 16 )
    self.C2_max = Wire ( 16 )
    self.C2_min = Wire ( 16 )

  #---------------------------------------------------------------------
  # Stage A->B pipeline registers
  #---------------------------------------------------------------------

  @posedge_clk
  def reg_ab( self ):

    self.reg_AB[0].next = self.in_[0].value
    self.reg_AB[1].next = self.in_[1].value
    self.reg_AB[2].next = self.in_[2].value
    self.reg_AB[3].next = self.in_[3].value

  #---------------------------------------------------------------------
  # Stage B combinational logic
  #---------------------------------------------------------------------

  @combinational
  def stage_b( self ):

    if self.reg_AB[0].value >= self.reg_AB[1].value:
      self.B0_max.value = self.reg_AB[0].value
      self.B0_min.value = self.reg_AB[1].value
    else:
      self.B0_max.value = self.reg_AB[1].value
      self.B0_min.value = self.reg_AB[0].value

    if self.reg_AB[2].value >= self.reg_AB[3].value:
      self.B1_max.value = self.reg_AB[2].value
      self.B1_min.value = self.reg_AB[3].value
    else:
      self.B1_max.value = self.reg_AB[3].value
      self.B1_min.value = self.reg_AB[2].value

  #---------------------------------------------------------------------
  # Stage B->C pipeline registers
  #---------------------------------------------------------------------

  @posedge_clk
  def reg_bc( self ):

    self.reg_BC[0].next = self.B0_min.value
    self.reg_BC[1].next = self.B0_max.value

    self.reg_BC[2].next = self.B1_min.value
    self.reg_BC[3].next = self.B1_max.value

  #---------------------------------------------------------------------
  # Stage C combinational logic
  #---------------------------------------------------------------------

  @combinational
  def stage_c( self ):

    if self.reg_BC[0].value >= self.reg_BC[2].value:
      self.C0_max.value = self.reg_BC[0].value
      self.C0_min.value = self.reg_BC[2].value
    else:
      self.C0_max.value = self.reg_BC[2].value
      self.C0_min.value = self.reg_BC[0].value

    if self.reg_BC[1].value >= self.reg_BC[3].value:
      self.C1_max.value = self.reg_BC[1].value
      self.C1_min.value = self.reg_BC[3].value
    else:
      self.C1_max.value = self.reg_BC[3].value
      self.C1_min.value = self.reg_BC[1].value

    if self.C0_max.value >= self.C1_min.value:
      self.C2_max.value = self.C0_max.value
      self.C2_min.value = self.C1_min.value
    else:
      self.C2_max.value = self.C1_min.value
      self.C2_min.value = self.C0_max.value

    # Connect to output ports

    self.out[0].value = self.C0_min.value
    self.out[1].value = self.C2_min.value
    self.out[2].value = self.C2_max.value
    self.out[3].value = self.C1_max.value

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} () {:04x} {:04x} {:04x} {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint,
               self.in_[2].value.uint, self.in_[3].value.uint,
               self.out[0].value.uint, self.out[1].value.uint,
               self.out[2].value.uint, self.out[3].value.uint )

