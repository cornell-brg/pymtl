#=========================================================================
# Ueittest: bit operations
#=========================================================================

import unittest

from bit import *

#-------------------------------------------------------------------------
# reverse unit test
#-------------------------------------------------------------------------

class TestREV( unittest.TestCase ):

  def setUp( self ):
    self.model = REV( 4 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 15,],
                   [ 1, 14,],
                   [ 5, 10,],
                   [ 7, 8,],
                   [ 9, 6,],
                   [ 10, 5,],
                   [ 11, 4,],
                   [ 12, 3,],
                   [ 13, 2,],
                   [ 14, 1,],
                   [ 15, 0,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'REV_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'REV.v' )

#-------------------------------------------------------------------------
# MSB unit test
#-------------------------------------------------------------------------

class TestMSB( unittest.TestCase ):

  def setUp( self ):
    self.model = MSB( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0,],
                   [ 1, 0,],
                   [ 5, 0,],
                   [ 7, 0,],
                   [ 8, 0,],
                   [ 9, 0,],
                   [ 10, 0,],
                   [ 11, 0,],
                   [ 12, 0,],
                   [ 13, 0,],
                   [ 14, 0,],
                   [ 15, 0,],
                   [ 32767, 0,],
                   [ 32768, 1,],
                   [ 32770, 1,],
                   [ 65535, 1,],
                   [ 65536, 0,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )
      self.assertEquals( self.model.out.width, 1 )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'MSB_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'MSB.v' )

#-------------------------------------------------------------------------
# DoubleConnection unit test
#-------------------------------------------------------------------------

class TestDoubleCon( unittest.TestCase ):

  def setUp( self ):
    self.model = DoubleCon()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    print "\nDouble connection test currently fails"
#    test_cases = [ [ 0, 0,],
#                   [ 1, 3,],
#                 ]
#
#    for test in test_cases:
#      self.model.in_.value = test[0]
#      self.sim.cycle()
#
#      self.assertEquals( self.model.out.width, 2 )
#      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'DoubleCon_test.vcd' )
#    self.test_one()
    pass

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'DoubleCon.v' )

#-------------------------------------------------------------------------
# TripleConnection unit test
#-------------------------------------------------------------------------

class TestTriCon( unittest.TestCase ):

  def setUp( self ):
    self.model = TriCon()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    print "\nTriple connection test currently fails"
#    test_cases = [ [ 0, 0,],
#                   [ 1, 8,],
#                 ]
#
#    for test in test_cases:
#      self.model.in_.value = test[0]
#      self.sim.cycle()
#
#      self.assertEquals( self.model.out.width, 3 )
#      self.assertEquals( self.model.out.value, test[1] )

if __name__ == '__main__':
  unittest.main()

