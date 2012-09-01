#=========================================================================
# Unittest: Arithmetic components
#=========================================================================

import unittest

from arith import *

#-------------------------------------------------------------------------
# FullAdder unit test
#-------------------------------------------------------------------------

class TestFullAdder( unittest.TestCase ):

  def setUp( self ):
    self.model = FullAdder()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
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

  def test_vcd( self ):
#    self.sim.dump_vcd( 'FA_test.vcd' )
    self.test_one()

  def test_translate( self ):
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
                   [ 65535, 65535, 1, 65535, 1,],
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

#-------------------------------------------------------------------------
# Subtractor unit test
#-------------------------------------------------------------------------

class TestSub( unittest.TestCase ):

  def setUp( self ):
    self.model = Sub( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0, 0,],
                   [ 1, 0, 1,],
                   [ 0, 1, 65535,],
                   [ 1, 1, 0,],
                   [ 10, 4, 6,],
                   [ 321, 121, 200,],
                   [ 1024, 512, 512,],
                   [ 65535, 1, 65534,],
                   [ 65535, 65535, 0,],
                   [ 0, 65535, 1,],
                   [ 65534, 65535, 65535,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[2] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Sub_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Sub.v' )

#-------------------------------------------------------------------------
# Incrementer unit tests
#-------------------------------------------------------------------------
# Test1 for INC = 1
# Test2 for INC = 123
# Test3 for INC = 65537 % 65536 = 1
#

  #-----------------------------------------------------------------------
  # Incrementer unit test1
  #-----------------------------------------------------------------------

class TestInc1( unittest.TestCase ):

  def setUp( self ):
    self.model = Inc( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 1,],
                   [ 1, 2,],
                   [ 10, 11,],
                   [ 321, 322,],
                   [ 1024, 1025,],
                   [ 65535, 0,],
                   [ 65536, 1,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Inc_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Inc.v' )

  #-----------------------------------------------------------------------
  # Incrementer unit test2
  #-----------------------------------------------------------------------

class TestInc2( unittest.TestCase ):

  def setUp( self ):
    self.model = Inc( 16, 123 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 123,],
                   [ 1, 124,],
                   [ 10, 133,],
                   [ 321, 444,],
                   [ 1024, 1147,],
                   [ 65535, 122,],
                   [ 65536, 123,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Inc_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Inc.v' )

  #-----------------------------------------------------------------------
  # Incrementer unit test3
  #-----------------------------------------------------------------------

class TestInc3( unittest.TestCase ):

  def setUp( self ):
    self.model = Inc( 16, 65537 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 1,],
                   [ 1, 2,],
                   [ 10, 11,],
                   [ 321, 322,],
                   [ 1024, 1025,],
                   [ 65535, 0,],
                   [ 65536, 1,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Inc_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Inc.v' )

#-------------------------------------------------------------------------
# Zero-Extension unit test
#-------------------------------------------------------------------------

class TestZeroExt( unittest.TestCase ):

  def setUp( self ):
    self.model = ZeroExt( 16, 24 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0,],
                   [ 1,],
                   [ 10,],
                   [ 321,],
                   [ 1024,],
                   [ 65535,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[0] )
      self.assertEquals( self.model.out.width, 24 )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'ZeroExt_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'ZeroExt.v' )

#-------------------------------------------------------------------------
# Sign-Extension unit test
#-------------------------------------------------------------------------
# Endless loop
# TODO: find out the bug

#class TestSignExt( unittest.TestCase ):
#
#  def setUp( self ):
#    self.model = SignExt( 16, 32 )
#    self.model.elaborate()
#    self.sim = SimulationTool( self.model )
#
#  def test_one( self ):
#    print "\nSign extension module is not working, this test is not ready"
#    test_cases = [ [ 0, 0,],
#                   [ 1, 1,],
#                   [ 10, 10,],
#                   [ 127, 127,],
#                   [ 321, 321,],
#                   [ 1024, 1024,],
#                   [ 32767, 32767,],
#                   [ 32768, 4294934528,],
#                   [ 32769, 4294934529,],
#                   [ 32770, 4294934530,],
#                   [ 65535, 4294967295,],
#                 ]
#
#    for test in test_cases:
#      self.model.in_.value = test[0]
#      self.sim.cycle()
#
#      print self.model.in_.value, self.model.out.value, self.model.temp.value
#      self.assertEquals( self.model.out.value, test[1] )
#      self.assertEquals( self.model.out.width, 32 )
#
#  def test_vcd( self ):
##    self.sim.dump_vcd( 'SignExt_test.vcd' )
##    self.test_one()
#    pass
#
#  def test_translate( self ):
#    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'SignExt.v' )

#-------------------------------------------------------------------------
# Equal comparator unit test
#-------------------------------------------------------------------------

class TestCmpEQ( unittest.TestCase ):

  def setUp( self ):
    self.model = CmpEQ()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0, 1,],
                   [ 1, 1, 1,],
                   [ 10, 10, 1,],
                   [ 127, 127, 1,],
                   [ 321, 320, 0,],
                   [ 1024, 1024, 1,],
                   [ 32767, 32767, 1,],
                   [ 32768, 32767, 0,],
                   [ 32769, 32770, 0,],
                   [ 65535, 65535, 1,],
                   [ 65536, 65535, 0,],
                   [ 65536, 65536, 1,],
                   [ 65536, 65537, 0,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[2] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'CmpEQ_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'CmpEQ.v' )

#-------------------------------------------------------------------------
# Less-Than comparator unit test
#-------------------------------------------------------------------------

class TestCmpLT( unittest.TestCase ):

  def setUp( self ):
    self.model = CmpLT()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0, 0,],
                   [ 1, 1, 0,],
                   [ 0, 1, 1,],
                   [ 10, 10, 0,],
                   [ 11, 10, 0,],
                   [ 11, 12, 1,],
                   [ 127, 127, 0,],
                   [ 321, 320, 0,],
                   [ 1024, 1024, 0,],
                   [ 32767, 32767, 0,],
                   [ 32768, 32767, 0,],
                   [ 32769, 32770, 1,],
                   [ 65535, 65535, 0,],
                   [ 65536, 65535, 1,],
                   [ 65536, 65536, 0,],
                   [ 65536, 65537, 1,],
                   [ 65536, 1, 1,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[2] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'CmpLT_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'CmpLT.v' )

#-------------------------------------------------------------------------
# Greater-Than comparator unit test
#-------------------------------------------------------------------------

class TestCmpGT( unittest.TestCase ):

  def setUp( self ):
    self.model = CmpGT()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0, 0, 0,],
                   [ 1, 1, 0,],
                   [ 0, 1, 0,],
                   [ 10, 10, 0,],
                   [ 11, 10, 1,],
                   [ 11, 12, 0,],
                   [ 127, 127, 0,],
                   [ 321, 320, 1,],
                   [ 1024, 1024, 0,],
                   [ 32767, 32767, 0,],
                   [ 32768, 32767, 1,],
                   [ 32769, 32770, 0,],
                   [ 65535, 65535, 0,],
                   [ 65535, 65536, 1,],
                   [ 65536, 65535, 0,],
                   [ 65536, 65536, 0,],
                   [ 65536, 65537, 0,],
                   [ 1, 65536, 1,],
                 ]

    for test in test_cases:
      self.model.in0.value = test[0]
      self.model.in1.value = test[1]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[2] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'CmpGT_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'CmpGT.v' )

#-------------------------------------------------------------------------
# Sign unit test
#-------------------------------------------------------------------------

class TestSign( unittest.TestCase ):

  def setUp( self ):
    self.model = Sign( 4 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0b0000, 0b0000,],
                   [ 0b0001, 0b1111,],
                   [ 0b0101, 0b1011,],
                   [ 0b0111, 0b1001,],
                   [ 0b1001, 0b0111,],
                   [ 0b1010, 0b0110,],
                   [ 0b1101, 0b0011,],
                   [ 0b1110, 0b0010,],
                   [ 0b1111, 0b0001,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'Sign_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Sign.v' )

#-------------------------------------------------------------------------
# UnSign unit test
#-------------------------------------------------------------------------

class TestUnSign( unittest.TestCase ):

  def setUp( self ):
    self.model = UnSign( 4 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one( self ):
    test_cases = [ [ 0b0000, 0b0000,],
                   [ 0b0001, 0b0001,],
                   [ 0b0101, 0b0101,],
                   [ 0b0111, 0b0111,],
                   [ 0b1001, 0b0111,],
                   [ 0b1010, 0b0110,],
                   [ 0b1101, 0b0011,],
                   [ 0b1110, 0b0010,],
                   [ 0b1111, 0b0001,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[1] )

  def test_vcd( self ):
#    self.sim.dump_vcd( 'UnSign_test.vcd' )
    self.test_one()

  def test_translate( self ):
    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'UnSign.v' )


if __name__ == '__main__':
  unittest.main()
