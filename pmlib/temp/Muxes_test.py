import unittest

from Muxes import *

class TestMux2( unittest.TestCase ):

  def test_mux2( self ):
    self.mux2 = Mux2( 16 )
    self.mux2.elaborate()
    self.sim = SimulationTool( self.mux2 )

    test_mux2 = [ [ 0, 1, 1, 2,],
                   [ 1, 2, 1, 2,],
                   [ 1, 25, 18, 25,],
                   [ 0, 18, 18, 25,],
                 ]

    for test in test_mux2:
      self.mux2.sel.value = test[0]
      self.mux2.in0.value = test[2]
      self.mux2.in1.value = test[3]
      self.sim.cycle()
      self.assertEquals( self.mux2.out.value, test[1] )

    self.sim.dump_vcd( 'Mux2_test.vcd' )

    self.hdl = VerilogTranslationTool( self.mux2 )
    self.hdl.translate( 'Mux2.v' )

  def test_mux3( self ):
    self.mux3 = Mux3( 16 )
    self.mux3.elaborate()
    self.sim = SimulationTool( self.mux3 )

    test_mux3 = [ [ 0, 1, 1, 2, 3,],
                   [ 1, 2, 1, 2, 3,],
                   [ 2, 3, 1, 2, 3,],
                   [ 1, 25, 18, 25, 42,],
                   [ 2, 42, 18, 25, 42,],
                   [ 0, 18, 18, 25, 42,],
                 ]

    for t in test_mux3:
#      self.mux3.sel.value = t[0]
      self.mux3.in0.value = t[2]
      self.mux3.in1.value = t[3]
      self.mux3.in2.value = t[4]
      self.sim.cycle()
      self.assertEquals( self.mux3.out.value, t[1] )

    self.sim.dump_vcd( 'Mux3_test.vcd' )

    self.hdl = VerilogTranslationTool( self.mux3 )
    self.hdl.translate( 'Mux3.v' )


if __name__ == '__main__':
  unittest.main()
