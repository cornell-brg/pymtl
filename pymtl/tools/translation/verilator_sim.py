#=======================================================================
# verilator_sim.py
#=======================================================================

from __future__ import print_function

import os
import sys
import filecmp
import verilog

from os.path        import exists
from verilator_cffi import verilog_to_pymtl

#-----------------------------------------------------------------------
# TranslationTool
#-----------------------------------------------------------------------
def TranslationTool( model_inst, lint=False, enable_blackbox=False, verilator_xinit="zeros" ):
  """Translates a PyMTL model into Python-wrapped Verilog.

  model_inst:      an un-elaborated Model instance
  lint:            run verilator linter, warnings are fatal
                   (disables -Wno-lint flag)
  enable_blackbox: also generate a .v file with black boxes
  """

  model_inst.elaborate()

  # Translate the PyMTL module to Verilog, if we've already done
  # translation check if there's been any changes to the source
  model_name      = model_inst.class_name
  verilog_file    = model_name + '.v'
  temp_file       = model_name + '.v.tmp'
  c_wrapper_file  = model_name + '_v.cpp'
  py_wrapper_file = model_name + '_v.py'
  lib_file        = 'lib{}_v.so'.format( model_name )
  obj_dir         = 'obj_dir_' + model_name
  blackbox_file   = model_name + '_blackbox' + '.v'

  vcd_en   = True
  vcd_file = ''
  try:
    vcd_en   = ( model_inst.vcd_file != '' )
    vcd_file = model_inst.vcd_file
  except AttributeError:
    vcd_en = False

  # Write the output to a temporary file
  with open( temp_file, 'w+' ) as fd:
    verilog.translate( model_inst, fd, verilator_xinit=verilator_xinit )

  # write Verilog with black boxes
  if enable_blackbox:
    with open( blackbox_file, 'w+' ) as fd:
      verilog.translate( model_inst, fd, enable_blackbox=True, verilator_xinit=verilator_xinit )

  # Check if the temporary file matches an existing file (caching)

  cached = False
  if (     exists(verilog_file)
       and exists(py_wrapper_file)
       and exists(lib_file)
       and exists(obj_dir) ):

    cached = filecmp.cmp( temp_file, verilog_file )

    # if not cached:
    #   os.system( ' diff %s %s'%( temp_file, verilog_file ))

  # Rename temp to actual output
  os.rename( temp_file, verilog_file )

  # Verilate the module only if we've updated the verilog source
  if not cached:
    #print( "NOT CACHED", verilog_file )
    verilog_to_pymtl( model_inst, verilog_file, c_wrapper_file,
                      lib_file, py_wrapper_file, vcd_en, lint,
                      verilator_xinit )
  #else:
  #  print( "CACHED", verilog_file )

  # Use some trickery to import the verilated version of the model
  sys.path.append( os.getcwd() )
  __import__( py_wrapper_file[:-3] )
  imported_module = sys.modules[ py_wrapper_file[:-3] ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst  = model_class()

  if vcd_en:
    model_inst.vcd_file = vcd_file

  return model_inst
