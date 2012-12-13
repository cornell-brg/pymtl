#!/usr/bin/env python
#=========================================================================
# Verilate and Cythonize Translated PyMTL Models
#=========================================================================

import fileinput
import sys
import re
import os
import math


#-------------------------------------------------------------------------
# Verilate Translated PyMTL Model
#-------------------------------------------------------------------------

def verilate_model( filename, model_name ):
  # Verilate the translated module (warnings suppressed)
  os.system( 'verilator -cc {0} -top-module {1} -Wno-lint '
             '-Wno-UNOPTFLAT'.format( filename, model_name ) )

#-------------------------------------------------------------------------
# Cythonize Verilated Model
#-------------------------------------------------------------------------

def cythonize_model():
  # Cythonize the verilated module
  os.system( 'python setup.py build_ext -i -f' )

#-------------------------------------------------------------------------
# Get PyMTL Model Ports
#-------------------------------------------------------------------------

def get_model_ports( model_name ):
  # Import the specified module
  # If we received a module name from the commandline, we need to import
  if isinstance( model_name, str ):
    __import__( model_name )
    imported_module = sys.modules[ model_name ]
    model_class = imported_module.__dict__[ model_name ]
    model_name = model
  # Otherwise we received a model class definition (not an instance!)
  else:
    model_class = model_name

  model_inst = model_class()
  model_inst.elaborate()

  # Collect the input/output ports
  in_ports = model_inst.get_inports()
  out_ports = model_inst.get_outports()

  in_ports = [ ( p.verilog_name(), str( p.width ) )
               for p in in_ports
               if not p.verilog_name() in [ 'clk', 'reset' ] ]
  out_ports = [ ( p.verilog_name(), str( p.width ) ) for p in out_ports ]

  return in_ports, out_ports

#-------------------------------------------------------------------------
# Create Cython File
#-------------------------------------------------------------------------

def create_cython( in_ports, out_ports, model_name,
                   filename_pyx, vobj_name ):
  # Generate the Cython source code
  f = open( filename_pyx, 'w' )

  pyx = ("from pymtl import *\n\n"
         "cdef extern from 'obj_dir/{0}.h':\n"
         "  cdef cppclass {0}:\n".format( vobj_name ))

  ports = [ ('clk', '1'), ('reset', '1') ] + in_ports + out_ports
  for signal_name, bitwidth in ports:
    # TODO: change bitwidth to not be turned into a string above...
    bitwidth = int( bitwidth )

    pyx += '    '

    if   bitwidth <= 8:  pyx += 'char '
    elif bitwidth <= 16: pyx += 'unsigned short '
    elif bitwidth <= 32: pyx += 'unsigned long '
    elif bitwidth <= 64: pyx += 'long long '
    else:                pyx += 'unsigned long '

    pyx += signal_name

    if bitwidth <= 64:
      pyx += '\n'
    else:
      pyx += '[{0}]\n'.format( int ( math.ceil( bitwidth / 32.0 ) ) )

  pyx += '    void eval()\n\n'

  pyx += ("cdef class X{0}:\n"
          "  cdef {1}* {0}\n\n"
          "  def __cinit__(self):\n"
          "    self.{0} = new {1}()\n\n"
          "  def __dealloc__(self):\n"
          "    if self.{0}:\n"
          "      del self.{0}\n\n".format( model_name, vobj_name ))

  pyx += ("  property clk:\n"
          "    def __set__(self, clk):\n"
          "      self.{}.clk = clk\n\n".format( model_name ))

  pyx += ("  property reset:\n"
          "    def __set__(self, reset):\n"
          "      self.{}.reset = reset\n\n".format( model_name ))

  for signal_name, bitwidth in in_ports:
    pyx += ("  property {0}:\n"
            "    def __set__(self, {0}):\n".format( signal_name ))
    bitwidth = int( bitwidth )

    if bitwidth <= 64:
      pyx += ("      self.{0}.{1} = {1}.value.uint\n"
              "\n".format( model_name, signal_name ))
    else:
      word_aligned = bitwidth/32
      for j in range( word_aligned ):
        pyx += ("      self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint"
                "\n".format( model_name, signal_name, j, 32*j, 32*(j+1) ))
      if bitwidth % 32 != 0:
        idx = word_aligned
        start = word_aligned*32
        end = bitwidth
        pyx += ("      self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint"
                "\n".format( model_name, signal_name, idx, start, end ))

      pyx += '\n'

  for signal_name, bitwidth in out_ports:
    pyx += ("  property {0}:\n"
            "    def __get__(self):\n"
            "      return self.{1}.{0}\n\n".format( signal_name, model_name ))

  pyx += ("  def eval(self):\n"
          "    self.{}.eval()\n".format( model_name ))

  f.write( pyx )
  f.close()

#-------------------------------------------------------------------------
# Create Setup File
#-------------------------------------------------------------------------

