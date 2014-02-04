#===============================================================================
# verilator_sim.py
#===============================================================================

#from verilator_cython import verilog_to_pymtl
from verilator_cffi import verilog_to_pymtl

import verilog
import os
import sys
import filecmp

#------------------------------------------------------------------------------
# get_verilated
#------------------------------------------------------------------------------
def get_verilated( model_inst ):

  model_inst.elaborate()
  model_name = model_inst.class_name

  # Translate the PyMTL module to Verilog, if we've already done
  # translation check if there's been any changes to the source
  verilog_file = model_name + '.v'
  temp_file    = verilog_file + '.tmp'

  #verilog.translate( model_inst, open( verilog_file, 'w+' ) )
  #cached = False

  # Caching avoids regeneration/recompilation
  if os.path.exists( verilog_file ):
    verilog.translate( model_inst, open( temp_file, 'w+' ) )
    cached = filecmp.cmp( temp_file, verilog_file )
    if not cached:
      os.system( ' diff %s %s'%( temp_file, verilog_file ))
    os.rename( temp_file, verilog_file )
  else:
    verilog.translate( model_inst, open( verilog_file, 'w+' ) )
    cached = False

  # Verilate the module only if we've updated the verilog source
  if not cached:
    print "NOT CACHED", verilog_file
    verilog_to_pymtl( model_inst, verilog_file )

  # Use some trickery to import the verilated version of the model
  sys.path.append( os.getcwd() )
  __import__( 'W' + model_name )
  imported_module = sys.modules[ 'W'+model_name ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()

  return model_inst
