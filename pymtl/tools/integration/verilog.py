#=======================================================================
# verilog.py
#=======================================================================

from __future__ import print_function

import re
import os

from pymtl import *

from ..translation.verilog_structural import (
  tab, endl, port_delim, pretty_align,
  title_bar, header, start_mod, port_declarations, end_mod,
  start_param, end_param, start_ports, end_ports, connection,
)

#-----------------------------------------------------------------------
# VerilogModel
#-----------------------------------------------------------------------
class VerilogModel( Model ):
  _is_verilog = True
  module      = None
  filename    = None
  clk         = None
  reset       = None
  params      = None
  connections = None

#-----------------------------------------------------------------------
# import_module
#-----------------------------------------------------------------------
def import_module( model, o ):

  symtab = [()]*4

  print( header             ( model,    symtab ), file=o, end='' )
  print( start_mod.format   ( model.class_name ), file=o,        )
  print( port_declarations  ( model,    symtab ), file=o, end='' )
  print( instantiate_verilog( model            ), file=o         )
  print( end_mod  .format   ( model.class_name ), file=o )
  print( file=o )

  return model.filename

#-----------------------------------------------------------------------
# instantiate_verilog
#-----------------------------------------------------------------------
def instantiate_verilog( model ):

  params = [ connection.format( k, v ) for k,v in model.params.items() ]

  connections = []
  if model.vclk:
    connections.append( connection.format( model.vclk, model.clk.name ) )
  if model.vreset:
    connections.append( connection.format( model.vreset, model.reset.name ) )
  for port, verilog_portname in model.connections.items():
    connections.append( connection.format( verilog_portname, port.name ) )
  connections = pretty_align( connections, '(' )

  s  = tab + '// Imported Verilog source from:' + endl
  s += tab + '// {}'.format( model.filename ) + endl
  s += endl
  s += tab + model.module + start_param + endl
  s += port_delim.join( params ) + endl
  s += tab + end_param + tab + 'VERILOG_MODEL' + endl
  s += tab + start_ports + endl
  s += port_delim.join( connections ) + endl
  s += tab + end_ports + endl

  return s

#-----------------------------------------------------------------------
# import_sources
#-----------------------------------------------------------------------
def import_sources( source_list, o ):

  # Regex to extract verilog filenames from `include statements

  include_re = re.compile( r'"(?P<filename>[\w/\.-]*)"' )

  # Iterate through all source files and add any `include files to the
  # list of source files to import.

  for verilog_file in source_list:

    print( verilog_file )

    include_path = os.path.dirname( verilog_file )
    with open( verilog_file, 'r' ) as fp:
      for line in fp:
        if '`include' in line:
          filename = include_re.search( line ).group( 'filename' )
          fullname = os.path.join( include_path, filename )
          if fullname not in source_list:
            source_list.append( fullname )

  # Iterate through all source files in reverse order and write out all
  # source code from imported/`included verilog files. Do this in reverse
  # order to (hopefully) resolve any `define dependencies, and remove any
  # lines with `include statements.

  for verilog_file in reversed( source_list ):
    src = title_bar.replace('-','=').format( verilog_file )

    with open( verilog_file, 'r' ) as fp:
      for line in fp:
        if '`include' not in line:
          src += line

    print( src, file=o )

