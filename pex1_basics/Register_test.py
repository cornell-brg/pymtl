import unittest

from Register import *

class TestRegister(unittest.TestCase):

  def setUp(self):
    self.model = Register( 16 )
    self.model.elaborate()
    self.sim = SimulationTool( self.model )
    self.sim.generate()

  def test_one(self):
    test_vectors = [0, 5, 8, 1, 9, 12, 0, 4]
    for i, value in enumerate( test_vectors[1:] ):
      self.model.in_.value = value
      self.assertEqual( self.model.out.value, test_vectors[i] )
      self.sim.cycle()
      self.assertEqual( self.model.out.value, value )

  def test_vcd(self):
    VCDTool( self.sim, 'Register_test.vcd' )
    self.test_one()

  def test_translate(self):
    self.hdl = VerilogTranslationTool( self.model )
    self.hdl.generate( 'Register.v' )


if __name__ == '__main__':
  unittest.main()
