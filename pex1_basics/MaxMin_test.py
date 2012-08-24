import unittest

from MaxMin import *

class TestMaxMin(unittest.TestCase):

  def setUp(self):
    self.model = MaxMin()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )
    self.sim.generate()

  def test_one(self):
    test_cases = [ [ 1, 2,],
                   [ 5, 3,],
                   [ 9, 8,],
                   [ 5, 5,],
                   [ 0, 2,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()
      test.sort()
      self.assertEquals( self.model.min.value, test[0] )
      self.assertEquals( self.model.max.value, test[1] )

if __name__ == '__main__':
  unittest.main()
