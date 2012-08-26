import unittest

from SorterRTLFlat import *

class TestSorterRTLFlat(unittest.TestCase):

  def setUp(self):
    self.model = SorterRTLFlat()
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
    for i in range( len(test_cases) + 1 ):
      # Only set inputs for N cycles
      if i < len(test_cases):
        test = test_cases[i]
        self.model.in_0.value = test[0]
        self.model.in_1.value = test[1]
        self.model.in_2.value = test[2]
        self.model.in_3.value = test[3]
      # Cycle the simulator
      self.sim.cycle()
      print self.sim.num_cycles, self.model.line_trace()
      # Only check outputs after N delay cycles
      if i >= 1:
        test = test_cases[i - 1]
        test.sort()
        self.assertEquals( self.model.out_0.value, test[0] )
        self.assertEquals( self.model.out_1.value, test[1] )
        self.assertEquals( self.model.out_2.value, test[2] )
        self.assertEquals( self.model.out_3.value, test[3] )

  def test_vcd(self):
    VCDTool( self.sim, 'SorterRTLFlat_test.vcd' )
    self.test_one()

  def test_translate(self):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'SorterRTLFlat.v' )


if __name__ == '__main__':
  unittest.main()
