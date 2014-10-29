#=======================================================================
# cpp_sim.py
#=======================================================================

from cpp         import CLogicTransl as translate
from cpp         import compiler
from cpp_helpers import gen_cppsim, create_cpp_py_wrapper
from subprocess  import check_output, STDOUT, CalledProcessError

import os
import sys
import filecmp

#-----------------------------------------------------------------------
# get_cpp
#-----------------------------------------------------------------------
def get_cpp( model_inst ):

  model_inst.elaborate()

  # Translate the PyMTL module to cpp, if we've already done
  # translation check if there's been any changes to the source
  model_name   = model_inst.class_name
  source_file  = model_name + '.cpp'
  temp_file    = model_name + '.cpp.tmp'
  wrapper_file = model_name + '_cpp.py'
  lib_file     = 'lib{}_cpp.so'.format( model_name )

  # Write the output to a temporary file
  cdef = None
  with open( temp_file, 'w+' ) as fd:
    cdef, _ = translate( model_inst, fd )

  def do_work():
    cmd  = compiler.format( libname = lib_file,
                            csource = source_file )
    try:
      result = check_output( cmd.split() , stderr=STDOUT )
    except CalledProcessError as e:
      raise Exception( 'Module did not compile!\n\n'
                       'Command:\n' + ' '.join(e.cmd) + '\n\n'
                       'Error:\n' + e.output + '\n'
                      )
    #csim, ffi = gen_cppsim ( lib_file, cdef )
    #sim       = CSimWrapper( csim, ffi )
    create_cpp_py_wrapper( model_inst, cdef, lib_file, wrapper_file )

  # Check if the temporary file matches an existing file (caching)
  cached = False
  # TODO: fix caching
  #if os.path.exists( source_file ):
  #  cached = filecmp.cmp( temp_file, source_file )
  #  if not cached:
  #    os.system( ' diff -y %s %s'%( temp_file, source_file ))

  # Rename temp to actual output
  os.rename( temp_file, source_file )

  # Compile the module only if we've updated the verilog source
  if not cached:
    print "NOT CACHED", source_file
    # verilog_to_pymtl( model_inst, source_file )
    do_work()

  # Use some trickery to import the verilated version of the model
  sys.path.append( os.getcwd() )
  __import__( wrapper_file[:-3] )
  imported_module = sys.modules[ wrapper_file[:-3] ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()

  return model_inst

