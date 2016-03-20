#=======================================================================
# verilog.py
#=======================================================================

from __future__ import print_function

import re
import os
import sys
import inspect
import collections
from   ...model.metaclasses        import MetaCollectArgs

from pymtl import *

from ..translation.verilog_structural import (
  mangle_name, tab, endl, port_delim, pretty_align,
  title_bar, header, start_mod, port_declarations, end_mod,
  start_param, end_param, start_ports, end_ports, connection,
)

#-----------------------------------------------------------------------
# VerilogImportError
#-----------------------------------------------------------------------

class VerilogImportError( Exception ):
  pass

class SomeMeta( MetaCollectArgs ):
  def __call__( self, *args, **kwargs ):
    inst = super( SomeMeta, self ).__call__( *args, **kwargs )

    # TODO: THIS IS SUPER HACKY. FIXME
    # We import TranslationTool here because of circular imports...
    from ..translation.verilator_sim import TranslationTool

    # TODO: THIS IS SUPER HACKY. FIXME
    # After the VerilogModel has been constructed and __init__ has
    # completed, pass the VerilogModel into the TranslationTool.
    # We need to do this **before** elaboration, and before the parent who
    # instantiated us completes their initialization. This is because if
    # we wait, then we'll have to find all the references to the
    # original VerilogModel and its ports/other members and swap them!
    #
    # A simpler but less user friendly way to do this is to force the user
    # to **always** wrap instantiations of VerilogModels in the
    # TranslationTool explicitly, like so:
    #
    # >>> my_verilog_model = TranslationTool( MyVerilogModel( p1, p2 ) )
    #

    # I think there is no way to turn on VCD dumping after the fact, so I
    # think we have no choice but to always turn on VCD dumping for now
    # if we are using Verilog import? -cbatten

    inst.vcd_file = '__dummy__'

    new_inst = TranslationTool( inst, lint=True )

    new_inst.vcd_file = None

    # TODO: THIS IS SUPER HACKY. FIXME
    # We hack the TranslationTool model in all kinds of awful ways to make
    # it look like the original VerilogModel. This ensures the the
    # translated Verilog code and the generated Python wrapper looks the
    # same whether the parent design is just passed into SimulationTool,
    # or passed into TranslationTool first.

    new_inst.__class__.__name__  = inst.__class__.__name__
    new_inst.__class__.__bases__ = (VerilogModel,)
    new_inst._args       = inst._args
    new_inst.vprefix     = inst.vprefix
    new_inst.modulename  = inst.modulename
    new_inst.sourcefile  = inst.sourcefile
    new_inst.vlinetrace  = inst.vlinetrace
    new_inst._param_dict = inst._param_dict
    new_inst._port_dict  = inst._port_dict

    # TODO: THIS IS SUPER HACKY. FIXME
    # This copies the user-defined line_trace method from the
    # VerilogModel to the generated Python wrapper.
    try:
      new_inst.__class__.line_trace = inst.__class__.__dict__['line_trace']

      # If we make it here this means the user has set Verilog line
      # tracing to true, but has _also_ defined a PyMTL line tracing, but
      # you can't have both.

      if inst.vlinetrace:
        raise VerilogImportError( "Cannot define a PyMTL line_trace\n"
          "function and also use vlinetrace = True. Must use _either_\n"
          "PyMTL line tracing or use Verilog line tracing." )

    except KeyError:
      pass

    return new_inst

#-----------------------------------------------------------------------
# VerilogModel
#-----------------------------------------------------------------------

class VerilogModel( Model ):
  """
  A PyMTL model for importing hand-written Verilog modules.

  Attributes:
    modulename  Name of the Verilog module to import.
    sourcefile  Location of the .v file containing the module.
  """
  __metaclass__ = SomeMeta

  modulename   = None
  sourcefile   = None
  vprefix      = None
  vlinetrace   = False

  _param_dict  = None
  _port_dict   = None

  #---------------------------------------------------------------------
  # set_params
  #---------------------------------------------------------------------
  def set_params( self, param_dict ):
    """Specify values for each parameter in the imported Verilog module.

    Note that param_dict should be a dictionary that provides a mapping
    from parameter names (strings) to parameter values, for example:

    >>> s.set_params({
    >>>   'param1': 5,
    >>>   'param2': 0,
    >>> })
    """

    self._param_dict = collections.OrderedDict( sorted(param_dict.items()) )

  #---------------------------------------------------------------------
  # set_ports
  #---------------------------------------------------------------------
  def set_ports( self, port_dict ):
    """Specify values for each parameter in the imported Verilog module.

    Note that port_dict should be a dictionary that provides a mapping
    from port names (strings) to PyMTL InPort or OutPort objects, for
    examples:

    >>> s.set_ports({
    >>>   'clk':    s.clk,
    >>>   'reset':  s.reset,
    >>>   'input':  s.in_,
    >>>   'output': s.out,
    >>> })
    """

    self._port_dict = collections.OrderedDict( sorted(port_dict.items()) )

  #---------------------------------------------------------------------
  # _auto_init
  #---------------------------------------------------------------------
  def _auto_init( self ):
    """Infer fields not set by user based on Model attributes."""

    if not self.modulename:
      self.modulename = self.__class__.__name__

    if not self.sourcefile:
      file_ = inspect.getfile( self.__class__ )
      self.sourcefile = os.path.join( os.path.dirname( file_ ),
                                      self.modulename+'.v' )

    # I added an extra check to only add the prefix if has not already
    # been added. Once we started using Verilog import and then turning
    # around and translated in the importing module this is what I needed
    # to do to get things to work -cbatten.

    if self.vprefix and not self.modulename.startswith(self.vprefix):
      self.modulename = self.vprefix + "_" + self.modulename

    if not self._param_dict:
      self._param_dict = self._args

    if not self._port_dict:
      self._port_dict = { port.name: port for port in self.get_ports() }

