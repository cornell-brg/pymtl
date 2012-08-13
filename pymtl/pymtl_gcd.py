from pymtl_model import *

class GCD(Model):

  def __init__(self):
    # Ports
    self.clk     = InPort(1)

    self.in_A    = InPort(32)
    self.in_B    = InPort(32)
    self.in_val  = InPort(1)
    self.in_rdy  = OutPort(1)

    self.out     = OutPort(32)
    self.out_val = OutPort(1)
    self.out_rdy = InPort(1)

    # Wires
    self.state      = TempVal(2)
    self.A_reg      = TempVal(32)
    self.B_reg      = TempVal(32)
    self.is_A_lt_B  = TempVal(1)
    self.is_B_neq_0 = TempVal(1)

    # Constants
    self.IDLE   = 0
    self.ACTIVE = 1
    self.DONE   = 2

  @posedge_clk
  def tick(self):
    # State transition
    if   self.state.value == self.IDLE:
      if self.in_val.value:
        self.state.next = self.ACTIVE
    elif self.state.value == self.ACTIVE:
      if not self.is_A_lt_B.value and not self.is_B_neq_0.value:
        self.state.next = self.DONE
    elif self.state.value == self.DONE:
      if self.out_rdy.value:
        self.state.next = self.IDLE

    # Set A_reg
    if   self.state.value == self.IDLE:
      self.A_reg.next = self.in_A.value
    elif self.state.value == self.ACTIVE:
      if self.is_A_lt_B.value:
        self.A_reg.next = self.B_reg.value
      elif self.is_B_neq_0.value:
        self.A_reg.next = self.A_reg.value - self.B_reg.value

    # Set B_reg
    if   self.state.value == self.IDLE:
      self.B_reg.next = self.in_B.value
    elif self.state.value == self.ACTIVE and self.is_A_lt_B.value:
        self.B_reg.next = self.A_reg.value

  @combinational
  def logic(self):
    self.is_A_lt_B.value  = (self.A_reg.value < self.B_reg.value)
    self.is_B_neq_0.value = (self.B_reg.value != 0)
    self.out_val.value    = (self.state.value == self.DONE)
    self.out.value        = self.A_reg.value
    if self.state.value == self.IDLE:
      self.in_rdy.value = 1
    else:
      self.in_rdy.value = 0

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

