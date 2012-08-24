import unittest

from SorterBehavioralLevel import *

class TestSorterBehavioralLevel(unittest.TestCase):

  def setUp(self):
    self.model = SorterBehavioralLevel()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )
    self.sim.generate()

  def test_one(self):
    test_cases = [ [ 1, 2, 3, 4],
                   [ 3, 5, 8, 2],
                   [ 9, 8, 7, 6],
                   [ 5, 4, 5, 5],
                   [ 5, 2, 9, 4],
                 ]

    print self.sim.num_cycles, self.model.line_trace()
    for test in test_cases:
      for i, input in enumerate(test):
        self.model.in_[ i ].value = input
      self.sim.cycle()
      print self.sim.num_cycles, self.model.line_trace()
      test.sort()
      for i, value in enumerate(test):
        self.assertEquals( self.model.out[ i ].value, value )


if __name__ == '__main__':
  unittest.main()
