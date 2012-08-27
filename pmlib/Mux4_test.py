import unittest

from Muxes import *

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


if __name__ == '__main__':
  unittest.main()
