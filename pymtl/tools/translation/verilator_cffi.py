#=======================================================================
# verilator_cffi.py
#=======================================================================

from __future__ import print_function

import os
import shutil

import verilog_structural
from ...tools.simulation.vcd import get_vcd_timescale

from subprocess          import check_output, STDOUT, CalledProcessError
from ...model.signals    import InPort, OutPort
from ...model.PortBundle import PortBundle
from exceptions          import VerilatorCompileError

#-----------------------------------------------------------------------
# verilog_to_pymtl
#-----------------------------------------------------------------------
# Create a PyMTL compatible interface for Verilog HDL.

def verilog_to_pymtl( model, verilog_file, c_wrapper_file,
                      lib_file, py_wrapper_file, vcd_en, lint, verilator_xinit ):

  model_name = model.class_name

  try:
    vlinetrace = model.vlinetrace
  except AttributeError:
    vlinetrace = False

  # Verilate the model  # TODO: clean this up
  verilate_model( verilog_file, model_name, vcd_en, lint )

  # Add names to ports of module
  for port in model.get_ports():
    port.verilog_name   = verilog_structural.mangle_name( port.name )
    port.verilator_name = verilator_mangle( port.verilog_name )

  # Create C++ Wrapper
  cdefs = create_c_wrapper( model, c_wrapper_file, vcd_en, vlinetrace, verilator_xinit )

  # Create Shared C Library
  create_shared_lib( model_name, c_wrapper_file, lib_file,
                     vcd_en, vlinetrace )

  # Create PyMTL wrapper for CFFI interface to Verilated model
  create_verilator_py_wrapper( model, py_wrapper_file, lib_file,
                               cdefs, vlinetrace )

#-----------------------------------------------------------------------
# verilate_model
#-----------------------------------------------------------------------
# Convert Verilog HDL into a C++ simulator using Verilator.
# http://www.veripool.org/wiki/verilator

def verilate_model( filename, model_name, vcd_en, lint ):

  # verilator commandline template

  compile_cmd = ( 'verilator -cc {source} -top-module {model_name} '
                  '--Mdir {obj_dir} {flags}' )

  # verilator commandline options

  source  = filename
  obj_dir = 'obj_dir_' + model_name
  flags   = ' '.join([
              '-Wno-lint' if not lint else '',
              '-Wno-UNOPTFLAT',
              '--unroll-count 1000000',
              '--unroll-stmts 1000000',
              '--assert',
              '--trace' if vcd_en else '',
            ])

  # remove the obj_dir because issues with staleness

  if os.path.exists( obj_dir ):
    shutil.rmtree( obj_dir )

  # create the verilator compile command

  compile_cmd = compile_cmd.format( **vars() )

  # try compilation

  try:
    # print( compile_cmd )
    result = check_output( compile_cmd, stderr=STDOUT, shell=True )
    # print( result )

  # handle verilator failure

  except CalledProcessError as e:
    # error_msg = """
    #   Module did not Verilate!
    #
    #   Command:
    #   {command}
    #
    #   Error:
    #   {error}
    # """

    # We remove the final "Error: Command Failed" line to make the output
    # more succinct.

    split_output = e.output.splitlines()
    error = '\n'.join(split_output[:-1])

    if not split_output[-1].startswith("%Error: Command Failed"):
      error += "\n"+split_output[-1]

    error_msg = """
See "Errors and Warnings" section in the manual located here
http://www.veripool.org/projects/verilator/wiki/Manual-verilator
for more details on various Verilator warnings and error messages.

{error}"""

    raise VerilatorCompileError( error_msg.format(
      command = e.cmd,
      error   = error
    ))

#-----------------------------------------------------------------------
# create_c_wrapper
#-----------------------------------------------------------------------
# Generate a C wrapper file for Verilated C++.

