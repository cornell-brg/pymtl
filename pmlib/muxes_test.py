import unittest

from muxes import *

class TestMux2( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux2( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 1, 1, 2,],
                   [ 1, 2, 1, 2,],
                   [ 1, 25, 18, 25,],
                   [ 0, 18, 18, 25,],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

    self.sim.dump_vcd( 'Mux2_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux2.v' )

class TestMux3( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux3( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 1, 1, 2, 3,],
                   [ 1, 2, 1, 2, 3,],
                   [ 2, 3, 1, 2, 3,],
                   [ 1, 25, 18, 25, 42,],
                   [ 2, 42, 18, 25, 42,],
                   [ 0, 18, 18, 25, 42,],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

    self.sim.dump_vcd( 'Mux3_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux3.v' )

class TestMux4( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux4( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 18, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 25, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 2, 42, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 3, 56, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 2, 3, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 3, 4, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 0, 1, 1, 2, 3, 4, 5, 6, 7, 8],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.model.in3.value = test[5]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

#    self.sim.dump_vcd( 'Mux4_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Mux4.v' )

class TestMux5( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux5( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 18, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 25, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 2, 42, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 3, 56, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 4, 74, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 4, 5, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 2, 3, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 3, 4, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 0, 1, 1, 2, 3, 4, 5, 6, 7, 8],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.model.in3.value = test[5]
      self.model.in4.value = test[6]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

#    self.sim.dump_vcd( 'Mux5_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Mux5.v' )

class TestMux6( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux6( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 18, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 25, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 2, 42, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 3, 56, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 4, 74, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 5, 13, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 5, 6, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 4, 5, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 2, 3, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 3, 4, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 0, 1, 1, 2, 3, 4, 5, 6, 7, 8],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.model.in3.value = test[5]
      self.model.in4.value = test[6]
      self.model.in5.value = test[7]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

#    self.sim.dump_vcd( 'Mux6_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Mux6.v' )

class TestMux7( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux7( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 18, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 25, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 2, 42, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 3, 56, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 4, 74, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 5, 13, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 6, 55, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 6, 7, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 5, 6, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 4, 5, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 2, 3, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 3, 4, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 0, 1, 1, 2, 3, 4, 5, 6, 7, 8],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.model.in3.value = test[5]
      self.model.in4.value = test[6]
      self.model.in5.value = test[7]
      self.model.in6.value = test[8]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

#    self.sim.dump_vcd( 'Mux7_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Mux7.v' )

class TestMux8( unittest.TestCase ):

  def test_model( self ):
    self.model = Mux8( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_model = [ [ 0, 18, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 25, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 2, 42, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 3, 56, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 4, 74, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 5, 13, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 6, 55, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 7, 43, 18, 25, 42, 56, 74, 13, 55, 43],
                   [ 1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 6, 7, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 5, 6, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 4, 5, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 2, 3, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 3, 4, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 7, 8, 1, 2, 3, 4, 5, 6, 7, 8],
                   [ 0, 1, 1, 2, 3, 4, 5, 6, 7, 8],
                 ]

    for test in test_model:
      self.model.sel.value = test[0]
      self.model.in0.value = test[2]
      self.model.in1.value = test[3]
      self.model.in2.value = test[4]
      self.model.in3.value = test[5]
      self.model.in4.value = test[6]
      self.model.in5.value = test[7]
      self.model.in6.value = test[8]
      self.model.in7.value = test[9]
      self.sim.cycle()
      self.assertEquals( self.model.out.value, test[1] )

    self.sim.dump_vcd( 'Mux8_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'Mux8.v' )


if __name__ == '__main__':
  unittest.main()
