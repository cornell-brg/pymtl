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

if __name__ == '__main__':
  unittest.main()