def create_c_wrapper( model, c_wrapper_file, vcd_en, vlinetrace, verilator_xinit ):

  template_dir      = os.path.dirname( os.path.abspath( __file__ ) )
  template_filename = template_dir + os.path.sep + 'verilator_wrapper.templ.c'
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
    code = 'm->{verilator_name} = {dereference}model->{verilator_name};'

    verilator_name = port.verilator_name
    bitwidth       = port.nbits
    dereference    = '&' if bitwidth <= 64 else ''

    return code.format( **locals() )

  # Create port declaration, initialization, and extern statements
  indent_zero = '\n'
  indent_two  = '\n  '
  indent_four = '\n    '
  indent_six  = '\n      '

  port_externs = indent_two .join( [ port_to_decl( x ) for x in ports ] )
  port_decls   = indent_zero.join( [ port_to_decl( x ) for x in ports ] )
  port_inits   = indent_two .join( [ port_to_init( x ) for x in ports ] )

  # Convert verilator_xinit to number
  if   ( verilator_xinit == "zeros" ) : verilator_xinit_num = 0
  elif ( verilator_xinit == "ones"  ) : verilator_xinit_num = 1
  elif ( verilator_xinit == "rand"  ) : verilator_xinit_num = 2
  else : print( "Not valid choice" )

  # Generate the source code using the template
  with open( template_filename , 'r' ) as template, \
       open( c_wrapper_file,     'w' ) as output:

    c_src = template.read()
    c_src = c_src.format( model_name    = model.class_name,
                          port_externs  = port_externs,
                          port_decls    = port_decls,
                          port_inits    = port_inits,
                          # What was this for? -cbatten
                          # vcd_prefix    = vcd_file[:-4],
                          vcd_timescale = get_vcd_timescale( model ),
                          dump_vcd      = '1' if vcd_en else '0',
                          vlinetrace    = '1' if vlinetrace else '0',

                          verilator_xinit_num = verilator_xinit_num,
                        )

    output.write( c_src )

  return port_decls.replace( indent_zero, indent_six )

#-----------------------------------------------------------------------
# create_shared_lib
#-----------------------------------------------------------------------
# Compile the cpp wrapper into a shared library.
#
# Verilator suggests:
#
# For best performance, run Verilator with the "-O3 --x-assign=fast
# --noassert" flags. The -O3 flag will require longer compile times, and
# --x-assign=fast may increase the risk of reset bugs in trade for
# performance; see the above documentation for these flags.
#
# Minor Verilog code changes can also give big wins. You should not have
# any UNOPTFLAT warnings from Verilator. Fixing these warnings can
# result in huge improvements; one user fixed their one UNOPTFLAT
# warning by making a simple change to a clock latch used to gate clocks
# and gained a 60% performance improvement.
#
# Beyond that, the performance of a Verilated model depends mostly on
# your C++ compiler and size of your CPU's caches.
#
# By default, the lib/verilated.mk file has optimization
# turned off. This is for the benefit of new users, as it improves
# compile times at the cost of runtimes. To add optimization as the
# default, set one of three variables, OPT, OPT_FAST, or OPT_SLOW
# lib/verilated.mk. Or, use the -CFLAGS and/or -LDFLAGS option on the
# verilator command line to pass the flags directly to the compiler or
# linker. Or, just for one run, pass them on the command line to make:
#
#   make OPT_FAST="-O2" -f Vour.mk Vour__ALL.a

# OPT_FAST specifies optimizations for those programs that are part of
# the fast path, mostly code that is executed every cycle. OPT_SLOW
# specifies optimizations for slow-path files (plus tracing), which
# execute only rarely, yet take a long time to compile with optimization
# on. OPT specifies overall optimization and affects all compiles,
# including those OPT_FAST and OPT_SLOW affect. For best results, use
# OPT="-O2", and link with "-static". Nearly the same results can be had
# with much better compile times with OPT_FAST="-O1 -fstrict-aliasing".
# Higher optimization such as "-O3" may help, but gcc compile times may
# be excessive under O3 on even medium sized designs. Alternatively,
# some larger designs report better performance using "-Os".
#
# http://www.veripool.org/projects/verilator/wiki/Manual-verilator

