import sys

from rtler_vbase import *

#  Target:
#
#  class FullAdder (foo):
#
#   def __init__(self):
#     self.in0  = InputPort(1)
#     self.in1  = InputPort(1)
#     self.cin  = InputPort(1)
#     self.sum  = OutputPort(1)
#     self.cout = OutputPort(1)
#
#  class RippleCarryAdder (foo):
#
#   def __init__(self):
#     self.in0  = InputPort(32)
#     self.in1  = InputPort(32)
#     self.sum  = OutputPort(32)
#
#   def elaborate(self):
#
#     self.adders = [ FullAdder() for i in xrange(32) ]
#
#     for i in xrange(32):
#       self.adders[i].in0 <> self.in0[i]
#       self.adders[i].in1 <> self.in1[i]
#       self.adders[i].out <> self.out[i]
#
#     self.adders[0].cin.wr(0)
#     for i in xrange(31):
#       self.adders[i+1].cin <> self.adders[i].cout


class InPort(VerilogPort):
  def __init__(self, width=None):
    super(InPort, self).__init__('input', width)

class OutPort(VerilogPort):
  def __init__(self, width=None):
    super(OutPort, self).__init__('output', width)

class FullAdder(ToVerilog):
  def __init__(self):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)

class RippleCarryAdder(ToVerilog):
  def __init__(self, bits):
    self.in0 = InPort (bits)
    self.in1 = InPort (bits)
    self.sum = OutPort(bits)

    self.adders = [ FullAdder() for i in xrange(bits) ]

    for i in xrange(bits):
      self.adders[i].in0 <> self.in0[i]
      self.adders[i].in1 <> self.in1[i]
      self.adders[i].sum <> self.sum[i]

    # TODO: does not create intermediate wires! Fix!
    for i in xrange(bits-1):
      self.adders[i+1].cin <> self.adders[i].cout
    self.adders[0].cin <> 0


#TODO: run pychecker?
#one_bit = FullAdder()
#one_bit.generate_new(sys.stdout)
four_bit = RippleCarryAdder(4)
four_bit.elaborate()
four_bit.generate(sys.stdout)
