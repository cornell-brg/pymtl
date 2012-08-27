import unittest

from Muxes import *

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

#    self.sim.dump_vcd( 'Mux3_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Mux3.v' )


if __name__ == '__main__':
  unittest.main()
