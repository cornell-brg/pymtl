#=========================================================================
# RegIncrFlat Unit Tests
#=========================================================================

import unittest

from RegIncrFlat import *

#-------------------------------------------------------------------------
# Basic Test Suite
#-------------------------------------------------------------------------

class TestRegIncrFlat(unittest.TestCase):

  def setUp(self):
    self.model = RegIncrFlat()
    self.model.elaborate()
    self.sim = SimulationTool( self.model )

  def basic_cycle( self, in_, out ):
    self.model.in_.value = in_
    self.sim.cycle()
    self.assertEqual( self.model.out.value, out )

  def test_basic(self):

    self.model = RegIncrFlat()
    self.model.elaborate()

    self.sim = SimulationTool( self.model )

    self.basic_cycle(  0,  1 )
    self.basic_cycle(  1,  2 )
    self.basic_cycle( 10, 11 )
    self.basic_cycle( 13, 14 )


if __name__ == '__main__':
  unittest.main()

