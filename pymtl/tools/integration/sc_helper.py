import os
import sys
import shutil
from os.path import basename
from subprocess import check_output, STDOUT, CalledProcessError

class SystemCIncludeEnvError( Exception ): pass
class SystemCCompileError( Exception ): pass

#-----------------------------------------------------------------------
# systemc_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for SystemC.

def systemc_to_pymtl( model, c_wrapper_file, lib_file, py_wrapper_file ):
  pass


def compile_object( obj, ext, obj_dir, include ):
  
  # Check if systemc include folder is in the environment
  
  if "SYSTEMC_INCLUDE" not in os.environ:
    raise SystemCIncludeEnvError( '''\n
-   SystemC Include Environment Variable $SYSTEMC_INCLUDE doesn't exist!
    ''')
  
  # Get the full include folder
  include = " ".join( [ "-I. -I ..",
                        "-I" + os.environ["SYSTEMC_INCLUDE"],
                      ] + 
                      [ "-I" + x for x in include ] )
  
  # Name, without the folder prefix
  obj_name = basename( obj )
  
  compile_cmd = ( 'g++ -o {obj_dir}{obj_name}.o '
                  '-fPIC -shared -O1 -fstrict-aliasing '
                  '-Wall -Wno-long-long -Werror '
                  ' {include} -c {obj}{ext} '  ).format( **vars() )
            
  try:
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
    
  except CalledProcessError as e:
    
    # We remove the final "Error: Command Failed" line to make the output
    # more succinct.

    split_output = e.output.splitlines()
    error = '\n-   '.join(split_output[:-1])

    if not split_output[-1].startswith("%Error: Command Failed"):
      error += "\n-   "+split_output[-1]

    error_msg = "\n\n-   {}\n".format(error)

    raise SystemCCompileError( error_msg )

#-----------------------------------------------------------------------
# gen_sc_datatype
#-----------------------------------------------------------------------
# 1   : sc_signal<bool>
# <0  : special case for sc_clock
# <=32: use sc_uint<bitwidth>
# >32 : use sc_biguint<bitwidth>

def gen_sc_datatype(port_width):
  
  sc_type = "sc_signal<bool>" # default 1-bit bool
  if port_width < 0:
    sc_type = "sc_clock" # special case for the clock bit
  if port_width > 1:
    sc_type = "sc_signal< sc_{}uint<{}> >" \
                  .format("big" if port_width > 32 else "", port_width)
  
  return sc_type

#-----------------------------------------------------------------------
# create_c_wrapper_return_cdef
#-----------------------------------------------------------------------
# Create a c_wrapper for given pymtl file which inherits a SystemCModel
# Returns the cffi cdef string for convenience.