#-----------------------------------------------------------------------
# import_module
#-----------------------------------------------------------------------

def import_module( model, o ):
  """Generate Verilog source for a user-defined VerilogModule and return
  the name of the source file containing the imported component.
  """

  symtab = [()]*4

  print( header              ( model,    symtab ), file=o, end='' )
  print( start_mod.format    ( model.class_name ), file=o,        )
  print( port_declarations   ( model,    symtab ), file=o, end='' )
  print( _instantiate_verilog( model            ), file=o         )
  print( end_mod  .format    ( model.class_name ), file=o )
  print( file=o )

  return model.sourcefile

#-----------------------------------------------------------------------
# import_sources
#-----------------------------------------------------------------------
# The right way to do this is to use a recursive function like I have
# done below. This ensures that files are inserted into the output stream
# in the correct order. -cbatten

# Regex to extract verilog filenames from `include statements

include_re = re.compile( r'"(?P<filename>[\w/\.-]*)"' )

def output_verilog_file( fout, include_path, verilog_file ):
  with open( verilog_file, 'r' ) as fp:

    short_verilog_file = verilog_file
    if verilog_file.startswith( include_path+"/" ):
      short_verilog_file = verilog_file[len(include_path+"/"):]

    fout.write( '`line 1 "{}" 0\n'.format( short_verilog_file ) )

    line_num = 0
    for line in fp:
      line_num += 1
      if '`include' in line:
        filename = include_re.search( line ).group( 'filename' )
        fullname = os.path.join( include_path, filename )
        output_verilog_file( fout, include_path, fullname )
        fout.write( '\n' )
        fout.write( '`line {} "{}" 0\n'.format( line_num+1, short_verilog_file ) )
      else:
        fout.write( line )

def import_sources( source_list, o ):
  """Import Verilog source from all Verilog files source_list, as well
  as any source files specified by `include within those files.
  """

  if not source_list:
    return

  # For now we assume the first file in the sources_list is top?

  top_verilog_file = source_list[0]

  # All verilog includes are relative to the root of the PyMTL project.
  # We identify the root of the PyMTL project by looking for the special
  # .pymtl-python-path file.

  _path = os.path.dirname( top_verilog_file )
  special_file_found = False
  include_path = os.path.dirname( os.path.abspath( top_verilog_file ) )
  while include_path != "/":
    if os.path.exists( include_path + os.path.sep + ".pymtl-python-path" ):
      special_file_found = True
      sys.path.insert(0,include_path)
      break
    include_path = os.path.dirname(include_path)

  # If we could not find the special .pymtl-python-path file, then assume
  # the include directory is the same as the directory that contains the
  # verilog file.

  if not special_file_found:
    include_path = os.path.dirname( os.path.abspath( top_verilog_file ) )

  # Regex to extract verilog filenames from `include statements

  include_re = re.compile( r'"(?P<filename>[\w/\.-]*)"' )

  # Iterate through all source files and add any `include files to the
  # list of source files to import.

  output_verilog_file( o, include_path, source_list[0] )

  # for verilog_file in source_list:
  #
  #   print(verilog_file)
  #   with open( verilog_file, 'r' ) as fp:
  #     for line in fp:
  #       if '`include' in line:
  #         filename = include_re.search( line ).group( 'filename' )
  #         fullname = os.path.join( include_path, filename )
  #         if fullname not in source_list:
  #           source_list.append( fullname )

  # Iterate through all source files in reverse order and write out all
  # source code from imported/`included verilog files. Do this in reverse
  # order to (hopefully) resolve any `define dependencies, and remove any
  # lines with `include statements.

  # for verilog_file in reversed( source_list ):
  #
  #   # We remove the include directory from the verilog file name to make
  #   # error reporting by Verilator more succinct. -cbatten
  #
  #   short_verilog_file = verilog_file
  #   if verilog_file.startswith( include_path+"/" ):
  #     short_verilog_file = verilog_file[len(include_path+"/"):]
  #
  #   src = '`line 1 "{}" 0\n'.format( short_verilog_file )
  #
  #   with open( verilog_file, 'r' ) as fp:
  #     for line in fp:
  #       if '`include' not in line:
  #         src += line
  #       else:
  #         src += "// " + line
  #
  #   print( src, file=o )

#-----------------------------------------------------------------------
# _instantiate_verilog
#-----------------------------------------------------------------------

def _instantiate_verilog( model ):

  model._auto_init()

  params = [ connection.format(k, v) for k,v in model._param_dict.items() ]

  connections = []
  for verilog_portname, port in model._port_dict.items():
    pymtl_port = mangle_name( port.name )
    connections.append( connection.format( verilog_portname, pymtl_port ) )
  connections = pretty_align( connections, '(' )

  s  = tab + '// Imported Verilog source from:' + endl
  s += tab + '// {}'.format( model.sourcefile ) + endl
  s += endl
  s += tab + model.modulename + start_param + endl
  s += port_delim.join( params ) + endl
  s += tab + end_param + tab + 'verilog_module' + endl
  s += tab + start_ports + endl
  s += port_delim.join( connections ) + endl
  s += tab + end_ports + endl

  return s