# I have added a new feature which compiles all of the standard Verilator
# code into a static library and then simply links this in. This reduces
# compile times.

def try_cmd( name, cmd ):

  # print( "cmd: ", cmd )

  try:
    result = check_output( cmd.split() , stderr=STDOUT )

  # handle gcc/llvm failure

  except CalledProcessError as e:
    error_msg = """
      {name} error!

      Command:
      {command}

      Error:
      {error}
    """

    raise Exception( error_msg.format(
      name      = name,
      command   = ' '.join( e.cmd ),
      error     = e.output
    ))

def compile( flags, include_dirs, output_file, input_files ):

  compile_cmd = 'g++ {flags} {idirs} -o {ofile} {ifiles}'

  compile_cmd = compile_cmd.format(
    flags  = flags,
    idirs  = ' '.join( [ '-I'+s for s in include_dirs ] ),
    ofile  = output_file,
    ifiles = ' '.join( input_files ),
  )

  try_cmd( "Compilation", compile_cmd )

def make_lib( output_file, input_files ):

  # First run ar command

  ar_cmd = 'ar rcv {ofile} {ifiles}'

  ar_cmd = ar_cmd.format(
    ofile  = output_file,
    ifiles = ' '.join( input_files ),
  )

  try_cmd( "Make library", ar_cmd )

  # Then run ranlib command

  ranlib_cmd = 'ranlib {lib}'

  ranlib_cmd = ranlib_cmd.format(
    lib = output_file,
  )

  try_cmd( "Make library", ranlib_cmd )

