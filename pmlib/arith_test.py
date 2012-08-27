#=========================================================================
# Unittest: Arithmetic components
#=========================================================================

import unittest

from arith import *

#-------------------------------------------------------------------------
# FullAdder unit test
#-------------------------------------------------------------------------

class TestFullAdder( unittest.TestCase ):

  def test_FA( self ):
    self.model = FullAdder()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_cases = [ [ 0, 0, 0, 0, 0,],
                   [ 1, 0, 0, 1, 0,],
                   [ 0, 1, 0, 1, 0,],
                   [ 1, 1, 0, 0, 1,],
                   [ 0, 0, 1, 1, 0,],
                   [ 1, 0, 1, 0, 1,],
                   [ 0, 1, 1, 0, 1,],
                   [ 1, 1, 1, 1, 1,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.model.cin.value = test[2]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[3] )
      self.assertEquals( self.model.cout.value, test[4] )

#    self.sim.dump_vcd( 'FA_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'FA.v' )

#-------------------------------------------------------------------------
# Adder unit test
#-------------------------------------------------------------------------

class TestAdder( unittest.TestCase ):

  def setUp( self ):
    self.model = Adder( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0, 0, 0, 0,],
                   [ 1, 0, 0, 1, 0,],
                   [ 0, 1, 0, 1, 0,],
                   [ 1, 1, 0, 2, 0,],
                   [ 0, 0, 1, 1, 0,],
                   [ 1, 0, 1, 2, 0,],
                   [ 0, 1, 1, 2, 0,],
                   [ 1, 1, 1, 3, 0,],
                   [ 10, 21, 0, 31, 0,],
                   [ 65534, 1, 0, 65535, 0,],
                   [ 65534, 1, 1, 0, 1,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.model.cin.value = test[2]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[3] )
      self.assertEquals( self.model.cout.value, test[4] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Adder_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Adder.v' )


if __name__ == '__main__':
  unittest.main()
