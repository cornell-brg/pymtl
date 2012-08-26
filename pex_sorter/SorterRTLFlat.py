#=========================================================================
# SorterRTLFlat
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

from pex_regincr.Register import *
from MaxMin import *

class SorterRTLFlat( Model ):

  def __init__( self ):

    #self.in_ = [ InPort(16)   for x in range(4) ]
    #self.out = [ OutPort(16)  for x in range(4) ]
    self.in_0 = InPort(16)
    self.in_1 = InPort(16)
    self.in_2 = InPort(16)
    self.in_3 = InPort(16)
    self.out_0 = OutPort(16)
    self.out_1 = OutPort(16)
    self.out_2 = OutPort(16)
    self.out_3 = OutPort(16)

    #self.reg_AB = [ Wire(16) for x in range(4) ]
    self.reg_AB_0 = Wire(16)
    self.reg_AB_1 = Wire(16)
    self.reg_AB_2 = Wire(16)
    self.reg_AB_3 = Wire(16)

    self.B0_max = Wire(16)
    self.B0_min = Wire(16)
    self.B1_max = Wire(16)
    self.B1_min = Wire(16)

    #self.reg_BC = [ Wire(16) for x in range(4) ]
    self.reg_BC_0 = Wire(16)
    self.reg_BC_1 = Wire(16)
    self.reg_BC_2 = Wire(16)
    self.reg_BC_3 = Wire(16)

    self.C0_max = Wire(16)
    self.C0_min = Wire(16)
    self.C1_max = Wire(16)
    self.C1_min = Wire(16)
    self.C2_max = Wire(16)
    self.C2_min = Wire(16)

  @posedge_clk
  def seq_logic( self ):
    #---------------------------------------------------------------------
    # Stage A->B pipeline registers
    #---------------------------------------------------------------------
    self.reg_AB_0.next = self.in_0.value
    self.reg_AB_1.next = self.in_1.value
    self.reg_AB_2.next = self.in_2.value
    self.reg_AB_3.next = self.in_3.value

    self.out_0.next = self.reg_AB_0.value
    self.out_1.next = self.reg_AB_1.value
    self.out_2.next = self.reg_AB_2.value
    self.out_3.next = self.reg_AB_3.value

    #---------------------------------------------------------------------
    # Stage B->C pipeline registers
    #---------------------------------------------------------------------

    self.reg_BC_0.next = self.B0_min.value
    self.reg_BC_1.next = self.B0_max.value

    self.reg_BC_2.next = self.B1_min.value
    self.reg_BC_3.next = self.B1_max.value

  @combinational
  def comb_logic( self ):
    #---------------------------------------------------------------------
    # Stage B combinational logic
    #---------------------------------------------------------------------
    if self.reg_AB_0.value >= self.reg_AB_1.value:
      self.B0_max.value = self.reg_AB_0.value
      self.B0_min.value = self.reg_AB_1.value
    else:
      self.B0_max.value = self.reg_AB_1.value
      self.B0_min.value = self.reg_AB_0.value

    if self.reg_AB_2.value >= self.reg_AB_3.value:
      self.B1_max.value = self.reg_AB_2.value
      self.B1_min.value = self.reg_AB_3.value
    else:
      self.B1_max.value = self.reg_AB_3.value
      self.B1_min.value = self.reg_AB_2.value

    #---------------------------------------------------------------------
    # Stage C combinational logic
    #---------------------------------------------------------------------
    if self.reg_BC_0.value >= self.reg_BC_2.value:
      self.C0_max.value = self.reg_BC_0.value
      self.C0_min.value = self.reg_BC_2.value
    else:
      self.C0_max.value = self.reg_BC_2.value
      self.C0_min.value = self.reg_BC_0.value

    if self.reg_BC_1.value >= self.reg_BC_3.value:
      self.C1_max.value = self.reg_BC_1.value
      self.C1_min.value = self.reg_BC_3.value
    else:
      self.C1_max.value = self.reg_BC_3.value
      self.C1_min.value = self.reg_BC_1.value

    if self.C0_max.value >= self.C1_min.value:
      self.C2_max.value = self.C0_max.value
      self.C2_min.value = self.C1_min.value
    else:
      self.C2_max.value = self.C1_min.value
      self.C2_min.value = self.C0_max.value

    #---------------------------------------------------------------------
    # Connect to output ports
    #---------------------------------------------------------------------
    self.out_0.value = self.C0_min.value
    self.out_1.value = self.C2_min.value
    self.out_2.value = self.C2_max.value
    self.out_3.value = self.C1_max.value


  def line_trace( self ):
    inputs  = [ (x.name, x.value) for x in self._ports if isinstance(x, InPort) ]
    outputs = [ (x.name, x.value) for x in self._ports if isinstance(x, OutPort) ]
    inputs.sort()
    outputs.sort()
    return "inputs: {0}  out: {1}".format( inputs, outputs )