def create_shared_lib( model_name, c_wrapper_file, lib_file,
                       vcd_en, vlinetrace ):

  # We need to find out where the verilator include directories are
  # globally installed. We first check the PYMTL_VERILATOR_INCLUDE_DIR
  # environment variable, and if that does not exist then we fall back on
  # using pkg-config.

  verilator_include_dir = os.environ.get('PYMTL_VERILATOR_INCLUDE_DIR')
  if verilator_include_dir is None:
    cmd = ['pkg-config', '--variable=includedir', 'verilator']

    try:

      verilator_include_dir = check_output( cmd, stderr=STDOUT ).strip()

    except OSError as e:

      error_msg = """
Error trying to find verilator include directories. The
PYMTL_VERILATOR_INCLUDE_DIR environment variable was not set,
so we attempted to use pkg-config to find where verilator was
installed, but it looks like we had trouble finding or executing
pkg-config itself. Try running the following command on your own
to debug the issue.

Command:
{command}

Error:
[Errno {errno}] {strerror}
      """

      raise VerilatorCompileError( error_msg.format(
        command  = ' '.join( cmd ),
        errno    = e.errno,
        strerror = e.strerror,
      ))

    except CalledProcessError as e:

      error_msg = """
Error trying to find verilator include directories. The
PYMTL_VERILATOR_INCLUDE_DIR environment variable was not set,
so we attempted to use pkg-config to find where verilator was
installed, but it looks like pkg-config had trouble finding
the verilator.pc file installed by verilator. Is a recent
version of verilator installed? Older versions of verilator
did not have pkg-config support. Try running the following
command on your own to debug the issue.

Command:
{command}

Error:
{error}
      """

      raise VerilatorCompileError( error_msg.format(
        command = ' '.join( e.cmd ),
        error   = e.output,
      ))

  include_dirs = [
    verilator_include_dir,
    verilator_include_dir+"/vltstd",
  ]

  # Compile standard Verilator code if libverilator.a does not exist.
  # Originally, I was also including verilated_dpi.cpp in this library,
  # but for some reason that screws up line tracing. Somehow there is
  # some kind of global state or something that is shared across the
  # shared libraries or something. I was able to fix it by recompiling
  # verilated_dpi if linetracing is enabled. Actually, the line tracing
  # doesn't work -- if you use this line tracing approach, so we are back
  # to always recomping everyting every time for now.

  # if not os.path.exists( "libverilator.a" ):
  #
  #   compile(
  #     flags        = "-O3 -c",
  #     include_dirs = include_dirs,
  #     output_file  = "verilator.o",
  #     input_files  = [ verilator_include_dir+"/verilated.cpp" ]
  #   )
  #
  #   compile(
  #     flags        = "-O3 -c",
  #     include_dirs = include_dirs,
  #     output_file  = "verilator_vcd_c.o",
  #     input_files  = [ verilator_include_dir+"/verilated_vcd_c.cpp" ]
  #   )
  #
  #   # compile(
  #   #   flags        = "-O3 -c",
  #   #   include_dirs = include_dirs,
  #   #   output_file  = "verilator_dpi.o",
  #   #   input_files  = [ verilator_include_dir+"/verilated_dpi.cpp" ]
  #   # )
  #
  #   make_lib(
  #     output_file  = "libverilator.a",
  #     # input_files  = [ "verilator.o", "verilator_vcd_c.o", "verilator_dpi.o" ]
  #     input_files  = [ "verilator.o", "verilator_vcd_c.o" ]
  #    )

  obj_dir_prefix = "obj_dir_{m}/V{m}".format( m=model_name )

  # We need to find a list of all the generated classes. We look in the
  # Verilator makefile for that.

  cpp_sources_list = []

  with open( obj_dir_prefix+"_classes.mk" ) as mkfile:
    found = False
    for line in mkfile:
      if line.startswith("VM_CLASSES_FAST += "):
        found = True
      elif found:
        if line.strip() == "":
          found = False
        else:
          filename = line.strip()[:-2]
          cpp_file = "obj_dir_{m}/{f}.cpp".format( m=model_name, f=filename )
          cpp_sources_list.append( cpp_file )

  # Compile this module

  cpp_sources_list += [
    obj_dir_prefix+"__Syms.cpp",
    verilator_include_dir+"/verilated.cpp",
    verilator_include_dir+"/verilated_dpi.cpp",
    c_wrapper_file,
  ]

  if vcd_en:
    cpp_sources_list += [
      verilator_include_dir+"/verilated_vcd_c.cpp",
      obj_dir_prefix+"__Trace.cpp",
      obj_dir_prefix+"__Trace__Slow.cpp",
    ]

  compile(
    # flags        = "-O1 -fstrict-aliasing -fPIC -shared -L. -lverilator",
    flags        = "-O1 -fstrict-aliasing -fPIC -shared",
    include_dirs = include_dirs,
    output_file  = lib_file,
    input_files  = cpp_sources_list,
  )

#-----------------------------------------------------------------------
# create_verilator_py_wrapper
#-----------------------------------------------------------------------

def create_verilator_py_wrapper( model, wrapper_filename, lib_file,
                                 cdefs, vlinetrace ):

  template_dir      = os.path.dirname( os.path.abspath( __file__ ) )
  template_filename = template_dir + os.path.sep + 'verilator_wrapper.templ.py'

  port_defs  = []
  set_inputs = []
  set_comb   = []
  set_next   = []

  from cpp_helpers import recurse_port_hierarchy
  for x in model.get_ports( preserve_hierarchy=True ):
    recurse_port_hierarchy( x, port_defs )

  for port in model.get_inports():
    if port.name == 'clk': continue
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
        vlinetrace  = '1' if vlinetrace else '0',
    )

    #py_src += 'XTraceEverOn()' # TODO: add for tracing?

    output.write( py_src )
    #print( py_src )

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
    inputs.append( 's._m.{v_name}[{idx}] = s.{py_name}{offset}' \
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
    assign = 's.{py_name}{offset}.{sigtype} = s._m.{v_name}[{idx}]' \
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
    #print( py_src )
