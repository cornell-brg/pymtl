import unittest

from vcd import *
from simulate import *
from simulate_test import *

import simulate
simulate.dump_vcd = True

def setUp(self):
  self.temp_file = self.id().split('.')[-1] + '.vcd'
  self.fd = open(self.temp_file, 'w+')

def setup_sim(self, model):
  model.elaborate()
  sim = SimulationTool(model)
  sim.generate()
  VCDTool(sim, self.fd)
  simulate.o = self.fd
  if debug_verbose:
    debug_utils.port_walk(model)
  return sim

TestSlicesSim.setUp              = setUp
TestSlicesSim.setup_sim          = setup_sim
TestCombinationalSim.setUp       = setUp
TestCombinationalSim.setup_sim   = setup_sim
TestPosedgeClkSim.setUp          = setUp
TestPosedgeClkSim.setup_sim      = setup_sim
TestCombAndPosedge.setUp         = setUp
TestCombAndPosedge.setup_sim     = setup_sim


if __name__ == '__main__':
  unittest.main()
