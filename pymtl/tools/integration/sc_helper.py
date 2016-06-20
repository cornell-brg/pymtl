#=======================================================================
# sc_helper.py
#=======================================================================

import os
import sys
import shutil
from subprocess import check_output, STDOUT, CalledProcessError

class SystemCIncludeEnvError( Exception ): pass
class SystemCLibraryEnvError( Exception ): pass
class SystemCCompileError( Exception ): pass

#-----------------------------------------------------------------------
# compile_object
#-----------------------------------------------------------------------
# Compile {obj}.{ext} to {obj}.o

def compile_object( obj, ext, include_dirs ):
  
  # Check if systemc include folder is in the environment
  
  if "SYSTEMC_INCLUDE" not in os.environ:
    raise SystemCIncludeEnvError( '''\n
-   SystemC Include Environment Variable $SYSTEMC_INCLUDE doesn't exist!
    ''')
  
  # Get the full include folder
  include = " ".join( [ "-I. -I .." ] +
                      [ "-I" + os.environ["SYSTEMC_INCLUDE"] ] +
                      [ "-I" + x for x in include_dirs ] )
  compile_cmd = ( 'g++ -o {obj}.o '
                  '-fPIC -shared -O1 -fstrict-aliasing '
                  '-Wall -Wno-long-long -Werror '
                  ' {include} -c {obj}{ext} '  ).format( **vars() )
  
  try:
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
  except CalledProcessError as e:
    raise SystemCCompileError( "\n\n-   {}\n".format(e.output) )

#-----------------------------------------------------------------------
# systemc_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for SystemC.

def systemc_to_pymtl( model, obj_dir, include_dirs, sc_module_name, 
                      objs, c_wrapper_file, lib_file, py_wrapper_file ):
    
  port_width_dict = { x: y.nbits if y.name != "clk" else -1 \
                      for x,y in model._port_dict.iteritems() }
  
  cdef = create_c_wrapper( sc_module_name, c_wrapper_file, port_width_dict )  
  
  create_shared_lib( lib_file, c_wrapper_file, objs, include_dirs, obj_dir )
  
  create_py_wrapper( model, py_wrapper_file, cdef )

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
# create_c_wrapper
#-----------------------------------------------------------------------
# Create a c_wrapper for given pymtl file which inherits a SystemCModel
# Returns the cffi cdef string for convenience.

def create_c_wrapper( sc_module_name, c_wrapper_file, port_dict ):
  
  ind_0 = '\n'
  ind_2 = '\n  '
  ind_4 = '\n    '
  ind_6 = '\n      '
  
  cdef_port_decls = ""
  wrap_port_decls = ""
  method_decls    = ""
  method_impls    = ""
  
  new_stmts = '''
  {sc_module_name}_t *m     = ({sc_module_name}_t*) malloc(sizeof({sc_module_name}_t));
  {sc_module_name}   *model = new {sc_module_name}("{sc_module_name}");
  m->model = model;
  '''.format(**vars())
  
  delete_stmts = ""
  
  for port_name, port_width in sorted(port_dict.items()):
    
    #...................................................................
    # port_decls: for the c_wrapper struct def
    #...................................................................
    
    cdef_port_decls += ind_6 + "void *{};".format(port_name)
    wrap_port_decls += ind_2 + "void *{};".format(port_name)
    
    #...................................................................
    # new and delete stmts: new and delete the port
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    new_stmts += ind_2 + "{} *{} = new {};" \
                           .format( sc_type, port_name, sc_type )
    new_stmts += ind_2 + "m->{} = {};".format( port_name, port_name )
    new_stmts += ind_2 + "model->{}(*{});\n".format( port_name, port_name )
    
    delete_stmts += ind_2 + "{} *{} = static_cast<{}*>(obj->{});" \
                              .format( sc_type, port_name, 
                                       sc_type, port_name )
    delete_stmts += ind_2 + "delete {};\n".format( port_name )
    
    if port_width < 0: continue # the clock only needs the above two.
    
    #...................................................................
    # method_decls: for cffi cdef 
    #...................................................................
    
    if port_width <= 32:
      # rd
      method_decls += ind_4 + "unsigned rd_{}({}_t* obj);" \
                                .format( port_name, sc_module_name )
      # wr
      method_decls += ind_4 + "void     wr_{}({}_t* obj, unsigned x);" \
                                .format( port_name, sc_module_name )
    else:
      # stripmine the read
      for x in xrange(0, port_width, 32):
        lsb, msb = x, min(port_width, x+32)-1
        
        method_decls += ind_4 + "unsigned rd_{}_{}_{}({}_t* obj);" \
                                  .format( port_name, lsb, msb, sc_module_name )
  
      # write a single string
      method_decls += ind_4 + "void     wr_{}({}_t* obj, const char* x);" \
                                .format( port_name, sc_module_name )
    method_decls += "\n"
    
    #...................................................................
    # method_impls: implements cffi cdef methods in c_wrapper
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    if port_width <= 32:
      
      method_impls += '''
unsigned rd_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read(); }}''' \
      .format( port_name, sc_module_name, sc_type, port_name )
      
      method_impls += '''
void wr_{}({}_t* obj, unsigned x)
{{ static_cast<{}*>(obj->{})->write(x); }}
  '''.format( port_name, sc_module_name, sc_type, port_name )
      
    else:
      # stripmine the read
      for x in xrange(0, port_width, 32):
        lsb, msb = x, min(port_width, x+32)-1
        method_impls += '''
unsigned rd_{}_{}_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read().range({},{}).to_uint(); }}''' \
          .format( port_name, lsb, msb, sc_module_name, sc_type, port_name, msb, lsb )
      
      # single write
      method_impls += '''
void wr_{}({}_t* obj, const char* x)
{{ static_cast<{}*>(obj->{})->write(x); }}
'''       .format( port_name, sc_module_name, sc_type, port_name )
  
  delete_stmts += '''
  {sc_module_name} *model = static_cast< {sc_module_name}* >(obj->model);
  delete model;
  
  delete obj;
    '''.format( **vars() )
  
  templ = os.path.dirname( os.path.abspath( __file__ ) ) + \
          os.path.sep + 'systemc_wrapper.templ.cpp'
  
  with open( templ, "r" )           as template, \
       open( c_wrapper_file, "w" )  as output:
    
    output.write( template.read().format(**vars()) )

  cdef = '''
    typedef struct
    {{
      {cdef_port_decls}
      
      void *model;
      
    }} {sc_module_name}_t;

    {method_decls}

    {sc_module_name}_t* create();
    void destroy({sc_module_name}_t *obj);

    void sim_comb();
    void sim_cycle();
    '''.format( **vars() )
  
  return cdef
