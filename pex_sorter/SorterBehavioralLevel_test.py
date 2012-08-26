import unittest

from SorterBehavioralLevel import *

class TestSorterBehavioralLevel(unittest.TestCase):

  def setUp(self):
    self.model = SorterBehavioralLevel()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

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

  def test_vcd(self):
    self.sim.dump_vcd( 'SorterBehavioralLevel_test.vcd' )
    self.test_one()

  # Not Translatable!
  #def test_translate(self):
  #  self.hdl = VerilogTranslationTool( self.model )
  #  self.hdl.translate( 'SorterBehavioralLevel.v' )


if __name__ == '__main__':
  unittest.main()
