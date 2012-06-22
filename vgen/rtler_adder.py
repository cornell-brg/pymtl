import sys

from rtler_vbase import *

"""
Target:

class FullAdder (foo):

 def __init__(self):
   self.in0  = InputPort(1)
   self.in1  = InputPort(1)
   self.cin  = InputPort(1)
   self.sum  = OutputPort(1)
   self.cout = OutputPort(1)

class RippleCarryAdder (foo):

 def __init__(self):
   self.in0  = InputPort(32)
   self.in1  = InputPort(32)
   self.sum  = OutputPort(32)

 def elaborate(self):

   self.adders = [ FullAdder() for i in xrange(32) ]

   for i in xrange(32):
     self.adders[i].in0 <> self.in0[i]
     self.adders[i].in1 <> self.in1[i]
     self.adders[i].out <> self.out[i]

   self.adders[0].cin.wr(0)
   for i in xrange(31):
     self.adders[i+1].cin <> self.adders[i].cout

"""

class InPort(VerilogPort):
  def __init__(self, width=None, name=None):
    super(InPort, self).__init__('input', width, name)

class OutPort(VerilogPort):
  def __init__(self, width=None, name=None):
    super(OutPort, self).__init__('output', width, name)

class FullAdder(ToVerilog):
  def __init__(self):
    # Can't find a way to make the name the instance name...
    self.name = 'FA_instance_name'
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)

class RippleCarryAdder(ToVerilog):
  def __init__(self):
    self.name = 'RCA_instance_name'
    self.in0 = InPort (4)
    self.in1 = InPort (4)
    self.out = OutPort(4)

    self.adders = [ FullAdder() for i in xrange(4) ]

    for i in xrange(4):
      #self.adders[i].in0 <> self.in0[i]
      #self.adders[i].in1 <> self.in1[i]
      #self.adders[i].out <> self.out[i]
      print '@ ', self.in0.connection
      self.adders[i].in0 <> self.in0[i]
      self.adders[i].in1 <> self.in1[i]
      #self.adders[i].sum <> self.out
      self.out <> self.adders[i].sum
      #print type(self.adders[i].in0), self.adders[i].in0
      #print self.in0[i]


#one_bit = FullAdder()
#one_bit.generate_new(sys.stdout)
four_bit = RippleCarryAdder()
four_bit.elaborate()
four_bit.generate(sys.stdout)
