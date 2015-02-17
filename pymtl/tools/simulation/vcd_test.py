#=======================================================================
# vcd_test.py
#=======================================================================

import inspect

#=======================================================================
# Tests
#=======================================================================

# This imports all the SimulationTool tests. Below we will hack the
# setup_sim() function call in each module to use a special vcd version
# of the setup.

from SimulationTool_seq_test    import *
from SimulationTool_comb_test   import *
from SimulationTool_mix_test    import *
from SimulationTool_struct_test import *
from SimulationTool_wire_test   import *

#=======================================================================
# Test Config
#=======================================================================

#-----------------------------------------------------------------------
# local_setup_sim
#-----------------------------------------------------------------------
# - elaborate the module
# - create a simulator with the SimulationTool
# - create a vcd dump of the simulation
#
def local_setup_sim( model ):
  model.elaborate()

  model.vcd_file = \
    'pymtl.tools.simulation.vcd_test.{}.vcd'.format( model.class_name )

  sim = SimulationTool( model )
  return model, sim
