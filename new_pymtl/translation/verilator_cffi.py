#=======================================================================
# verilator_cffi.py
#=======================================================================

import os

import verilog_structural

from subprocess   import check_output, STDOUT, CalledProcessError
from ..signals    import InPort, OutPort
from ..PortBundle import PortBundle

#-----------------------------------------------------------------------
# verilog_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for Verilog HDL.
def verilog_to_pymtl( model, verilog_file, c_wrapper_file,
                      lib_file, py_wrapper_file ):

  model_name = model.class_name

  # Verilate the model
  verilate_model( verilog_file, model_name )  # TODO: clean this up

  # Add names to ports of module
  for port in model.get_ports():
    port.verilog_name   = verilog_structural.mangle_name( port.name )
    port.verilator_name = verilator_mangle( port.verilog_name )

  # Create C++ Wrapper
  cdefs = create_c_wrapper( model, c_wrapper_file )

  # Create Shared C Library
  create_shared_lib( model_name, c_wrapper_file, lib_file )

  # Create PyMTL wrapper for CFFI interface to Verilated model
  #pymtl_wrapper_from_ports( in_ports, out_ports, model_name,
  create_verilator_py_wrapper( model, py_wrapper_file, lib_file, cdefs )

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
  print cmd
  os.system( cmd )

#-----------------------------------------------------------------------
# create_c_wrapper
#-----------------------------------------------------------------------
# Generate a C wrapper file for Verilated C++.
def create_c_wrapper( model, c_wrapper_file ):

  template_filename = '../new_pymtl/translation/verilator_wrapper.templ.c'
  ports = model.get_ports()

  # Utility function for creating port declarations
  def port_to_decl( port ):
    code = '{data_type} * {verilator_name};'

    verilator_name = port.verilator_name
    bitwidth       = port.nbits

    if   bitwidth <= 8:  data_type = 'unsigned char'
    elif bitwidth <= 16: data_type = 'unsigned short'
    elif bitwidth <= 32: data_type = 'unsigned int'
    elif bitwidth <= 64: data_type = 'unsigned long'
    else:                data_type = 'unsigned int'

    return code.format( **locals() )

  # Utility function for creating port initializations
  def port_to_init( port ):
    code = '{verilator_name} = {dereference}model->{verilator_name};'

    verilator_name = port.verilator_name
    bitwidth       = port.nbits
    dereference    = '&' if bitwidth <= 64 else ''

    return code.format( **locals() )

  # Create port declaration, initialization, and extern statements
  pfx         = 'extern '
  indent_four = '\n    '
  indent_six  = '\n      '

  port_externs = indent_six .join( [ pfx+port_to_decl( x ) for x in ports ] )
  port_decls   = indent_four.join( [     port_to_decl( x ) for x in ports ] )
  port_inits   = indent_six .join( [     port_to_init( x ) for x in ports ] )

  # Generate the source code using the template
  with open( template_filename , 'r' ) as template, \
       open( c_wrapper_file,     'w' ) as output:

    c_src = template.read()
    c_src = c_src.format( model_name   = model.class_name,
                          port_externs = port_externs,
                          port_decls   = port_decls,
                          port_inits   = port_inits,
                        )

    output.write( c_src )

  return port_decls

