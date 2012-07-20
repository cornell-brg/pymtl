import sys

from rtler_vbase import *
from rtler_simulate import *

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


class FullAdder(VerilogModule):
  def __init__(self):
    # Can't set the instance name of each port during init, but can during
    # elaboration by walking the Top-Level Module's __dict__ and checking types.
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)

  @combinational
  def logic(self):
    in0 = self.in0
    in1 = self.in1
    cin = self.cin
    sum = self.sum
    cout = self.cout
    sum  <<= (in0 ^ in1) ^ cin
    cout <<= (in0 & in1) | (in0 & cin) | (in1 & cin)


class AdderChain(VerilogModule):
  def __init__(self, depth):
    # Can't set the instance name of each port during init, but can during
    # elaboration by walking the Top-Level Module's __dict__ and checking types.
    # This might be an argument for moving the connectivity stuff below into a
    # separate elaborate() function, instead of in the constructor?
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.sum  = OutPort(1)

    self.adders = [ FullAdder() for i in xrange(depth) ]
    self.adders[0].in0 <> self.in0
    self.adders[0].in1 <> self.in1
    self.adders[0].cin <> 0

    for i in xrange(1, depth):
      self.adders[i].in0 <> self.adders[i-1].sum
      self.adders[i].in1 <> 1
      self.adders[i].cin <> 0

    self.sum <> self.adders[-1].sum


class RippleCarryAdder(VerilogModule):
  def __init__(self, bits):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
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


class ManyAdders(VerilogModule):
  def __init__(self, bits, num_adders):
    self.in0 = InPort ( bits )
    self.in1 = [ InPort ( bits ) for i in xrange( num_adders ) ]
    self.sum = [ OutPort( bits ) for i in xrange( num_adders ) ]

    self.rc_adders = [ RippleCarryAdder( bits ) for i in xrange( num_adders ) ]

    for i in xrange( num_adders ):
      self.rc_adders[i].in0 <> self.in0
      self.rc_adders[i].in1 <> self.in1[i]
      self.rc_adders[i].sum <> self.sum[i]


