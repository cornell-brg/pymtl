#!/usr/bin/env python

import fileinput
import sys
import re
import os

if( __name__ == '__main__' ):

  if( len(sys.argv) < 3 ):
    print 'Usage: v2pymtl.py [model name] [verilog file]'
    sys.exit()

  model_name = sys.argv[1]
  filename_v = sys.argv[2]

  filename_pyx = model_name + '.pyx'
  filename_w = 'W' + model_name + '.py'
  vobj_name = 'V' + model_name

  # Verilate the translated module (warnings suppressed)
  os.system('verilator -cc {0} -top-module {1} -Wno-lint -Wno-UNOPTFLAT'.format(filename_v, model_name))

  # Import the specified module and get its input and output ports
  __import__( model_name )

  imported_module = sys.modules[ model_name ]

  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()
  model_inst.elaborate()

  in_ports = model_inst.get_inports()
  out_ports = model_inst.get_outports()

  in_ports = [ ( p.verilog_name(), str( p.width ) ) for p in in_ports ] 
  out_ports = [ ( p.verilog_name(), str( p.width ) ) for p in out_ports ] 

  # Generate the Cython source code
  f = open(filename_pyx, 'w')

  pyx = '\
#{0}\n\
# cdefs\n\
#{0}\n\
\n\
cdef extern from \"obj_dir/{1}.h\":\n\
  cdef cppclass {1}:\n\
    long long '.format('-'*72, vobj_name)

  for i in (in_ports + out_ports):
    pyx += i[0] + ', '

  pyx = pyx[:-2]
  pyx += '\n\
    void eval()\n\
\n\
cdef {0} *{1} = new {0}()\n\n'.format(vobj_name, model_name)

  for i in in_ports:
    pyx += '\
def set_{0}({0}):\n\
  global {1}\n\
  {1}.{0} = {0}\n\n'.format(i[0], model_name)

  for i in out_ports:
    pyx += '\
def get_{0}():\n\
  global {1}\n\
  return {1}.{0}\n\n'.format(i[0], model_name)

  pyx += '\
def eval():\n\
  global {0}\n\
  {0}.eval()\n'.format(model_name)

  f.write(pyx)

  f.close()

  # Generate setup.py
  f = open('setup.py', 'w')

  f.write('\
from distutils.core import setup\n\
from distutils.extension import Extension\n\
from Cython.Distutils import build_ext\n\
\n\
setup(\n\
  ext_modules = [ Extension( \"{0}\", sources=[\"{1}\", \"obj_dir/{0}.cpp\", \"obj_dir/{0}__Syms.cpp\", \"obj_dir/verilated.cpp\"], language=\"c++\" ) ],\n\
  cmdclass = {2}\"build_ext\": build_ext{3}\n\
)\n'.format(vobj_name, filename_pyx, '{', '}'))

  f.close()

  # Cythonize the verilated module
  os.system('python setup.py build_ext -i -f')

  # Generate the PyMTL wrapper to wrap the cythonized module
  f = open(filename_w, 'w')

  w = '\
#{0}\n\
# {1}\n\
#{0}\n\
\n\
import {2}\n\
from pymtl import *\n\
\n\
class {1} (Model):\n\
\n\
  def __init__(s):\n\
\n\
    # Ports\n'.format('-'*72, model_name, vobj_name)

  for i in in_ports:
    w += '    s.' + i[0] + ' = InPort(' + i[1] + ')\n'

  for i in out_ports:
    w += '    s.' + i[0] + ' = OutPort(' + i[1] + ')\n'

  w += '\n\
  @combinational\n\
  def logic(s):\n\n'

  for i in in_ports:
    if( i[0] != 'clk' ):
      w += '    {0}.set_{1}(s.{1}.value.int)\n'.format(vobj_name, i[0])

  w += '\n    {0}.eval()\n\n'.format(vobj_name)

  for i in out_ports:
    w += '    s.{0}.value = {1}.get_{0}()\n'.format(i[0], vobj_name)

  w += '\n\
  @posedge_clk\n\
  def tick(s):\n\
\n\
    {0}.eval()\n\n\
    {0}.set_clk(1)\n\n\
    {0}.eval()\n\n'.format(vobj_name)

  for i in out_ports:
    w += '    s.{0}.next = {1}.get_{0}()\n'.format(i[0], vobj_name)

  w += '    {0}.set_clk(0)'.format(vobj_name)

  f.write(w)
  f.close()
