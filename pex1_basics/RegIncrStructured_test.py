import unittest

from RegIncrStructured import *

class TestRegIncrStructured(unittest.TestCase):

  def setUp(self):
    self.model = RegIncrStructured( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def test_one(self):
    for i in range(10):
      self.model.in_.value = i
      self.sim.cycle()
      self.assertEqual( self.model.out.value, i + 1 )

  def test_vcd(self):
    VCDTool( self.sim, 'RegIncrStructured_test.vcd' )
    self.test_one()

  def test_translate(self):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.translate( 'RegIncrStructured.v' )


if __name__ == '__main__':
  unittest.main()
