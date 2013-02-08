from translate import VerilogTranslationTool
import v2pymtl

import os
import filecmp

# TODO: figure out a way to replace module instantiation with dummy
#       model that performs translate/verilation with provided
#       parameters and then return the Wrapped/Verilated instance

def translate_class( model_class, config=None ):
  # TODO: currently assumes construct doesn't need any arguments
  #       need to change it to take configuration parameters
  model_inst = model_class()
  model_inst.elaborate()
  verilog_file = model_inst.class_name + '.v'
  VerilogTranslationTool( model_inst, verilog_file )

def get_verilated( model_inst ):

  model_inst.elaborate()
  model_name = model_inst.class_name

  # Translate the PyMTL module to Verilog, if we've already done
  # translation check if there's been any changes to the source
  verilog_file = model_name + '.v'
  temp_file    = verilog_file + '.tmp'
  if os.path.exists( verilog_file ):
    VerilogTranslationTool( model_inst, temp_file )
    cached = filecmp.cmp( temp_file, verilog_file )
    if not cached:
      os.system( ' diff %s %s'%( temp_file, verilog_file ))
    os.rename( temp_file, verilog_file )
  else:
    VerilogTranslationTool( model_inst, verilog_file )
    cached = False

  # Verilate the module only if we've updated the verilog source
  if not cached:
    print "NOT CACHED", verilog_file
    v2pymtl.v2pymtl.verilog_to_pymtl( model_inst, verilog_file )

  # Use some trickery to import the verilated version of the model
  import sys
  sys.path.append('../build')
  __import__( 'W' + model_name )
  imported_module = sys.modules[ 'W'+model_name ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()
  model_inst.elaborate()

  return model_inst

def verilate( model_class, src_file, config=None ):
  # Translate the model to Verilog
  translate_class( model_class )
  # Verilate the generated Verilog into Python wrapped C++
  v2pymtl.v2pymtl.verilog_to_pymtl( model_class, src_file )
