########################################################################
# GCD Module Interface
#
#    INPUTS
#    Name     Width
#
#    clk          1
#    reset        1
#    in_A        16
#    in_B        16
#    in_val       1
#    in_rdy       1
#
#    OUTPUTS
#    Name     Width
#
#    out         16
#    out_val      1
#    out_rdy      1
#
########################################################################

from pymtl.pymtl_model import *

class GCD(Model):

  ########################################################################
  # INTERFACE
  ########################################################################
  def __init__(self):

    # Declare Interface Here

    # Constants
    self.IDLE   = 0
    self.ACTIVE = 1
    self.DONE   = 2

  ########################################################################
  # LOGIC
  ########################################################################

  # Insert Logic Here

  ########################################################################
  # UTILITY FUNCTIONS
  ########################################################################

  def line_trace(self):
    sdict = { 0:'Idle', 1:'Actv', 2:'Done' }
    self.IDLE   = 0
    self.ACTIVE = 1
    self.DONE   = 2
    line  = "{0} {1} {2} ||".format( self.in_A.value, self.in_B.value,
                                     self.in_val.value )
    line += "{0:2} {1:2} {2}".format( self.A_reg.value, self.B_reg.value,
                                    sdict[self.state.value] )
    line += " A<B:{0} B!=0:{1}".format( self.is_A_lt_B.value, self.is_B_neq_0.value)
    line += "|| {0} {1}".format( self.out.value, self.out_val.value )
    print line

