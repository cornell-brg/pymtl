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
    self.type  = 'input'
    self.width = width
    self.name  = name

class OutPort(VerilogPort):
  def __init__(self, width=None, name=None):
    self.type  = 'output'
    self.width = width
    self.name  = name

class FullAdder(ToVerilog):
  def __init__(self):
    self.name = 'FullAdder'
    self.in0  = InPort (1, 'in0')
    self.in1  = InPort (1, 'in1')
    self.cin  = InPort (1, 'cin')
    self.sum  = OutPort(1, 'sum')
    self.cout = OutPort(1, 'cout')
    self.ports = [self.in0, self.in1, self.cin, self.sum, self.cout]
    self.wires = None
    self.submodules = None


one_bit = FullAdder()
one_bit.generate(sys.stdout)
