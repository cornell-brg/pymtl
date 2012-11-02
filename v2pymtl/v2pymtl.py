#!/usr/bin/env python

import fileinput
import sys
import re
import os
import math

if __name__ == '__main__':

  if len(sys.argv) < 3:
    print 'Usage: v2pymtl.py [model name] [verilog file]'
    sys.exit()

  model_name = sys.argv[1]
  filename_v = sys.argv[2]

  filename_pyx = model_name + '.pyx'
  filename_w = 'W' + model_name + '.py'
  vobj_name = 'V' + model_name
  xobj_name = 'X' + model_name

  ds = 2*' '
  qs = 2*ds
  hs = 3*ds

  # Verilate the translated module (warnings suppressed)
  os.system( 'verilator -cc {0} -top-module {1} -Wno-lint -Wno-UNOPTFLAT'.format( filename_v, model_name ) )

  # Import the specified module and get its input and output ports
  __import__( model_name )

  imported_module = sys.modules[ model_name ]

  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()
  model_inst.elaborate()

  in_ports = model_inst.get_inports()
  out_ports = model_inst.get_outports()

  in_ports = [ ( p.verilog_name(), str( p.width ) ) for p in in_ports if not p.verilog_name() in [ 'clk', 'reset' ] ] 
  out_ports = [ ( p.verilog_name(), str( p.width ) ) for p in out_ports ] 

  # Generate the Cython source code
  f = open(filename_pyx, 'w')

  pyx = 'from pymtl import *\n\ncdef extern from \"obj_dir/{0}.h\":\n  cdef cppclass {0}:\n'.format( vobj_name )

  for i in ( [ ('clk', '1') ] + in_ports + out_ports ):
    s = int( i[1] )

    pyx += qs

    if s <= 8:
      pyx += 'char '
    elif s <= 16:
      pyx += 'unsigned short '
    elif s <= 32:
      pyx += 'unsigned long '
    elif s <= 64:
      pyx += 'long long '
    else:
      pyx += 'unsigned long '

    pyx += i[0]

    if s <= 64:
      pyx += '\n'
    else:
      pyx += '[{0}]\n'.format( int ( math.ceil( s / 32.0 ) ) )

  pyx += '\n{0}void eval()\n\n'.format( qs )

  pyx += 'cdef class X{0}:\n\
  cdef {1}* {0}\n\n\
  def __cinit__(self):\n{2}self.{0} = new {1}()\n\n\
  def __dealloc__(self):\n{2}if self.{0}:\n{3}del self.{0}\n\n'.format( model_name, vobj_name, qs, hs )

  pyx += '{0}def set_clk(self, clk):\n{1}self.{2}.clk = clk\n\n'.format( ds, qs, model_name )

  for i in in_ports:
    pyx += ds + 'def set_{0}(self, {0}):\n'.format( i[0], model_name )
    s = int( i[1] )

    if s <= 64:
      pyx += qs + 'self.{0}.{1} = {1}.value.uint\n\n'.format( model_name, i[0] )
    else:
      word_aligned = s/32
      for j in range( word_aligned ):
        pyx += qs + 'self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint\n'.format( model_name, i[0], j, 32*j, 32*(j+1) )
      if s % 32 != 0:
        idx = word_aligned
        start = word_aligned*32
        end = s
        pyx += qs + 'self.{0}.{1}[{2}] = {1}.value[{3}:{4}].uint\n'.format( model_name, i[0], idx, start, end )

      pyx += '\n'

  for i in out_ports:
    pyx += ds + 'def get_{0}(self):\n{2}return self.{1}.{0}\n\n'.format( i[0], model_name, qs )

  pyx += ds + 'def eval(self):\n{0}self.{1}.eval()\n'.format( qs, model_name )

  f.write(pyx)

  f.close()

  # Generate setup.py
  f = open('setup.py', 'w')

  f.write( '\
from distutils.core import setup\n\
from distutils.extension import Extension\n\
from Cython.Distutils import build_ext\n\
\n\
setup(\n\
  ext_modules = [ Extension( \"{0}\", sources=[\"{1}\", \"obj_dir/{0}.cpp\", \"obj_dir/{0}__Syms.cpp\", \"obj_dir/verilated.cpp\"], language=\"c++\" ) ],\n\
  cmdclass = {2}\"build_ext\": build_ext{3}\n\
)\n'.format( vobj_name, filename_pyx, '{', '}' ) )

  f.close()

  # Cythonize the verilated module
  os.system('python setup.py build_ext -i -f')

  # Generate the PyMTL wrapper to wrap the cythonized module
  f = open(filename_w, 'w')

  w = 'from {0} import X{1}\nfrom pymtl import *\n\nclass {1} (Model):\n\n{2}def __init__(self):\n\n'.format( vobj_name, model_name, ds )
  w += '{0}self.{1} = {1}()\n\n'.format( qs, xobj_name )

  for p in [ ( in_ports, 'In' ), ( out_ports, 'Out' ) ]:

    k = [ ( re.sub('IDX.*', '', i[0]), i[1] ) for i in p[0] ]
    l = [ (i[0], i[1], k.count(i)) for i in set(k) if k.count(i) > 1 ]
    k = [ i for i in k if not k.count(i) > 1 ]

    for i in l:
      w += '{0}self.{1} = [ {4}Port( {2} ) for x in range( {3} ) ]\n'.format( qs, i[0], i[1], i[2], p[1] )

    for i in k:
      w += '{0}self.{1} = {3}Port( {2} )\n'.format( qs, i[0], i[1], p[1] )

  w += '\n  @combinational\n  def logic(self):\n\n'

  for i in in_ports:
    if 'IDX' in i[0]:
      w += '{0}self.{1}.set_{2}(self.{3}])\n'.format( qs, xobj_name, i[0], re.sub('IDX', '[', i[0]) )
    else:
      w += '{0}self.{1}.set_{2}(self.{2})\n'.format( qs, xobj_name, i[0] )

  w += '\n{0}self.{1}.eval()\n\n'.format( qs, xobj_name )

  for i in out_ports:
    if 'IDX' in i[0]:
      w += '{0}self.{1}].value = self.{2}.get_{3}()\n'.format( qs, re.sub('IDX', '[', i[0]), xobj_name, i[0] )
    else:
      w += '{0}self.{1}.value = self.{2}.get_{1}()\n'.format( qs, i[0], xobj_name )

  w += '\n{0}@posedge_clk\n{0}def tick(self):\n\n{1}self.{2}.eval()\n\n{1}self.{2}.set_clk(1)\n\n{1}self.{2}.eval()\n\n'.format( ds, qs, xobj_name )

  for i in out_ports:
    if 'IDX' in i[0]:
      w += '{0}self.{1}].next = self.{2}.get_{3}()\n'.format( qs, re.sub('IDX', '[', i[0]), xobj_name, i[0] )
    else:
      w += '{0}self.{1}.next = self.{2}.get_{1}()\n'.format( qs, i[0], xobj_name )

  w += '\n{0}self.{1}.set_clk(0)'.format( qs, xobj_name )

  f.write(w)
  f.close()
