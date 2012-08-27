#=========================================================================
# Unittest: Reg
#=========================================================================

import unittest

from regs import *

class TestReg( unittest.TestCase ):

  #=======================================================================
  # Reg
  #=======================================================================

  def test_Reg( self ):
    self.model = Reg( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_cases = [ [ 0,],
                   [ 1,],
                   [ 2,],
                   [ 3,],
                   [ 4,],
                   [ 1024,],
                   [ 32768,],
                 ]

    for test in test_cases:
      self.model.in_.value = test[0]
      self.sim.cycle()

      self.assertEquals( self.model.out.value, test[0] )

#    self.sim.dump_vcd( 'Reg_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'Reg.v' )

  #=======================================================================
  # RegEn
  #=======================================================================

  def test_RegEn( self ):
    self.model = RegEn( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_cases = [ [ 0, 0,],
                   [ 1, 1,],
                   [ 0, 2,],
                   [ 1, 3,],
                   [ 1, 4,],
                   [ 0, 1024,],
                   [ 0, 32768,],
                 ]

    # if en == 0, do not update test_result
    test_result = 0

    for test in test_cases:
      self.model.en.value = test[0]
      self.model.in_.value = test[1]
      self.sim.cycle()
      if test[0] == 1:
        test_result = test[1]

      # print out signals
#      print test_result, self.model.out.value, test[1]
      self.assertEquals( self.model.out.value, test_result )

#    self.sim.dump_vcd( 'RegEn_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'RegEn.v' )

  #=======================================================================
  # RegRst
  #=======================================================================

  def test_RegRst( self ):
    self.model = RegRst( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_cases = [ [ 0, 0,],
                   [ 1, 1,],
                   [ 0, 2,],
                   [ 0, 3,],
                   [ 1, 4,],
                   [ 1, 1024,],
                   [ 1, 32768,],
                 ]

    # if reset, test_result should become 0
    test_result = 0

    for test in test_cases:
      self.model.rst.value = test[0]
      self.model.in_.value = test[1]
      self.sim.cycle()
      if test[0] == 1:
        test_result = 0
      else:
        test_result = test[1]

      # print out signals
#      print test_result, self.model.out.value, test[1]
      self.assertEquals( self.model.out.value, test_result )

#    self.sim.dump_vcd( 'RegRst_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'RegRst.v' )

  #=======================================================================
  # RegEnRst
  #=======================================================================

  def test_RegEnRst( self ):
    self.model = RegEnRst( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

    test_cases = [ [ 0, 1, 0,],
                   [ 1, 1, 1,],
                   [ 0, 1, 2,],
                   [ 0, 1, 3,],
                   [ 1, 1, 4,],
                   [ 1, 1, 1024,],
                   [ 1, 1, 32768,],
                   [ 0, 0, 0,],
                   [ 1, 0, 1,],
                   [ 0, 0, 2,],
                   [ 0, 0, 3,],
                   [ 1, 0, 4,],
                   [ 1, 0, 1024,],
                   [ 1, 0, 32768,],
                 ]

    # if reset, test_result should become 0
    test_result = 0

    for test in test_cases:
      self.model.rst.value = test[0]
      self.model.en.value = test[1]
      self.model.in_.value = test[2]
      self.sim.cycle()
      if test[0] == 1:
        test_result = 0
      elif test[1] == 1:
        test_result = test[2]

      # print out signals
#      print test_result, self.model.out.value, test[0], test[1], test[2]
      self.assertEquals( self.model.out.value, test_result )

#    self.sim.dump_vcd( 'RegEnRst_test.vcd' )

    self.hdl = VerilogTranslationTool( self.model )
#    self.hdl.translate( 'RegEnRst.v' )

if __name__ == '__main__':
  unittest.main()
