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

def always_comb(fn):
  def wrapped(self):
    return fn(self)
  return wrapped

class FullAdder(Synthesizable):
  def __init__(self):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)

  @always_comb
  def logic(self):
    in0 = self.in0
    in1 = self.in1
    cin = self.cin
    sum = self.sum
    cout = self.cout
    sum  <<= (in0 ^ in1) ^ cin
    cout <<= (in0 & in1) | (in0 & cin) | (in1 & cin)

class RippleCarryAdder(Synthesizable):
  def __init__(self, bits):
    self.in0 = InPort (bits)
    self.in1 = InPort (bits)
    self.sum = OutPort(bits)

    self.adders = [ FullAdder() for i in xrange(bits) ]

    for i in xrange(bits):
      self.adders[i].in0 <> self.in0[i]
      self.adders[i].in1 <> self.in1[i]
      self.adders[i].sum <> self.sum[i]

    for i in xrange(bits-1):
      self.adders[i+1].cin <> self.adders[i].cout
    self.adders[0].cin <> 0


v = ToVerilog()
#TODO: run pychecker?
one_bit = FullAdder()
one_bit.in0.value = 0b1
one_bit.in1.value = 0b1
one_bit.cin.value = 0b1
one_bit.logic()
print "// Simulation:"
print "// Inputs:",
print bin(one_bit.in0.value ),
print bin(one_bit.in1.value ),
print bin(one_bit.cin.value )
print "// Outputs:",
print bin(one_bit.sum.value ),
print bin(one_bit.cout.value )
print

v.elaborate( one_bit )
v.generate( one_bit, sys.stdout )

four_bit = RippleCarryAdder(4)
v.elaborate( four_bit )
v.generate( four_bit, sys.stdout )
