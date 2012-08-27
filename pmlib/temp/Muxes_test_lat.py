import unittest

from Muxes import *

class TestMux3( unittest.TestCase ):

  def setUp( self ):
    self.model = Mux3( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 1, 1, 2, 3,],
                   [ 1, 2, 1, 2, 3,],
                   [ 2, 3, 1, 2, 3,],
                   [ 1, 25, 18, 25, 42,],
                   [ 2, 42, 18, 25, 42,],
                   [ 0, 18, 18, 25, 42,],
                 ]

    for test in test_cases:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
    self.sim.dump_vcd( 'Mux3_test.vcd' )
    self.test_one

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux3.v' )


if __name__ == '__main__':
  unittest.main()
