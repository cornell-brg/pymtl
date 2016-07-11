#=======================================================================
# sc_helper.py
#=======================================================================

import os
import sys
import shutil
from subprocess import check_output, STDOUT, CalledProcessError

class SystemCIncludeEnvError( Exception ): pass
class SystemCLibraryEnvError( Exception ): pass
class SystemCCompileError   ( Exception ): pass

# get_sc_include and get_sc_lib now support pkg-config

def get_sc_include():
  
  # Check if SYSTEMC_INCLUDE is in the environment variable
  # The environment variable overrides pkg-config.

  sc_include_dir = os.environ.get( "SYSTEMC_INCLUDE" )
  
  if sc_include_dir == None:
    cmd = ["pkg-config", "--variable=includedir", "systemc"]
    
    try:
      sc_include_dir = check_output( cmd, stderr=STDOUT ).strip()
      
    except OSError as e:
      error_msg = """ SystemC include directory not found!
- $SYSTEMC_INCLUDE doesn't exist. PyMTL resorts to pkg-config instead.
- Cannot execute "pkg-config". Is pkg-config installed?

Try running the following command on your own to debug the issue.
{command}
      """
      raise SystemCIncludeEnvError( error_msg.format(
        command  = ' '.join( cmd ),
        errno    = e.errno,
        strerror = e.strerror,
      ))

    except CalledProcessError as e:
      error_msg = """ SystemC include directory not found!
- $SYSTEMC_INCLUDE doesn't exist. PyMTL resorts to pkg-config instead.
- pkg-config cannot find systemc.pc. Is SystemC installed?

Try running the following command on your own to debug the issue.
{command}
      """
      raise SystemCIncludeEnvError( error_msg.format(
        command = ' '.join( e.cmd ),
        error   = e.output,
      ))
  
  return sc_include_dir

def get_sc_lib():

  # Check if SYSTEMC_LIBDIR is in the environment variable
  # The environment variable overrides pkg-config.

  sc_library_dir = os.environ.get( "SYSTEMC_LIBDIR" )
  
  if sc_library_dir == None:
    cmd = ["pkg-config", "--variable=libarchdir", "systemc"]
    
    try:
      sc_library_dir = check_output( cmd, stderr=STDOUT ).strip()
      
    except OSError as e:
      error_msg = """ SystemC library directory not found!
- $SYSTEMC_LIBDIR doesn't exist. PyMTL resorts to pkg-config instead.
- Cannot execute "pkg-config". Is pkg-config installed?

Try running the following command on your own to debug the issue.
{command}
      """
      raise SystemCLibraryEnvError( error_msg.format(
        command  = ' '.join( cmd ),
        errno    = e.errno,
        strerror = e.strerror,
      ))

    except CalledProcessError as e:
      error_msg = """ SystemC library directory not found!
- $SYSTEMC_LIBDIR doesn't exist. PyMTL resorts to pkg-config instead.
- pkg-config cannot find systemc.pc. Is SystemC installed?

Try running the following command on your own to debug the issue.
{command}
      """
      raise SystemCLibraryEnvError( error_msg.format(
        command = ' '.join( e.cmd ),
        error   = e.output,
      ))
  
  return sc_library_dir

#-----------------------------------------------------------------------
# compile_object
#-----------------------------------------------------------------------
# Compile {src_name} to {obj_name}.o

def compile_object( obj_name, src_name, include_dirs ):
  
  # Get the full include folder
  include = " ".join( [ "-I. -I .. -I " + get_sc_include() ] +
                      [ "-I" + x for x in include_dirs ] )
  
  compile_cmd = ( 'g++ -o {obj_name}.o -DSYSTEMC_SIM '
                  '-fPIC -shared -O1 -fstrict-aliasing '
                  '-Wall -Wno-long-long -Werror '
                  ' {include} -c {src_name} '  ).format( **vars() )
  try:
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
  except CalledProcessError as e:
    raise SystemCCompileError( "\n-\n-   " + 
                                  "\n-   ".join( e.output.splitlines() ) )

#-----------------------------------------------------------------------
# systemc_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for SystemC.

