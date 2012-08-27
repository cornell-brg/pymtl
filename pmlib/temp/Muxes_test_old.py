import unittest

from Muxes import *

class TestMux2( unittest.TestCase ):

  def setUp( self ):
    self.model = Mux2( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 1, 0, 0,],
                   [ 0, 1, 1, 1,],
                   [ 42, 25, 0, 42,],
                   [ 42, 25, 1, 25,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.model.sel.value = test[2]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[3] )

  def test_vcd( self ):
    self.sim.dump_vcd( 'Mux2_test.vcd' )
    self.test_one

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux2.v' )


class TestMux3( unittest.TestCase ):

  def setUp( self ):
    self.model = Mux3( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 1, 2, 0, 0,],
                   [ 0, 1, 2, 1, 1,],
                   [ 0, 1, 2, 2, 2,],
                   [ 42, 25, 18, 0, 42,],
                   [ 42, 25, 18, 2, 18,],
                   [ 42, 25, 18, 1, 25,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.model.in2.value = test[2]
      self.model.sel.value = test[3]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[4] )

  def test_vcd( self ):
    self.sim.dump_vcd( 'Mux3_test.vcd' )
    self.test_one

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux3.v' )


if __name__ == '__main__':
  unittest.main()
