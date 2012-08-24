import unittest

from SorterCycleLevel import *

class TestSorterCycleLevel(unittest.TestCase):

  def setUp(self):
    self.model = SorterCycleLevel()
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
    for i in range( len(test_cases) + 1 ):
      # Only set inputs for N cycles
      if i < len(test_cases):
        test = test_cases[i]
        for j, input in enumerate(test):
          self.model.in_[ j ].value = input
      # Cycle the simulator
      self.sim.cycle()
      print self.sim.num_cycles, self.model.line_trace()
      # Only check outputs after N delay cycles
      if i >= 1:
        test = test_cases[i - 1]
        test.sort()
        for j, value in enumerate(test):
          self.assertEquals( self.model.out[ j ].value, value )


if __name__ == '__main__':
  unittest.main()