#-----------------------------------------------------------------------
# create_shared_lib
#-----------------------------------------------------------------------
# Compile the cpp wrapper into a shared library.
def create_shared_lib( model_name, c_wrapper_file, lib_file ):

  # Compiler template string
  compile_cmd  = 'g++ {flags} -I {verilator} -o {libname} {cpp_sources}'

  flags        = '-O3 -fPIC -shared'
  verilator    = '{}/include'.format( os.environ['VERILATOR_ROOT'] )
  libname      = lib_file
  cpp_sources  = ' '.join( [
                   'obj_dir_{model_name}/V{model_name}.cpp',
                   'obj_dir_{model_name}/V{model_name}__Syms.cpp',
                   'obj_dir_{model_name}/V{model_name}__Trace.cpp',
                   'obj_dir_{model_name}/V{model_name}__Trace__Slow.cpp',
                   '{verilator}/verilated.cpp',
                   '{verilator}/verilated_vcd_c.cpp',
                   '{c_wrapper}'
                 ])

  # Substitute flags in compiler string, then any remaining flags
  compile_cmd = compile_cmd.format( **vars() )
  compile_cmd = compile_cmd.format( model_name = model_name,
                                    c_wrapper  = c_wrapper_file,
                                    verilator  = verilator )

  # Perform compilation
  try:
    result = check_output( compile_cmd.split() , stderr=STDOUT )
  except CalledProcessError as e:
    error_msg = """
      Module did not compile!

      Command:
      {command}

      Error:
      {error}
    """

    # Source:
    # \x1b[31m {source} \x1b[0m

    raise Exception( error_msg.format(
      command = ' '.join( e.cmd ),
      error   = e.output
    ))

#-----------------------------------------------------------------------
# create_verilator_py_wrapper
#-----------------------------------------------------------------------
def create_verilator_py_wrapper( model, wrapper_filename, lib_file, cdefs ):

  template_filename = '../new_pymtl/translation/verilator_wrapper.templ.py'

  port_defs  = []
  set_inputs = []
  set_comb   = []
  set_next   = []

  from cpp_helpers import recurse_port_hierarchy
  for x in model.get_ports( preserve_hierarchy=True ):
    recurse_port_hierarchy( x, port_defs )

  for port in model.get_inports():
    if port.name in ['clk', 'reset']: continue  # TODO: remove me!
    input_ = set_input_stmt( port )
    set_inputs.extend( input_ )

  for port in model.get_outports():
    comb, next_ = set_output_stmt( port )
    set_comb.extend( comb  )
    set_next.extend( next_ )

  # pretty printing
  indent_four = '\n    '
  indent_six  = '\n      '

  # create source
  with open( template_filename , 'r' ) as template, \
       open( wrapper_filename,   'w' ) as output:

    py_src = template.read()
    py_src = py_src.format(
        model_name  = model.class_name,
        port_decls  = cdefs,
        lib_file    = lib_file,
        port_defs   = indent_four.join( port_defs ),
        set_inputs  = indent_six .join( set_inputs ),
        set_comb    = indent_six .join( set_comb ),
        set_next    = indent_six .join( set_next ),
    )

    #py_src += 'XTraceEverOn()' # TODO: add for tracing?

    output.write( py_src )
    #print py_src

#-----------------------------------------------------------------------
# get_indices
#-----------------------------------------------------------------------
# Utility function for determining assignment of wide ports
def get_indices( port ):
  num_assigns = 1 if port.nbits <= 64 else (port.nbits-1)/32 + 1
  if num_assigns == 1:
    return [(0, "")]
  return [ ( i, '[{}:{}]'.format( i*32, min( i*32+32, port.nbits) ) )
           for i in range(num_assigns) ]

#-----------------------------------------------------------------------
# set_input_stmt
#-----------------------------------------------------------------------
def set_input_stmt( port ):
  inputs = []
  for idx, offset in get_indices( port ):
    inputs.append( 's._model.{v_name}[{idx}] = s.{py_name}{offset}' \
                    .format( v_name  = port.verilator_name,
                             py_name = port.name,
                             idx     = idx,
                             offset  = offset )
                   )
  return inputs

#-----------------------------------------------------------------------
# set_output_stmt
#-----------------------------------------------------------------------
# TODO: no way to distinguish between combinational and sequential
#       outputs, so we set outputs both ways...
#       This seems broken, but I can't think of a better way.
def set_output_stmt( port ):
  comb, next_ = [], []
  for idx, offset in get_indices( port ):
    assign = 's.{py_name}{offset}.{sigtype} = s._model.{v_name}[{idx}]' \
             .format( v_name  = port.verilator_name,
                      py_name = port.name,
                      idx     = idx,
                      offset  = offset,
                      sigtype = '{sigtype}' )
    comb .append( assign.format( sigtype = 'value' ) )
    next_.append( assign.format( sigtype = 'next'  ) )
  return comb, next_

