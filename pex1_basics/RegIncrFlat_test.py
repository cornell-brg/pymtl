import unittest

from RegIncrFlat import *

class TestRegIncrFlat(unittest.TestCase):

  def setUp(self):
    self.model = RegIncrFlat()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )
    self.sim.generate()

  def test_one(self):
    for i in range(10):
      self.model.in_.value = i
      self.sim.cycle()
      self.assertEqual( self.model.out.value, i + 1 )

  def test_vcd(self):
    VCDTool( self.sim, 'RegIncrFlat_test.vcd' )
    self.test_one()

  def test_translate(self):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.generate( 'RegIncrFlat.v' )


if __name__ == '__main__':
  unittest.main()
