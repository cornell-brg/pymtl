from pymtl_model import *

class Rotator(Model):
  def __init__(self, bits):
    # Ports
    self.inp = [ InPort(1)  for x in xrange(bits) ]
    self.out = [ OutPort(1) for x in xrange(bits) ]
    # Connections
    for i in xrange(bits - 1):
      self.inp[i] <> self.out[i+1]
    self.inp[-1] <> self.out[0]

# TODO: broken!
#class RotatorSlice(Model):
#  def __init__(self, bits):
#    # Ports
#    self.inp = InPort(bits)
#    self.out = OutPort(bits)
#    # Connections
#    for i in xrange(bits - 1):
#      self.inp[i] <> self.out[i+1]
#    self.inp[-1] <> self.out[0]

class SimpleSplitter(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = [ OutPort(1) for x in xrange(bits) ]
    # Connections
    for i in xrange(bits):
      self.out[i] <> self.inp[i]


class ComplexSplitter(Model):
  def __init__(self, bits, groupings):
    # Port Definitions
    self.inp = InPort(bits)
    self.out = [ OutPort(groupings) for x in xrange(0, bits, groupings) ]
    # Connections
    outport_num = 0
    for i in xrange(0, bits, groupings):
      self.out[outport_num] <> self.inp[i:i+groupings]
      outport_num += 1


class SimpleMerger(Model):
  def __init__(self, bits):
    # Port Definitions
    self.inp = [ InPort(1) for x in xrange(bits) ]
    self.out = OutPort(bits)
    # Connections
    for i in xrange(bits):
      self.out[i] <> self.inp[i]


class ComplexMerger(Model):
  def __init__(self, bits, groupings):
    # Port Definitions
    self.inp = [ InPort(groupings) for x in xrange(0, bits, groupings) ]
    self.out = OutPort(bits)
    # Connections
    inport_num = 0
    for i in xrange(0, bits, groupings):
      self.out[i:i+groupings] <> self.inp[inport_num]
      inport_num += 1


class OneWire(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # Connections
    self.inp <> self.out


class OneWireWrapped(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # Submodules
    # TODO: cannot use keyword "wire" for variable names when converting
    #       To! Check for this?
    self.wire0 = OneWire(bits)
    # Connections
    self.inp <> self.wire0.inp
    self.out <> self.wire0.out


class Register(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # TODO: how to handle clock?
    self.clk = InPort(1)
  @posedge_clk
  def tick(self):
    self.out.next = self.inp.value


class RegisterWrapper(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # TODO: how to handle clock?
    self.clk = InPort(1)
    # Submodules
    # TODO: cannot use keyword "reg" for variable names when converting
    #       To! Check for this?
    self.reg0 = Register(bits)
    # Connections
    self.inp <> self.reg0.inp
    self.out <> self.reg0.out
    self.clk <> self.reg0.clk


class RegisterChain(Model):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # TODO: how to handle clock?
    self.clk = InPort(1)
    # Submodules
    self.reg1 = Register(bits)
    self.reg2 = Register(bits)
    self.reg3 = Register(bits)
    # Connections
    self.inp <> self.reg1.inp
    self.reg1.out <> self.reg2.inp
    self.reg2.out <> self.reg3.inp
    self.reg3.out <> self.out
    self.clk <> self.reg1.clk
    self.clk <> self.reg2.clk
    self.clk <> self.reg3.clk


class RegisterSplitter(Model):
  def __init__(self, bits):
    groupings = 2
    # Ports
    self.inp = InPort(bits)
    self.out = [ OutPort(groupings) for x in xrange(0, bits, groupings) ]
    # TODO: how to handle clock?
    self.clk = InPort(1)
    # Submodules
    self.reg0  = Register(bits)
    self.split = ComplexSplitter(bits, groupings)
    # Connections
    self.clk      <> self.reg0.clk
    self.inp      <> self.reg0.inp
    self.reg0.out <> self.split.inp
    for i, x in enumerate(self.out):
      self.split.out[i] <> x


class FullAdder(Model):
  def __init__(self):
    # Ports
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)

  @combinational
  def logic(self):
    in0 = self.in0.value
    in1 = self.in1.value
    cin = self.cin.value
    self.sum.value  = (self.in0.value ^ self.in1.value) ^ self.cin.value
    self.cout.value = (in0 & in1) | (in0 & cin) | (in1 & cin)


class RippleCarryAdder(Model):
  def __init__(self, bits):
    # Ports
    self.in0 = InPort (bits)
    self.in1 = InPort (bits)
    self.sum = OutPort(bits)
    # Submodules
    self.adders = [ FullAdder() for i in xrange(bits) ]
    # Connections
    for i in xrange(bits):
      self.adders[i].in0 <> self.in0[i]
      self.adders[i].in1 <> self.in1[i]
      self.adders[i].sum <> self.sum[i]
    for i in xrange(bits-1):
      self.adders[i+1].cin <> self.adders[i].cout
    self.adders[0].cin <> 0


class Incrementer(Model):
  def __init__(self):
    # Ports
    self.inp  = InPort(32)
    self.out  = OutPort(32)

  @combinational
  def logic(self):
    self.out.value = self.inp.value + 1

class Counter(Model):
  def __init__(self, max=None):
    # Ports
    self.clk   = InPort(1)
    self.clear = InPort(1)
    self.count = OutPort(32)
    # Params
    self.max   = max

  @posedge_clk
  def logic(self):
    if self.clear.value:
      self.count.next = 0
    elif self.count.value == self.max:
      self.count.next = 0
    else:
      self.count.next = self.count.value + 1

class CountIncr(Model):
  def __init__(self, max=None):
    # Ports
    self.clk   = InPort(1)
    self.clear = InPort(1)
    self.count = OutPort(32)
    # Submodules
    self.incr  = Incrementer()
    self.cntr  = Counter(max)
    # Connections
    self.clk   <> self.cntr.clk
    self.clear <> self.cntr.clear
    self.cntr.count <> self.incr.inp
    self.incr.out <> self.count

class RegIncr(Model):
  def __init__(self):
    # Ports
    self.clk = InPort(1)
    self.inp = InPort(32)
    self.out = OutPort(32)
    # Submodules
    self.reg0 = Register(32)
    self.incr = Incrementer()
    # Connections
    self.clk <> self.reg0.clk
    self.inp <> self.reg0.inp
    self.reg0.out <> self.incr.inp
    self.incr.out <> self.out

class IncrReg(Model):
  def __init__(self):
    # Ports
    self.clk = InPort(1)
    self.inp = InPort(32)
    self.out = OutPort(32)
    # Submodules
    self.incr = Incrementer()
    self.reg0 = Register(32)
    # Connections
    self.clk <> self.reg0.clk
    self.inp <> self.incr.inp
    self.incr.out <> self.reg0.inp
    self.reg0.out <> self.out

class GCD(Model):
  def __init__(self):
    # Ports
    self.clk     = InPort(1)
    self.in_A    = InPort(32)
    self.in_B    = InPort(32)
    self.in_val  = InPort(1)
    self.out     = OutPort(32)
    self.out_val = OutPort(1)
    # Wires
    self.state      = UWire(2)
    self.A_reg      = UWire(32)
    self.B_reg      = UWire(32)
    self.is_A_lt_B  = UWire(1)
    self.is_B_neq_0 = UWire(1)
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

#class RegisteredAdder1(Model):
#  def __init__(self, bits):
#    # Ports
#    self.in0 = InPort(bits)
#    self.in1 = InPort(bits)
#    self.out = OutPort(bits)
#  @posedge_clk
#  def tick(self):
#    in0 = self.in0
#    in1 = self.in1
#    out = self.out
#    out <<= in0 + in1
#
#class RegisteredAdder2(Model):
#  def __init__(self, bits):
#    # Ports
#    self.in0 = InPort(bits)
#    self.in1 = InPort(bits)
#    self.out = OutPort(bits)
#    # Submodules
#    self.sum = Wire(bits)
#  @combinational
#  def tick(self):
#    in0 = self.in0
#    in1 = self.in1
#    sum = self.sum
#    sum <<= in0 + in1
#  @posedge_clk
#  def tick():
#    in0 = self.in0
#    in1 = self.in1
#    out = self.out
#    out <<= sum