def systemc_to_pymtl( model, obj_dir, include_dirs, sc_module_name, 
                      objs, c_wrapper_file, lib_file, py_wrapper_file ):
  
  cdef = create_c_wrapper( model, sc_module_name, c_wrapper_file )  
  
  create_shared_lib( lib_file, c_wrapper_file, objs, include_dirs, obj_dir )
  
  create_py_wrapper( model, py_wrapper_file, cdef )

#-----------------------------------------------------------------------
# gen_sc_datatype
#-----------------------------------------------------------------------
# 1   : sc_signal<bool>
# <=64: use sc_uint<bitwidth>
# >64 : use sc_biguint<bitwidth>

def gen_sc_datatype(port_width):
  
  sc_type = "sc_signal<bool>" # default 1-bit bool
  if port_width > 1:
    sc_type = "sc_signal< sc_{}uint<{}> >" \
                  .format("big" if port_width > 64 else "", port_width)
  
  return sc_type

#-----------------------------------------------------------------------
# create_c_wrapper
#-----------------------------------------------------------------------
# Create a c_wrapper for given pymtl file which inherits a SystemCModel
# Returns the cffi cdef string for convenience.

def create_c_wrapper( model, sc_module_name, c_wrapper_file ):
  
  sclinetrace = 1 if model.sclinetrace else 0
  
  port_width_dict = { x: y.nbits \
                      for x,y in model._port_dict.iteritems() }
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
  
  sc_simcontext* context = new sc_simcontext;
  m->context = sc_curr_simcontext = context;
  
  {sc_module_name}   *model = new {sc_module_name}("{sc_module_name}");
  m->model = model;
  '''.format(**vars())
  
  delete_stmts = ""
  
  for port_name, port_width in sorted(port_width_dict.items()):
    
    #...................................................................
    # port_decls: for the c_wrapper struct def
    #...................................................................
    
    cdef_port_decls += ind_6 + "void *{};".format(port_name)
    wrap_port_decls += ind_2 + "void *{};".format(port_name)
    
    #...................................................................
    # new and delete stmts: new and delete the ports
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    new_stmts += ind_2 + "{} *{} = new {}(\"{}\");" \
                           .format( sc_type, port_name, sc_type,
                                    port_name )
    new_stmts += ind_2 + "m->{} = {};".format( port_name, port_name )
    new_stmts += ind_2 + "model->{}(*{});\n".format( port_name, port_name )
    
    delete_stmts += ind_2 + "{} *{} = static_cast<{}*>(obj->{});" \
                              .format( sc_type, port_name, 
                                       sc_type, port_name )
    delete_stmts += ind_2 + "delete {};\n".format( port_name )
    
    #...................................................................
    # method_decls: for cffi cdef 
    #...................................................................
    
    if port_width <= 64:
      # rd
      method_decls += ind_4 + "unsigned long rd_{}({}_t* obj);" \
                                .format( port_name, sc_module_name )
      # wr
      method_decls += ind_4 + "void     wr_{}({}_t* obj, unsigned long x);" \
                                .format( port_name, sc_module_name )
    else:
      # stripmine the read
      for x in xrange(0, port_width, 64):
        lsb, msb = x, min(port_width, x+64)-1
        
        method_decls += ind_4 + "unsigned long rd_{}_{}_{}({}_t* obj);" \
                                  .format( port_name, lsb, msb, sc_module_name )
  
      # write a single string
      method_decls += ind_4 + "void     wr_{}({}_t* obj, const char* x);" \
                                .format( port_name, sc_module_name )
    method_decls += "\n"
    
    #...................................................................
    # method_impls: implements cffi cdef methods in c_wrapper
    #...................................................................
    
    sc_type = gen_sc_datatype(port_width)
    
    if port_width <= 64:
      
      method_impls += '''
unsigned long rd_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read(); }}''' \
      .format( port_name, sc_module_name, sc_type, port_name )
      
      method_impls += '''
void wr_{}({}_t* obj, unsigned long x)
{{ static_cast<{}*>(obj->{})->write(x); }}
  '''.format( port_name, sc_module_name, sc_type, port_name )
      
    else:
      # stripmine the read
      for x in xrange(0, port_width, 64):
        lsb, msb = x, min(port_width, x+64)-1
        method_impls += '''