def create_c_wrapper_return_cdef(class_name, port_dict):
  
  cdef_templ = '''
typedef struct
{{
  {port_decls}
  
  void *model;
  
}} {class_name}_t;

{method_decls}

{class_name}_t* create();
void destroy({class_name}_t *obj);

void sim_comb();
void sim_cycle();
'''
  cwrapper_templ = '''
#include "systemc.h"
#include "{class_name}.h"

extern "C"
{{

typedef struct
{{
  {port_decls}
  
  void *model;
}} {class_name}_t;

// Since for now we haven't figured out either a way to totally 
// destroy cffi instance, or to reset some static data structure by 
// some idiot systemc developer, we reuse the module.

// Here's why I cannot reset the systemc simulation kernel.
// http://stackoverflow.com/questions/37841872/access-some-static-variable-that-are-defined-in-cpp-while-its-class-type-is-als

// Here's why I cannot reset cffi context.
// http://stackoverflow.com/questions/29567200/cleanly-unload-shared-library-and-start-over-with-python-cffi

static {class_name}_t *obj = NULL;
{method_impls}

{class_name}_t* create()
{{
  if (obj)  return obj;
  {new_stmts}
  
  obj = m;
  return m;
}}
void destroy({class_name}_t *obj)
{{
  // Currently we don't reset, and reuse the module by the reset
  // signal, to let it start over again.
  
  // sc_get_curr_simcontext()->reset();
}}

void sim_comb()
{{
  sc_start(0, SC_NS);
}}
void sim_cycle()
{{
  sc_start(1, SC_NS);
}}

}}
'''
  ind_0 = '\n'
  ind_2 = '\n  '
  
  port_decls   = ""
  method_decls = ""
  method_impls = ""
  
  new_stmts = '''
  {class_name}_t *m     = ({class_name}_t*) malloc(sizeof({class_name}_t));
  {class_name}   *model = new {class_name}("{class_name}");
  m->model = model;
  '''.format(**vars())
  
  delete_stmts = ""
  
  for port_name, port_width in sorted(port_dict.items()):
    
    #...................................................................
    # port_decls: for the c_wrapper struct def
    #...................................................................
    
    port_decls  +=  ind_2 + "void *{};".format(port_name)
    
    #...................................................................
    # new and delete stmts: new and delete the port
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    new_stmts += ind_2 + "{} *{} = new {};" \
                           .format( sc_type, port_name, sc_type )
    new_stmts += ind_2 + "m->{} = {};".format( port_name, port_name )
    new_stmts += ind_2 + "model->{}(*{});".format( port_name, port_name )
    
    delete_stmts += ind_2 + "{} *{} = static_cast<{}*>(obj->{});" \
                              .format( sc_type, port_name, 
                                       sc_type, port_name )
    delete_stmts += ind_2 + "delete {};".format( port_name )
    
    if port_width < 0: continue # the clock only needs the above two.
    
    #...................................................................
    # method_decls: for cffi cdef 
    #...................................................................
    
    if port_width <= 32:
      # rd
      method_decls += ind_0 + "unsigned rd_{}({}_t* obj);" \
                                .format(port_name, class_name)
      # wr
      method_decls += ind_0 + "void     wr_{}({}_t* obj, unsigned x);" \
                                .format(port_name, class_name)
    else:
      # stripmine the read
      for x in xrange(0, port_width, 32):
        lsb, msb = x, min(port_width, x+32)-1
        
        method_decls += ind_0 + "unsigned rd_{}_{}_{}({}_t* obj);" \
                                  .format(port_name, lsb, msb, class_name)
  
      # write a single string
      method_decls += ind_0 + "void     wr_{}({}_t* obj, const char* x);" \
                                .format(port_name, class_name)
    method_decls += "\n"
    
    #...................................................................
    # method_impls: implements cffi cdef methods in c_wrapper
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    if port_width <= 32:
      
      method_impls += '''
unsigned rd_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read(); }}''' \
      .format(port_name, class_name, sc_type, port_name)
      
      method_impls += '''
void wr_{}({}_t* obj, unsigned x)
{{ static_cast<{}*>(obj->{})->write(x); }}
  '''.format(port_name, class_name, sc_type, port_name)
      
    else:
      # stripmine the read
      for x in xrange(0, port_width, 32):
        lsb, msb = x, min(port_width, x+32)-1
        method_impls += '''
unsigned rd_{}_{}_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read().range({},{}).to_uint(); }}''' \
          .format(port_name, lsb, msb, class_name, sc_type, port_name, msb, lsb)
      
      # single write
      method_impls += '''
void wr_{}({}_t* obj, const char* x)
{{ static_cast<{}*>(obj->{})->write({}(x)); }}
'''       .format(port_name, class_name, sc_type, port_name, sc_type)
  
  delete_stmts += '''
  {class_name} *model = static_cast< {class_name}* >(obj->model);
  delete model;
  
  delete obj;
    '''.format(**vars())
  
  with open(class_name+"_wrapper.cpp","w") as output:
    output.write(cwrapper_templ.format(**vars()))
    
  return cdef_templ.format(**vars())

def gen_py_wrapper(class_name):
  
  py_templ = '''
#=======================================================================
# {class_name}_sc.py
#=======================================================================
# This wrapper makes a SystemC model appear as if it
# were a normal PyMTL model.

import os

from pymtl import *
from cffi  import FFI

#-----------------------------------------------------------------------
# {class_name}
#-----------------------------------------------------------------------
class {class_name}( Model ):
  id_ = 0

  def __init__( s ):

    # initialize FFI, define the exposed interface
    s.ffi = FFI()
    s.ffi.cdef({cdef})

    # Import the shared library containing the model. We defer
    # construction to the elaborate_logic function to allow the user to
    # set the vcd_file.

    s._ffi = s.ffi.dlopen('./lib{}_sc.so'.format( class_name ))

    # dummy class to emulate PortBundles
    class BundleProxy( PortBundle ):
      flip = False

    # define the port interface
    {port_defs}

    # increment instance count
    {class_name}.id_ += 1

    # Defer vcd dumping until later
    s.vcd_file = None

    # Buffer for line tracing
    s._line_trace_str = s.ffi.new("char[512]")
    s._convert_string = s.ffi.string

  def __del__( s ):
    s._ffi.destroy( s._m )

  def elaborate_logic( s ):

    # Give verilator_vcd_file a slightly different name so PyMTL .vcd and
    # Verilator .vcd can coexist

    verilator_vcd_file = ""
    if s.vcd_file:
      filen, ext         = os.path.splitext( s.vcd_file )
      verilator_vcd_file = '{{}}.verilator{{}}{{}}'.format(filen, s.id_, ext)

    # Construct the model.

    s._m = s._ffi.create()

    @s.combinational
    def logic():
      
      m = s._m
      
      {set_inputs}

      s._ffi.sim_comb()

      {set_comb}

    @s.posedge_clk
    def tick():

      s._ffi.sim_cycle()
      
      m = s._m
      
      {set_next}

  def line_trace( s ):
    if {sclinetrace}:
      s._ffi.trace( s._m, s._line_trace_str )
      return s._convert_string( s._line_trace_str )
    else:
      return ""
'''

if __name__ == '__main__':
  ports = {
    "xcelreq_msg" : 160,
    "xcelreq_val" : 1,
    "xcelresp_msg": 69,
  }
  
  
  cdef = create_c_wrapper_return_cdef("nullxcel", ports)
  print cdef
  
  
