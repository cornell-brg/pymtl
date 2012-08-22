import unittest
from model import *

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

class BadSyncNextRead(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.out = OutPort( 1 )
  @posedge_clk
  def logic( self ):
    self.out.value = self.in0.next

class BadCombNextRead(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.out = OutPort( 1 )
  @combinational
  def logic( self ):
    self.out.value = self.in0.next

class TempNextAssign(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.out = OutPort( 1 )
  @combinational
  def logic( self ):
    next = self.in0.value
    self.out.value = next

class TempValueAssign(Model):
  def __init__(self):
    self.in0 = InPort( 1 )
    self.out = OutPort( 1 )
  @combinational
  def logic( self ):
    value = self.in0.value
    self.out.value = value


class TestSlicesVerilog(unittest.TestCase):

  def test_next_assign_exception(self):
    model = BadNextAssign()
    self.assertRaises(LogicSyntaxError, model.elaborate)

  def test_value_assign_exception(self):
    model = BadValueAssign()
    self.assertRaises(LogicSyntaxError, model.elaborate)

  def test_next_read_exception(self):
    model = BadSyncNextRead()
    self.assertRaises(LogicSyntaxError, model.elaborate)
    model = BadCombNextRead()
    self.assertRaises(LogicSyntaxError, model.elaborate)

  def test_temp_next_assign(self):
    model = TempNextAssign()
    # Should not throw an exception
    model.elaborate()

  def test_temp_value_assign(self):
    model = TempValueAssign()
    # Should not throw an exception
    model.elaborate()


if __name__ == '__main__':
  unittest.main()
