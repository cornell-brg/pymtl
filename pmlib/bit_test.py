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
    test_cases = [ [ 0b0000, 0b1111,],
                   [ 0b0001, 0b1110,],
                   [ 0b0101, 0b1010,],
                   [ 0b0111, 0b1000,],
                   [ 0b1001, 0b0110,],
                   [ 0b1010, 0b0101,],
                   [ 0b1101, 0b0010,],
                   [ 0b1110, 0b0001,],
                   [ 0b1111, 0b0000,],
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
    test_cases = [ [ 0x0000, 0,],
                   [ 0x0001, 0,],
                   [ 0x0107, 0,],
                   [ 0x1111, 0,],
                   [ 0x1fff, 0,],
                   [ 0x7fff, 0,],
                   [ 0x8000, 1,],
                   [ 0x8001, 1,],
                   [ 0x8111, 1,],
                   [ 0xbeef, 1,],
                   [ 0xffff, 1,],
                   [ 0x10000, 0,],
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
#
#  def test_vcd( self ):
#    self.sim.dump_vcd( 'DoubleCon_test.vcd' )
#    self.test_one()
#    pass
#
#  def test_translate( self ):
#    self.hdl = VerilogTranslationTool( self.model )
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
#                   [ 1, 7,],
#                 ]
#
#    for test in test_cases:
#      self.model.in_.value = test[0]
#      self.sim.cycle()
#
#      self.assertEquals( self.model.out.width, 3 )
#      self.assertEquals( self.model.out.value, test[1] )
#
#  def test_translate( self ):
#    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'TriCon.v' )

#-------------------------------------------------------------------------
# Concatenater unit test
#-------------------------------------------------------------------------

class TestCAT( unittest.TestCase ):

  def setUp( self ):
    self.model = CAT( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0x0000, 0x0000, 0x00000000,],
                   [ 0x0001, 0x0008, 0x00080001,],
                   [ 0x5555, 0xaaaa, 0xaaaa5555,],
                   [ 0xffff, 0x1111, 0x1111ffff,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()

      self.assertEquals( self.model.out.width, 32 )
      self.assertEquals( self.model.out.value, test[2] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'CAT_test.vcd' )
#    self.test_one()
    pass

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'CAT.v' )

#-------------------------------------------------------------------------
# Extend2 unit test
#-------------------------------------------------------------------------

class TestEXT2( unittest.TestCase ):

  def setUp( self ):
    self.model = EXT2( 2 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0x0, 0x00,],
                   [ 0x1, 0x05,],
                   [ 0x6, 0x0a,],
                   [ 0xf, 0x0f,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.width, 4 )
      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'EXT2_test.vcd' )
#    self.test_one()
    pass

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'EXT2.v' )

#-------------------------------------------------------------------------
# ExtendN unit test
#-------------------------------------------------------------------------

#class TestEXTN( unittest.TestCase ):
#
#  def setUp( self ):
#    self.model = EXTN( 4, 5 )
#    self.model.elaborate()
#    self.sim = SimulationTool( self.model )
#
#  def test_one( self ):
#    test_cases = [ [ 0x0, 0x00000,],
#                   [ 0x1, 0x11111,],
#                   [ 0x6, 0x66666,],
#                   [ 0xf, 0xfffff,],
#                 ]
#
#    for test in test_cases:
#      self.model.in_.value = test[0]
#      self.sim.cycle()
#
#      self.assertEquals( self.model.out.width, 20 )
#      self.assertEquals( self.model.out.value, test[1] )
#
#  def test_vcd( self ):
#    self.sim.dump_vcd( 'EXTN_test.vcd' )
#    self.test_one()
#    pass
#
#  def test_translate( self ):
#    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'EXTN.v' )


if __name__ == '__main__':
  unittest.main()