#-----------------------------------------------------------------------
# create_shared_lib
#-----------------------------------------------------------------------
# Link all the .o files and systemc lib into a single .so file

def create_shared_lib( lib_file, c_wrapper_file, all_objs, include_dirs, obj_dir ):

  # double check
    
  if "SYSTEMC_INCLUDE" not in os.environ:
    raise SystemCIncludeEnvError( '''\n
-   SystemC Include Environment Variable $SYSTEMC_INCLUDE doesn't exist!
    ''')
    
  if "SYSTEMC_LIBDIR" not in os.environ:
    raise SystemCLibraryEnvError( '''\n
-   SystemC Library Environment Variable $SYSTEMC_LIBDIR doesn't exist!
    ''')
  
   # Get the full include folder
  include = " ".join( [ "-I. -I .." ] +
                      [ "-I" + x for x in include_dirs ] +
                      [ "-I" + os.environ["SYSTEMC_INCLUDE"] ]
                    )
  library = " ".join( [ "-L. -L .." ] +
                      [ "-L" + obj_dir ] +
                      [ "-L" + os.environ["SYSTEMC_LIBDIR"] ]
                    )
  rpath   = os.environ["SYSTEMC_LIBDIR"]
  objects = " ".join( all_objs )
  
  compile_cmd = ( 'g++ -o {lib_file} {c_wrapper_file} '
                  '{objects} -fPIC -shared -O1 -fstrict-aliasing '
                  '-Wall -Wno-long-long -Werror {include} {library} '
                  '-Wl,-rpath={rpath} -lsystemc -lm' ) \
                  .format( **vars() )
  # print(compile_cmd)
  
  try:
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
  except CalledProcessError as e:
    raise SystemCCompileError( "\n\n-   {}\n".format(e.output) )
    
#-----------------------------------------------------------------------
# gen_py_wrapper
#-----------------------------------------------------------------------
# Create the python wrapper

def create_py_wrapper( model, py_wrapper_file, cdef ):
  
  port_defs  = []
  from ..translation.cpp_helpers import recurse_port_hierarchy
  for x in model.get_ports( preserve_hierarchy=True ):
    recurse_port_hierarchy( x, port_defs )

  set_inputs = []
  set_comb   = []
  set_next   = []
  
  inports  = model.get_inports()
  outports = model.get_outports()
  
  for (sc_name, port) in model._port_dict.iteritems():
    if port.name == "clk": continue
    
    if port in inports:
      set_inputs.append( "{sc_name} = s.{port.name}".format(**vars()) )
      if port.nbits > 32:
        set_inputs.append( "s._ffi.wr_{sc_name}(m, str(s.{port.name}.uint()))".format(**vars()) )
      else:
        set_inputs.append( "s._ffi.wr_{sc_name}(m, s.{port.name})".format(**vars()) )
      
      # empty line for better looking
      set_inputs.append("")
        
    if port in outports:
      
      if port.nbits > 32:
      # stripmine the read
        for x in xrange(0, port.nbits, 32):
          
          py_msb = min( port.nbits, x+32 )
          # because systemc uses range [l,r] but pymtl uses [l,r)
          sc_msb = py_msb - 1
          
          foo   = '{foo}'
          
          tmp = ("s.{port.name}[{x}:{py_msb}].{foo} = s._ffi.rd_{sc_name}_{x}_{sc_msb}(m)".format(**vars()) )
          set_comb.append( tmp.format(foo = "value") )
          set_next.append( tmp.format(foo = "next") )
      else:
        set_comb.append( "s.{port.name}.value = s._ffi.rd_{sc_name}(m)".format(**vars()) )
        set_next.append( "s.{port.name}.next = s._ffi.rd_{sc_name}(m)".format(**vars()) )
      
      # empty line for better looking
      set_comb.append("")
      set_next.append("")
        
  port_defs  = "\n    "  .join( port_defs )
  set_inputs = "\n      ".join( set_inputs )
  set_comb   = "\n      ".join( set_comb )
  set_next   = "\n      ".join( set_next )
  class_name = model.class_name
  sclinetrace = False
  
  templ = os.path.dirname( os.path.abspath( __file__ ) ) + \
          os.path.sep + 'systemc_wrapper.templ.py'
          
  # create source
  with open( templ, 'r' )           as template, \
       open( py_wrapper_file, 'w' ) as output:
    output.write( template.read().format(**vars()) )
  
  
