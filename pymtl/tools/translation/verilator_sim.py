#=======================================================================
# verilator_sim.py
#=======================================================================

from __future__ import print_function

#from verilator_cython import verilog_to_pymtl
from verilator_cffi import verilog_to_pymtl

import verilog
import os
import sys
import filecmp

#-----------------------------------------------------------------------
# TranslationTool
#-----------------------------------------------------------------------
def TranslationTool( model_inst ):

  model_inst.elaborate()

  # Translate the PyMTL module to Verilog, if we've already done
  # translation check if there's been any changes to the source
  model_name      = model_inst.class_name
  verilog_file    = model_name + '.v'
  temp_file       = model_name + '.v.tmp'
  c_wrapper_file  = model_name + '_v.cpp'
  py_wrapper_file = model_name + '_v.py'
  lib_file        = 'lib{}_v.so'.format( model_name )

  try:
    vcd_file      = model_inst.vcd_file
  except AttributeError:
    vcd_file      = ''

  # Write the output to a temporary file
  with open( temp_file, 'w+' ) as fd:
    verilog.translate( model_inst, fd )

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
    print( "NOT CACHED", verilog_file )
    verilog_to_pymtl( model_inst, verilog_file, c_wrapper_file,
                      lib_file, py_wrapper_file, vcd_file )

  # Use some trickery to import the verilated version of the model
  sys.path.append( os.getcwd() )
  __import__( py_wrapper_file[:-3] )
  imported_module = sys.modules[ py_wrapper_file[:-3] ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst  = model_class( vcd_file )

  return model_inst
