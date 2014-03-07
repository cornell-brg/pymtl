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

  # Write the output to a temporary file
  fd = open( temp_file, 'w+' )
  verilog.translate( model_inst, fd )
  fd.close()

  # Check if the temporary file matches an existing file (caching)
  cached = False
  if os.path.exists( verilog_file ):
    cached = filecmp.cmp( temp_file, verilog_file )
    if not cached:
      os.system( ' diff %s %s'%( temp_file, verilog_file ))

  # Rename temp to actual output
  os.rename( temp_file, verilog_file )

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
