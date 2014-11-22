#=======================================================================
# vcd_test.py
#=======================================================================

import inspect

# This imports all the SimulationTool tests. Below we will hack the
# setup_sim() function call in each module to use a special vcd version
# of the setup.

from SimulationTool_seq_test    import *
from SimulationTool_comb_test   import *
from SimulationTool_mix_test    import *
from SimulationTool_struct_test import *
from SimulationTool_wire_test   import *

#-----------------------------------------------------------------------
# vcd_setup_sim
#-----------------------------------------------------------------------
# Elaborate the module, create a SimulationTool, and also create a vcd
# dump of the simulation.
def vcd_setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  sim.dump_vcd( 'pymtl.tools.simulation.vcd_test.{}.vcd'.format( model.class_name ) )
  return sim

#-----------------------------------------------------------------------
# setup_function
#-----------------------------------------------------------------------
# A special setup function that get the functions parent module, saves
# the setup_sim defined by that module, and replaces it with
# vcd_setup_sim.
def setup_function( function ):
  parent_module           = inspect.getmodule( function )
  function._old_setup     = parent_module.setup_sim
  parent_module.setup_sim = vcd_setup_sim

#-----------------------------------------------------------------------
# teardown_function
#-----------------------------------------------------------------------
# Restore the setup_sim of the module the function is defined in with
# it's original version.
def teardown_function( function ):
  parent_module           = inspect.getmodule( function )
  parent_module.setup_sim = function._old_setup