#-----------------------------------------------------------------------
# verilator_mangle
#-----------------------------------------------------------------------
def verilator_mangle( signal_name ):
  return signal_name.replace( '__', '___05F' ).replace( '$', '__024' )

#-----------------------------------------------------------------------
# pymtl_wrapper_from_ports
#-----------------------------------------------------------------------
def pymtl_wrapper_from_ports( in_ports, out_ports, model_name, filename_w,
                              vobj_name, xobj_name, cdefs ):


  # Declare the interface ports for the wrapper class.
  port_defs = []
  for ports, port_type in [( in_ports, 'InPort' ), ( out_ports, 'OutPort' )]:

    # Replace all references to _M_ with .
    ports = [ ( name.replace('_M_', '.'), nbits ) for name, nbits in ports ]

    lists = []
    for port_name, bitwidth in ports:
      # Port List
      if '$' in port_name:
        pfx = port_name.split('$')[0]
        if pfx not in lists:
          lists.append(pfx)
          port_defs.append( 's.{} = []'.format( pfx ) )
        port_defs.append( 's.{port_list}.append( {port_type}( {bitwidth} ) )' \
                          .format( port_list = pfx,
                                    port_type = port_type,
                                    bitwidth  = bitwidth )
                        )
      else:
        port_defs.append( 's.{port_name} = {port_type}( {bitwidth} )' \
                           .format( port_name = port_name,
                                    port_type = port_type,
                                    bitwidth  = bitwidth )
                        )

  # Assigning input ports
  set_inputs = []
  for v_name, bitwidth in in_ports:
    py_name = v_name.replace('_M_', '.')
    if '$' in py_name:
      name, idx = py_name.split('$')
      py_name = '{name}[{idx}]'.format( name = name, idx = int(idx) )
    v_name = verilator_mangle( v_name )
    set_inputs.append( 's._model.{v_name}[0] = s.{py_name}' \
                       .format( v_name = v_name, py_name = py_name )
                     )

  # Assigning combinational output ports
  set_comb = []
  for v_name, bitwidth in out_ports:
    py_name = v_name.replace('_M_', '.')
    if '$' in py_name:
      name, idx = py_name.split('$')
      py_name = '{name}[{idx}]'.format( name = name, idx = int(idx) )
    v_name = verilator_mangle( v_name )
    set_comb.append( 's.{py_name}.value = s._model.{v_name}[0]' \
                      .format( v_name = v_name, py_name = py_name )
                    )

  # TODO: no way to distinguish between combinational and sequential
  #       outputs, so we set outputs both ways...
  #       This seems broken, but I can't think of a better way.

  # Assigning sequential output ports
  set_next = []
  for v_name, bitwidth in out_ports:
    py_name = v_name.replace('_M_', '.')
    if '$' in py_name:
      name, idx = py_name.split('$')
      py_name = '{name}[{idx}]'.format( name = name, idx = int(idx) )
    v_name = verilator_mangle( v_name )
    set_next.append( 's.{py_name}.next = s._model.{v_name}[0]' \
                      .format( v_name = v_name, py_name = py_name )
                    )

  with open( template_filename , 'r' ) as template, \
       open( wrapper_filename,   'w' ) as output:

    py_src = template.read()
    py_src = py_src.format(
        model_name  = model_name,
        port_decls  = cdefs,
        port_defs   = '\n    '  .join( port_defs ),
        set_inputs  = '\n      '.join( set_inputs ),
        set_comb    = '\n      '.join( set_comb ),
        set_next    = '\n      '.join( set_next ),
    )

    # TODO: needed for tracing?
    #w += 'XTraceEverOn()'

    output.write( py_src )
    #print py_src

