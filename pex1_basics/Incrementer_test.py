import unittest

from Incrementer import *

class TestIncrementer(unittest.TestCase):

  def setUp(self):
    self.model = Incrementer( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )
    self.sim.generate()

  def test_one(self):
    for i in range(10):
      self.model.in_.value = i
      self.sim.cycle()
      self.assertEqual( self.model.out.value, i + 1 )

if __name__ == '__main__':
  unittest.main()
