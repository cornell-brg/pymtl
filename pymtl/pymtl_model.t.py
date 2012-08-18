import unittest
from pymtl_model import *

class BadNextAssign(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.in1 = InPort( 1 )
    self.out = OutPort( 1 )
  @combinational
  def logic( self ):
    if self.in0.value:
      self.out.next = self.in1.value

class BadValueAssign(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.in1 = InPort( 1 )
    self.out = OutPort( 1 )
  @posedge_clk
  def logic( self ):
    if self.in0.value:
      self.out.value = self.in1.value


class TestSlicesVerilog(unittest.TestCase):

  def test_next_assign_exception(self):
    model = BadNextAssign()
    self.assertRaises(Exception, model.elaborate)

  def test_value_assign_exception(self):
    model = BadValueAssign()
    self.assertRaises(Exception, model.elaborate)

#  def test_value_assign_exception(self):

if __name__ == '__main__':
  unittest.main()
