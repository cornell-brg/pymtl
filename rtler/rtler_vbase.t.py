import unittest
from rtler_vbase import *

class TestRegisterNode(unittest.TestCase):

  def setUp(self):
    self.reg = RegisterNode(8)

  def test_init_write(self):
    self.reg.value = 2
    self.assertEqual( self.reg.value, 0 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 2 )

  def test_second_write(self):
    self.reg.value = 5
    self.reg.clock()
    self.reg.value = 7
    self.reg.value = 8
    self.assertEqual( self.reg.value, 5 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 8 )

class TestPortOperations(unittest.TestCase):

  def assign(self, valA, valB):
    self.portA = valA
    self.portB = valB

  def setUp(self):
    self.portA = VerilogPort(width=8)
    self.portB = VerilogPort(width=8)

  #TODO: test all __r<op>__ implementations!
  def test_and(self):
    self.assign(8, 8)
    x = self.portA & self.portB
    self.assertEqual(x, 8)
    self.assign(8, 4)
    x = self.portA & self.portB
    self.assertEqual(x, 0)
    self.assign(0b11001010, 0b11110000)
    x = self.portA & self.portB
    self.assertEqual(x, 0b11000000)

  def test_or(self):
    self.assign(8, 8)
    x = self.portA | self.portB
    self.assertEqual(x, 8)
    self.assign(8, 4)
    x = self.portA | self.portB
    self.assertEqual(x, 12)
    self.assign(0b11001010, 0b11110000)
    x = self.portA | self.portB
    self.assertEqual(x, 0b11111010)

  def test_xor(self):
    self.assign(8, 8)
    x = self.portA ^ self.portB
    self.assertEqual(x, 0)
    self.assign(8, 4)
    x = self.portA ^ self.portB
    self.assertEqual(x, 12)
    self.assign(0b11001010, 0b11110000)
    x = self.portA ^ self.portB
    self.assertEqual(x, 0b00111010)

  def test_add(self):
    self.assign(8, 8)
    x = self.portA + self.portB
    self.assertEqual(x, 16)
    self.assign(8, 0)
    x = self.portA + self.portB
    self.assertEqual(x, 8)
    self.assign(8, -4)
    x = self.portA + self.portB
    self.assertEqual(x, 4)

  def test_sub(self):
    self.assign(8, 8)
    x = self.portA - self.portB
    self.assertEqual(x, 0)
    self.assign(8, 4)
    x = self.portA - self.portB
    self.assertEqual(x, 4)
    self.assign(2, 4)
    x = self.portA - self.portB
    self.assertEqual(x, -2)

  # TODO
  #def test_mul(self):
  #def test_mod(self):
  #def test_div(self):

  def test_lshift(self):
    self.assign(8, 4)
    x = self.portA << self.portB
    self.assertEqual(x, 128)
    self.assign(8, 0)
    x = self.portA << self.portB
    self.assertEqual(x, 8)
    # TODO: this fails! Fix!
    self.assign(8, 8)
    x = self.portA << self.portB
    self.assertEqual(x, 0)

  def test_rshift(self):
    self.assign(8, 4)
    x = self.portA >> self.portB
    self.assertEqual(x, 0)
    self.assign(8, 0)
    x = self.portA >> self.portB
    self.assertEqual(x, 8)
    self.assign(8, 2)
    x = self.portA >> self.portB
    self.assertEqual(x, 2)

  def test_lt(self):
    self.assign(8, 4)
    x = self.portA < self.portB
    self.assertEqual(x, 0)
    self.assign(8, 12)
    x = self.portA < self.portB
    self.assertEqual(x, 1)
    self.assign(8, 8)
    x = self.portA < self.portB
    self.assertEqual(x, 0)

  def test_gt(self):
    self.assign(8, 4)
    x = self.portA > self.portB
    self.assertEqual(x, 1)
    self.assign(8, 12)
    x = self.portA > self.portB
    self.assertEqual(x, 0)
    self.assign(8, 8)
    x = self.portA > self.portB
    self.assertEqual(x, 0)

  def test_lte(self):
    self.assign(8, 4)
    x = self.portA <= self.portB
    self.assertEqual(x, 0)
    self.assign(8, 12)
    x = self.portA <= self.portB
    self.assertEqual(x, 1)
    self.assign(8, 8)
    x = self.portA <= self.portB
    self.assertEqual(x, 1)

  def test_gte(self):
    self.assign(8, 4)
    x = self.portA >= self.portB
    self.assertEqual(x, 1)
    self.assign(8, 12)
    x = self.portA >= self.portB
    self.assertEqual(x, 0)
    self.assign(8, 8)
    x = self.portA >= self.portB
    self.assertEqual(x, 1)

  def test_eq(self):
    self.assign(8, 4)
    x = self.portA == self.portB
    self.assertEqual(x, 0)
    self.assign(8, 12)
    x = self.portA == self.portB
    self.assertEqual(x, 0)
    self.assign(8, 8)
    x = self.portA == self.portB
    self.assertEqual(x, 1)
    # TODO: doesn't pass, should it?
    self.assign(0b11111111, -1)
    x = self.portA == self.portB
    self.assertEqual(x, 1)

  def test_neq(self):
    self.assign(8, 4)
    x = self.portA != self.portB
    self.assertEqual(x, 1)
    self.assign(8, 12)
    x = self.portA != self.portB
    self.assertEqual(x, 1)
    self.assign(8, 8)
    x = self.portA != self.portB
    self.assertEqual(x, 0)
    x = self.portA != 8
    self.assertEqual(x, 0)

if __name__ == '__main__':
  unittest.main()
