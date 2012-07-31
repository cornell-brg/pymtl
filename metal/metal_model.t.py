import unittest
from metal_model import *

class TestNode(unittest.TestCase):

  def setUp(self):
    self.reg = Node(8)

  def test_init_write(self):
    self.reg.next = 2
    self.assertEqual( self.reg.value, 0 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 2 )

  def test_second_write(self):
    self.reg.next = 5
    self.reg.clock()
    self.reg.next = 7
    self.reg.next = 8
    self.assertEqual( self.reg.value, 5 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 8 )

if __name__ == '__main__':
  unittest.main()
