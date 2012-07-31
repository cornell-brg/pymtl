from metal_model import *
from metal_simulate import posedge_clk

class Rotator(Module):
  def __init__(self, bits):
    # Ports
    self.inp = [ InPort(1)  for x in xrange(bits) ]
    self.out = [ OutPort(1) for x in xrange(bits) ]
    # Connections
    for i in xrange(bits - 1):
      self.inp[i] <> self.out[i+1]
    self.inp[-1] <> self.out[0]


class SimpleSplitter(Module):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = [ OutPort(1) for x in xrange(bits) ]
    # Connections
    for i in xrange(bits):
      self.out[i] <> self.inp[i]


class ComplexSplitter(Module):
  def __init__(self, bits, groupings):
    # Port Definitions
    self.inp = InPort(bits)
    self.out = [ OutPort(groupings) for x in xrange(0, bits, groupings) ]
    # Connections
    outport_num = 0
    for i in xrange(0, bits, groupings):
      self.out[outport_num] <> self.inp[i:i+groupings]
      outport_num += 1


class SimpleMerger(Module):
  def __init__(self, bits):
    # Port Definitions
    self.inp = [ InPort(1) for x in xrange(bits) ]
    self.out = OutPort(bits)
    # Connections
    for i in xrange(bits):
      self.out[i] <> self.inp[i]


class ComplexMerger(Module):
  def __init__(self, bits, groupings):
    # Port Definitions
    self.inp = [ InPort(groupings) for x in xrange(0, bits, groupings) ]
    self.out = OutPort(bits)
    # Connections
    inport_num = 0
    for i in xrange(0, bits, groupings):
      self.out[i:i+groupings] <> self.inp[inport_num]
      inport_num += 1


class Wire(Module):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # Connections
    self.inp <> self.out


class WireWrapped(Module):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # Submodules
    # TODO: cannot use keyword "wire" for variable names when converting
    #       To! Check for this?
    self.wire0 = Wire(16)
    # Connections
    self.inp <> self.wire0.inp
    self.out <> self.wire0.out


class Register(Module):
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # TODO: how to handle clock?
    self.clk = InPort(1)
    self.regs = [self.out]
  @posedge_clk
  def tick(self):
    self.out.value = self.inp.value


class RegisterWrapper(Module):
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


class RegisterChain(Module):
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


class RegisterSplitter(Module):
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


#class RegisteredAdder1(Module):
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
#class RegisteredAdder2(Module):
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

