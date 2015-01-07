#!/usr/bin/env python
#=======================================================================
# verilator_cython.py
#=======================================================================

from __future__ import print_function

import fileinput
import sys
import re
import os
import math

import verilog_structural

#-----------------------------------------------------------------------
# verilog_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for Verilog HDL.
def verilog_to_pymtl( model, filename_v ):

  # TODO: clean this up
  if   isinstance( model, str ):
    model_name = model
  elif isinstance( model, type ):
    x = model()
    model_name = x.__class__.__name__
  else:
    model_name = model.class_name

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
  create_setup( filename_pyx, vobj_name, model_name )

  # Cythonize the model
  cythonize_model( model_name )

  # Create PyMTL wrapper for Cynthonized module
  create_pymtl_wrapper( in_ports, out_ports, model_name,
                        filename_w, vobj_name, xobj_name )

#-----------------------------------------------------------------------
# verilate_model
#-----------------------------------------------------------------------
# Convert Verilog HDL into a C++ simulator using Verilator.
# http://www.veripool.org/wiki/verilator
def verilate_model( filename, model_name ):
  # Verilate the translated module (warnings suppressed)
  cmd = 'rm -r obj_dir_{1}; {2}/bin/verilator -cc {0} -top-module {1}' \
        ' --Mdir obj_dir_{1} -trace -Wno-lint -Wno-UNOPTFLAT'   \
        .format( filename, model_name, os.environ['VERILATOR_ROOT'] )
  print( cmd )
  os.system( cmd )

#-----------------------------------------------------------------------
# get_model_ports
#-----------------------------------------------------------------------
# Return all input and output ports of a PyMTL model.
def get_model_ports( model_name ):
  # TODO: clean this up, this is getting really messy...
  # Import the specified module
  # If we received a module name from the commandline, we need to import
  if isinstance( model_name, str ):
    __import__( model_name )
    imported_module = sys.modules[ model_name ]
    model_class = imported_module.__dict__[ model_name ]
    model_inst = model_class()
    model_inst.elaborate()
  # We received a model class definition (not an instance!)
  elif isinstance( model_name, type ):
    model_class = model_name
    model_inst = model_class()
    model_inst.elaborate()
  # Otherwise we received a model instance!
  else:
    model_inst = model_name

  # Collect the input/output ports
  in_ports  = model_inst.get_inports()
  out_ports = model_inst.get_outports()

  def verilog_name( port ):
    return verilog_structural.mangle_name( port.name )

  in_ports = [ ( verilog_name( p ), str( p.nbits ) )
               for p in in_ports
               if not verilog_name( p ) in [ 'clk', 'reset' ] ]
  out_ports = [ ( verilog_name( p ), str( p.nbits ) ) for p in out_ports ]

  return in_ports, out_ports