unsigned long rd_{}_{}_{}({}_t* obj)
{{ return static_cast<{}*>(obj->{})->read().range({},{}).to_uint64(); }}''' \
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
    
    output.write( template.read().format( **vars() ) )
  
  cdef = '''
    typedef struct
    {{
      {cdef_port_decls}
      
      void *context;
      void *model;
      
    }} {sc_module_name}_t;

    {method_decls}

    {sc_module_name}_t* create();
    void destroy({sc_module_name}_t *obj);

    void sim({sc_module_name}_t *obj);
    
    void line_trace({sc_module_name}_t *obj, char *str);
    '''.format( **vars() )
  
  return cdef
#-----------------------------------------------------------------------
# create_shared_lib
#-----------------------------------------------------------------------
# Link all the .o files and systemc lib into a single .so file

def create_shared_lib( lib_file, c_wrapper_file, all_objs, include_dirs, obj_dir ):
  
  include = " ".join( [ "-I. -I .. -I " + get_sc_include() ] +
                      [ "-I" + x for x in include_dirs ] )
  library = " ".join( [ "-L. -L .. -L " + get_sc_lib() ] +
                      [ "-L" + obj_dir ] )
  rpath   = get_sc_lib()
  objects = " ".join( all_objs )
  
  compile_cmd = ( 'g++ -o {lib_file} {c_wrapper_file} -DSYSTEMC_SIM '
                  '{objects} -fPIC -shared -O1 -fstrict-aliasing '
                  '-Wall -Wno-long-long -Werror {include} {library} '
                  '-Wl,-rpath={rpath} -lsystemc -lm' ) \
                  .format( **vars() )
  # print(compile_cmd)
  try:
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
  except CalledProcessError as e:
    raise SystemCCompileError( "\n-\n-   " + 
                                  "\n-   ".join( e.output.splitlines() ))
    
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
  set_clock  = '''
      s._ffi.wr_clk(m, 0)
      s._ffi.sim( m )
      s._ffi.wr_clk(m, 1)
      s._ffi.sim( m )
  ''' if "clk" in model._port_dict else ""
    
  inports  = model.get_inports()
  outports = model.get_outports()
  
  for (sc_name, port) in model._port_dict.iteritems():
    if port.name == "clk": continue
    
    if port in inports:
      set_inputs.append( "{sc_name} = s.{port.name}".format( **vars() ) )
      
      if port.nbits > 64:
        set_inputs.append( "s._ffi.wr_{sc_name}(m, str(s.{port.name}.uint()))".format( **vars() ) )
      else:
        set_inputs.append( "s._ffi.wr_{sc_name}(m, s.{port.name})".format( **vars() ) )
      
      # empty line for better looking
      set_inputs.append("")
        
    if port in outports:
      
      if port.nbits > 64:
      # stripmine the read
        for x in xrange(0, port.nbits, 64):
          py_msb = min( port.nbits, x+64 )
          # because systemc uses range [l,r] but pymtl uses [l,r)
          sc_msb = py_msb - 1
          
          foo = '{foo}'
          tmp = ("s.{port.name}[{x}:{py_msb}].{foo} = s._ffi.rd_{sc_name}_{x}_{sc_msb}(m)".format( **vars() ) )
          
          set_comb.append( tmp.format(foo = "value") )
          set_next.append( tmp.format(foo = "next") )
      else:
        set_comb.append( "s.{port.name}.value = s._ffi.rd_{sc_name}(m)".format( **vars() ) )
        set_next.append( "s.{port.name}.next = s._ffi.rd_{sc_name}(m)".format( **vars() ) )
      
      # empty line for better looking
      set_comb.append("")
      set_next.append("")
        
  port_defs  = "\n    "  .join( port_defs )
  set_inputs = "\n      ".join( set_inputs )
  set_comb   = "\n      ".join( set_comb )
  set_next   = "\n      ".join( set_next )
  class_name = model.class_name
  sclinetrace = model.sclinetrace
  
  templ = os.path.dirname( os.path.abspath( __file__ ) ) + \
          os.path.sep + 'systemc_wrapper.templ.py'
          
  # write to the py wrapper
  with open( templ, 'r' )           as template, \
       open( py_wrapper_file, 'w' ) as output:
    output.write( template.read().format( **vars() ) )
  
  
