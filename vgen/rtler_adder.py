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

import inspect
def always_comb(fn):
  def wrapped(self):
    #for x,y in inspect.getmembers(fn, inspect.isdatadescriptor):
    #  print x,y
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
    sim.add_callback(self.in0, self.logic)
    sim.add_callback(self.in1, self.logic)
    sim.add_callback(self.cin, self.logic)

  @always_comb
  def logic(self):
    in0 = self.in0
    in1 = self.in1
    cin = self.cin
    sum = self.sum
    cout = self.cout
    #print "FUNC", "in0", in0.value, "in1", in1.value, "cin", cin.value
    sum  <<= (in0 ^ in1) ^ cin
    cout <<= (in0 & in1) | (in0 & cin) | (in1 & cin)


class AdderChain(Synthesizable):
  def __init__(self, depth):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
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

#print "// Simulate FullAdder:"
#TODO: run pychecker?
#one_bit = FullAdder()
#import itertools
#for x,y,z in itertools.product([0,1], [0,1], [0,1]):
#  one_bit.in0.value = x
#  one_bit.in1.value = y
#  one_bit.cin.value = z
#  one_bit.logic()
#  print "// Inputs:",
#  print one_bit.in0.value,
#  print one_bit.in1.value,
#  print one_bit.cin.value
#  print "// Outputs:",
#  print "sum:",  one_bit.sum.value,
#  print "cout:", one_bit.cout.value
#v.elaborate( one_bit )
#v.generate( one_bit, sys.stdout )

print "// Simulate AdderChain:"
two_test = AdderChain( 1 )
v.elaborate( two_test )
two_test.in0.value = 1
two_test.in1.value = 1
sim.cycle()
print "// Result:", two_test.sum.value
#v.generate( two_test, sys.stdout )

#print "// Simulate RippleCarryAdder:"
#four_bit = RippleCarryAdder(4)
#v.elaborate( four_bit )
#four_bit.in0.value = 5
#four_bit.in1.value = 8
#sim.cycle()
#print "// Result:", four_bit.sum.value
#v.generate( four_bit, sys.stdout )