#-----------------------------------------------------------------------
# create_cython
#-----------------------------------------------------------------------
# Generate a Cython wrapper file for Verilated C++.
def create_cython( in_ports, out_ports, model_name,
                   filename_pyx, vobj_name ):
  # Generate the Cython source code
  f = open( filename_pyx, 'w' )

  pyx = ("from pymtl import *\n\n"
         "cdef extern from 'verilated_vcd_c.h':\n"
         "  cdef cppclass VerilatedVcdC:\n"
         "    void open( char* )\n"
         "    void dump( int )\n"
         "    void close()\n\n"
         "cdef extern from 'obj_dir_{1}/{0}.h':\n"
         "  cdef cppclass {0}:\n".format( vobj_name, model_name ))

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

  pyx += '    void eval()\n    void trace( VerilatedVcdC*, int )\n\n'

  pyx += "cdef extern from 'verilated.h' namespace 'Verilated':\n  void traceEverOn( bool )\n\n"
  pyx += "def XTraceEverOn():\n  traceEverOn( 1 )\n\n"

  pyx += ("cdef class X{0}:\n"
          "  cdef {1}* {0}\n"
          "  cdef VerilatedVcdC* tfp\n"
          "  cdef int main_time\n\n"
          "  def __cinit__(self):\n"
          "    self.{0} = new {1}()\n"
          "    self.tfp = new VerilatedVcdC()\n"
          "    self.main_time = 0\n"
          "    self.{0}.trace( self.tfp, 99 )\n"
          "    self.tfp.open( 'vlt_dump.vcd' )\n\n"
          "  def __dealloc__(self):\n"
          "    if self.{0}:\n"
          "      del self.{0}\n"
          "    if self.tfp:\n"
          "      self.tfp.close()\n"
          "      del self.tfp\n\n".format( model_name, vobj_name ))

  pyx += ("  def dump(self):\n"
          "      self.main_time = self.main_time + 1\n"
          "      self.tfp.dump( self.main_time )\n\n")

  pyx += ("  property the_time:\n"
          "    def __set__(self, time):\n"
          "      self.main_time = time\n"
          "    def __get__(self):\n"
          "      return self.main_time\n\n".format( model_name ))

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
      pyx += ("      self.{0}.{1} = {1}.value.uint()\n"
              "\n".format( model_name, signal_name ))
    else:
      word_aligned = bitwidth/32
      for j in range( word_aligned ):
        pyx += ("      self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint()"
                "\n".format( model_name, signal_name, j, 32*j, 32*(j+1) ))
      if bitwidth % 32 != 0:
        idx = word_aligned
        start = word_aligned*32
        end = bitwidth
        pyx += ("      self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint()"
                "\n".format( model_name, signal_name, idx, start, end ))

      pyx += '\n'

  for signal_name, bitwidth in out_ports:
    pyx += ("  property {0}:\n"
            "    def __get__(self):\n"
            "      return self.{1}.{0}\n\n".format( signal_name, model_name ))

#  pyx += ("  def eval(self):\n"
#          "    self.{}.eval()\n"
#          "    self.tfp.dump( self.main_time )\n"
#          "    self.main_time = self.main_time + 1".format( model_name ))

  pyx += ("  def eval(self):\n"
          "    self.{}.eval()\n".format( model_name ))

  f.write( pyx )
  f.close()

#-----------------------------------------------------------------------
# create_setup
#-----------------------------------------------------------------------
# Create a setup.py file to compile the Cython Verilator wrapper.
def create_setup( filename_pyx, vobj_name, model_name ):
  # Generate setup.py
  verilator_include = '{}/include'.format( os.environ['VERILATOR_ROOT'] )
  dir_  = 'obj_dir_{0}'.format( model_name )
  file_ = '"{0}/{{}}",'.format( dir_ )
  sources = [ file_.format(x) for x in os.listdir(dir_) if '.cpp' in x ]
  sources = ' '.join(sources)

  f = open( 'setup_{0}.py'.format( model_name ), 'w' )

  f.write( "from distutils.core import setup\n"
           "from distutils.extension import Extension\n"
           "from Cython.Distutils import build_ext\n"
           "\n"
           "setup(\n"
           "  ext_modules = [ Extension( '{0}',\n"
           "                             sources=['{1}',\n"
           "                             {5}\n"
           "                             '{4}/verilated.cpp', '{4}/verilated_vcd_c.cpp'],\n"
           "                             include_dirs=['{4}'],\n"
           "                             language='c++' ) ],\n"
           "  cmdclass = {2}'build_ext': build_ext{3}\n"
           ")\n".format( vobj_name, filename_pyx, '{', '}', verilator_include, sources ) )

  #raise Exception()

  f.close()

#-----------------------------------------------------------------------
# cythonize_model
#-----------------------------------------------------------------------
# Create a Python interface to the Verilated C++ using Cython.
def cythonize_model( model_name ):
  # Cythonize the verilated module
  os.system( 'python setup_{0}.py build_ext -i -f'.format( model_name ) )