def create_setup( filename_pyx, vobj_name ):
  # Generate setup.py
  f = open( 'setup.py', 'w' )

  f.write( "from distutils.core import setup\n"
           "from distutils.extension import Extension\n"
           "from Cython.Distutils import build_ext\n"
           "\n"
           "setup(\n"
           "  ext_modules = [ Extension( '{0}',\n"
           "                             sources=['{1}',\n"
           "                             'obj_dir/{0}.cpp',\n"
           "                             'obj_dir/{0}__Syms.cpp',\n"
           "                             '../v2pymtl/obj_dir/verilated.cpp'],\n"
           "                             include_dirs=['../v2pymtl/obj_dir'],\n"
           "                             language='c++' ) ],\n"
           "  cmdclass = {2}'build_ext': build_ext{3}\n"
           ")\n".format( vobj_name, filename_pyx, '{', '}' ) )

  f.close()

#-------------------------------------------------------------------------
# Create PyMTL Wrapper for Cythonized Verilog
#-------------------------------------------------------------------------

def create_pymtl_wrapper( in_ports, out_ports, model_name, filename_w,
                          vobj_name, xobj_name ):

  f = open( filename_w, 'w' )

  w = ("from {0} import {1}\n"
       "from pymtl import *\n\n"
       "class {2}(Model):\n\n"
       "  def __init__(self):\n\n"
       "    self.{1} = {1}()\n"
       "\n".format( vobj_name, xobj_name, model_name ))

  for port, ptype in [ ( in_ports, 'InPort' ), ( out_ports, 'OutPort' ) ]:

    k = [ ( re.sub('IDX.*', '', i[0]), i[1] ) for i in port ]
    l = [ (i[0], i[1], k.count(i)) for i in set(k) if k.count(i) > 1 ]
    k = [ i for i in k if not k.count(i) > 1 ]

    for i in l:
      w += ('    self.{0} = [ {3}( {1} ) for x in range( {2} ) ]'
            '\n'.format( i[0], i[1], i[2], ptype ))

    for i in k:
      w += '    self.{0} = {2}( {1} )\n'.format( i[0], i[1], ptype )

  # Register the sensitivity list.
  # Must be done explicitly since we dont access .value!
  w += "\n    self.register_combinational( 'logic', [\n"
  for name, bitwidth in in_ports:
    if 'IDX' in name:
      prefix, idx = name.split('IDX')
      name = '{}[{}]'.format( prefix, idx )
    w += "                                 self.{},\n".format(name)
  w += "                               ])\n\n"

  #w += ("\n  @combinational"
  w += ("\n  def logic(self):\n\n")

  w += ('    self.{0}.reset = self.reset.value.uint\n'
        '\n'.format( xobj_name ))

  for i in in_ports:
    if 'IDX' in i[0]:
      w += ('    self.{0}.{1} = self.{2}]'
            '\n'.format( xobj_name, i[0], re.sub('IDX', '[', i[0]) ))
    else:
      w += ('    self.{0}.{1} = self.{1}'
           '\n'.format( xobj_name, i[0] ))

  w += '\n    self.{0}.eval()\n\n'.format( xobj_name )

  for i in out_ports:
    if 'IDX' in i[0]:
      w += ('    self.{0}].value = self.{1}.{2}'
            '\n'.format( re.sub('IDX', '[', i[0]), xobj_name, i[0] ))
    else:
      w += ('    self.{0}.value = self.{1}.{0}'
            '\n'.format( i[0], xobj_name ))

  w += ("\n  @posedge_clk"
        "\n  def tick(self):\n"
        "\n    self.{0}.eval()\n"
        "\n    self.{0}.clk = 1\n"
        "\n    self.{0}.eval()\n\n".format( xobj_name ))

  for i in out_ports:
    if 'IDX' in i[0]:
      w += ('    self.{0}].next = self.{1}.{2}'
            '\n'.format( re.sub('IDX', '[', i[0]), xobj_name, i[0] ))
    else:
      w += ('    self.{0}.next = self.{1}.{0}'
            '\n'.format( i[0], xobj_name ))

  w += '\n    self.{0}.clk = 0'.format( xobj_name )

  f.write( w )
  f.close()

#-------------------------------------------------------------------------
# Create PyMTL Wrapper for Cythonized Verilog
#-------------------------------------------------------------------------

def verilog_to_pymtl( model, filename_v ):

  # TODO: clean this up
  if isinstance( model, str ):
    model_name = model
  else:
    x = model()
    model_name = x.__class__.__name__

  # Output file names
  filename_pyx = model_name + '.pyx'
  filename_w = 'W' + model_name + '.py'
  vobj_name = 'V' + model_name
  xobj_name = 'X' + model_name

  # Verilate the model
  # TODO: clean this up
  verilate_model( filename_v, model_name )

  # Get the ports of the module
  in_ports, out_ports = get_model_ports( model )

  # Create Cython
  create_cython( in_ports, out_ports, model_name,
                 filename_pyx, vobj_name )

  # Create setup.py
  create_setup( filename_pyx, vobj_name )

  # Cythonize the model
  cythonize_model()

  # Create PyMTL wrapper for Cynthonized module
  create_pymtl_wrapper( in_ports, out_ports, model_name,
                        filename_w, vobj_name, xobj_name )

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------

if __name__ == '__main__':

  if len( sys.argv ) < 3:
    print 'Usage: v2pymtl.py [model name] [verilog file]'
    sys.exit()

  model_name = sys.argv[1]
  filename_v = sys.argv[2]

  verilog_to_pymtl( model_name, filename_v )