#-----------------------------------------------------------------------
# create_pymtl_wrapper
#-----------------------------------------------------------------------
# Create PyMTL wrapper for Cythonized and Verilated Verilog source.
def create_pymtl_wrapper( in_ports, out_ports, model_name, filename_w,
                          vobj_name, xobj_name ):

  f = open( filename_w, 'w' )

  # Create module imports and the declaration for the PyMTL wrapper.
  w = ("from {0} import {1}\n"
       "from {0} import XTraceEverOn\n"
       "from pymtl import *\n\n"
       "class {2}(Model):\n\n"
       "  def __init__(self):\n\n"
       "    self.{1} = {1}()\n"
       "\n".format( vobj_name, xobj_name, model_name ))

  # Any signals with an _M_ in the name are part of bundles, handle these
  # specially by creating 'fake' PortBundle inner classes.
  from collections import defaultdict
  bundles = set()
  for name, width in in_ports + out_ports:
    if '_M_' in name:
      bundle_name, port_name = name.split('_M_')
      bundles.add( bundle_name )
  for b in bundles:
    w += ("    class {1}( PortBundle ): flip = False\n"
          "    self.{0} = {1}()\n\n".format( b, b.capitalize() ) )


  # Create the interface ports for the wrapper class.
  for port, ptype in [ ( in_ports, 'InPort' ), ( out_ports, 'OutPort' ) ]:

    port = [ ( i[0].replace('_M_', '.'), i[1] ) for i in port ]

    k = [ ( re.sub('IDX.*', 'IDX', i[0]), i[1] ) for i in port ]
    l = [ (re.sub('IDX', '', i[0]), i[1], k.count(i)) for i in set(k)
          if (k.count(i) > 1 or 'IDX' in i[0]) ]
    k = [ i for i in k if (not k.count(i) > 1 and not 'IDX' in i[0])]

    for i in l:
      w += ('    self.{0} = [ {3}( {1} ) for x in range( {2} ) ]'
            '\n'.format( i[0], i[1], i[2], ptype ))

    for i in k:
      w += '    self.{0} = {2}( {1} )\n'.format( i[0], i[1], ptype )

  # Register the sensitivity list.
  # Must be done explicitly since we dont access .value!
  #w += "\n    self.register_combinational( 'logic', [\n"
  #for name, bitwidth in in_ports:
  #  name = name.replace('_M_', '.')
  #  if 'IDX' in name:
  #    prefix, idx = name.split('IDX')
  #    name = '{}[{}]'.format( prefix, idx )
  #  w += "                                 self.{},\n".format(name)
  #w += "                               ])\n\n"

  w += ("\n  def elaborate_logic( self ):"
        "\n    @self.combinational"
        "\n    def logic():")

  w += ('\n      self.{0}.reset = self.reset.value.uint()'
        .format( xobj_name ))

  for i in in_ports:
    temp = i[0].replace('_M_', '.')
    if 'IDX' in i[0]:
      w += ('\n      self.{0}.{1} = self.{2}]'
            .format( xobj_name, i[0], re.sub('IDX', '[', temp) ))
    else:
      w += ('\n      self.{0}.{1} = self.{2}'
            .format( xobj_name, i[0], temp ))

  w += '\n      self.{0}.eval()'.format( xobj_name )

  for i in out_ports:
    temp = i[0].replace('_M_', '.')
    if 'IDX' in i[0]:
      w += ('\n      self.{0}].value = self.{1}.{2}'
            .format( re.sub('IDX', '[', temp), xobj_name, i[0] ))
    else:
      w += ('\n      self.{0}.value = self.{1}.{2}'
            .format( temp, xobj_name, i[0] ))

  w += ("\n"
        "\n    @self.posedge_clk"
        "\n    def tick():"
        "\n      self.{0}.eval()"
        #"\n      self.{0}.dump()" # TODO: not sure what dump is for...
        "\n      self.{0}.clk = 1"
        "\n      self.{0}.eval()"
        #"\n      self.{0}.dump()"
        .format( xobj_name ))

  for i in out_ports:
    temp = i[0].replace('_M_', '.')
    if 'IDX' in i[0]:
      w += ('\n      self.{0}].next = self.{1}.{2}'
            .format( re.sub('IDX', '[', temp), xobj_name, i[0] ))
    else:
      w += ('\n      self.{0}.next = self.{1}.{2}'
            .format( temp, xobj_name, i[0] ))

  w += '\n      self.{0}.clk = 0\n\n'.format( xobj_name )

  w += 'XTraceEverOn()'

  f.write( w )
  f.close()


#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------

if __name__ == '__main__':

  if len( sys.argv ) < 3:
    print( 'Usage: v2pymtl.py [model name] [verilog file]' )
    sys.exit()

  model_name = sys.argv[1]
  filename_v = sys.argv[2]

  verilog_to_pymtl( model_name, filename_v )

