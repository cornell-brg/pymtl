#=========================================================================
# verilog_structural.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

import re
import sys
import collections

from ..signals import InPort, OutPort, Constant

#-------------------------------------------------------------------------
# header
#-------------------------------------------------------------------------
def header( model, symtab ):
  s    = title_bar.format( model.class_name )
  for name, value in model._args.items():
    value_str = '{}'.format( value )
    if 'instance at' in value_str:
      value_str = value_str.split(' at')[0] + '>'
    s += '// {}: {}'.format( name, value_str ) + endl
  s   += net_none + endl
  return s

#-------------------------------------------------------------------------
# port_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for port declarations.
def port_declarations( model, symtab ):
  if not model.get_ports(): return ''
  port_list = [ port_decl( x ) for x in model.get_ports() ]
  s  = start_ports + endl
  s += port_delim.join( port_list ) + endl
  s += end_ports + endl
  s += endl
  return s

#------------------------------------------------------------------------
# wire_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for wire declarations.
def wire_declarations( model, symtab ):
  if not model.get_wires(): return ''
  regs = symtab[0]
  wires = [ wire_decl( x ) for x in model.get_wires() if x not in regs ]
  if not wires: return ''
  s  = '  // wire declarations' + endl
  s += wire_delim.join( wires ) + wire_delim + endl
  s += endl
  return s

#-------------------------------------------------------------------------
# submodel_instances
#-------------------------------------------------------------------------
# Generate Verilog source for submodel instances.
def submodel_instances( model, symtab ):

  if not model.get_submodules(): return ''
  regs = symtab[0]

  s = ''
  for submodel in model.get_submodules():

    # Create strings for port connections
    submodel_name = mangle_name( submodel.name )
    temporaries = []
    connections = []
    for p in submodel.get_ports():
      port_name = mangle_name( p.name )
      temp_name = signal_to_str( p, None, model )

      # TODO: not needed since declared in create_declarations
      #if p in regs:
      #  regs.remove(p)
      #  temporaries.append( reg_to_str( p, None, model ) )
      if p not in regs:
        temporaries.append( wire_to_str( p, None, model ) )

      connections.append( connection.format( port_name, temp_name ) )

    connections = pretty_align( connections, '(' )

    # Print the temporaries
    s += '  // {} temporaries'.format( submodel_name ) + endl
    s += wire_delim.join( temporaries ) + wire_delim + endl

    # Print the submodule instantiation
    s += instance.format( submodel.class_name, submodel_name ) + endl
    s += tab + start_ports + endl
    s += port_delim.join( connections ) + endl
    s += tab + end_ports + endl
    s += endl

  return s

#-------------------------------------------------------------------------
# signal_assignments
#-------------------------------------------------------------------------
# Generate Verilog source for signal connections.
def signal_assignments( model, symtab ):
  if not model.get_connections(): return ''

  # Create all the assignment statements
  assignment_list = []
  for c in model.get_connections():
    dest = signal_to_str( c.dest_node, c.dest_slice, model )
    src  = signal_to_str( c.src_node,  c.src_slice,  model )
    assignment_list.append( assignment.format( dest, src ) )

  assignment_list = pretty_align( assignment_list, '=' )
  # Print them in alphabetically sorted order (prettier)
  s  = '  // signal connections' + endl
  s += endl.join( sorted( assignment_list ) )
  s += endl

  return s

#-------------------------------------------------------------------------
# verilog
#-------------------------------------------------------------------------
tab         = '  '
endl        = '\n'
div         = '//' + '-'*77
comment     = '// {}'
net_none    = '`default_nettype none'
net_wire    = '`default_nettype wire'
title_bar   = div + endl + comment + endl + div + endl
start_mod   = 'module {}'
end_mod     = 'endmodule // {}' + endl + net_wire
start_ports = '('
end_ports   = ');'
instance    = tab + '{} {}'
connection  = tab + tab + '.{} ( {} )'
signal_decl = tab + '{:6} [{:4}:0] {}'
port_delim  = ',' + endl
wire_delim  = ';' + endl
assignment  = tab + 'assign {} = {};'

#-------------------------------------------------------------------------
# port_decl
#-------------------------------------------------------------------------
def port_decl( port ):

  if   isinstance( port, InPort ):
    type_ = 'input'
  elif isinstance( port, OutPort ):
    type_ = 'output'

  nbits = port.nbits - 1
  name  = mangle_name( port.name )

  return signal_decl.format( type_, nbits, name )

#-------------------------------------------------------------------------
# wire_decl
#-------------------------------------------------------------------------
def wire_decl( port ):

  type_ = 'wire'
  nbits = port.nbits - 1
  name  = mangle_name( port.name )

  return signal_decl.format( type_, nbits, name )

#-------------------------------------------------------------------------
# pretty_align
#-------------------------------------------------------------------------
def pretty_align( assignment_list, char ):
  split = [ x.split( char ) for x in assignment_list ]
  pad   = max( [len(x) for x,y in split] )
  return [ "{0:<{1}}{2}{3}".format( x, pad, char, y ) for x,y in split ]

#-------------------------------------------------------------------------
# wire_to_str
#-------------------------------------------------------------------------
# utility function
# TODO: replace
def wire_to_str( port, slice_=None, parent=None ):
  return '  wire   [{:4}:0] {}'.format( port.nbits-1,
                                signal_to_str( port, slice_, parent ) )

#-------------------------------------------------------------------------
# reg_to_str
#-------------------------------------------------------------------------
def reg_to_str( port, slice_=None, parent=None ):
  return '  reg    [{:4}:0] {}'.format( port.nbits-1,
                                signal_to_str( port, slice_, parent ) )

#-------------------------------------------------------------------------
# mangle_name
#-------------------------------------------------------------------------
def mangle_name( name ):
  # Utility function
  def replacement_string( m ):
    return "${:03d}".format( int(m.group('idx')) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name.replace('.','_') )

# Regex to match list indexing
indexing = re.compile("(\[)(?P<idx>.*?)(\])")

#-------------------------------------------------------------------------
# signal_to_str
#-------------------------------------------------------------------------
# TODO: clean this up
def signal_to_str( node, addr, context ):

  # Special case constants
  if isinstance( node, Constant ): return node.name

  # If the node's parent module isn't the same as the current module
  # we need to prefix the signal name with the module name
  prefix = ''
  if node.parent != context and node.parent != None:
    prefix = '{}$'.format( mangle_name( node.parent.name ) )

  # If this is a slice, we need to provide the slice indexing
  suffix = ''
  if isinstance( addr, slice ):
    suffix = '[{}:{}]'.format( addr.stop - 1, addr.start )
  elif isinstance( addr, int ):
    suffix = '[{}]'.format( addr )

  # Return the string
  return prefix + mangle_name( node.name ) + suffix


#-------------------------------------------------------------------------
# create_declarations
#-------------------------------------------------------------------------
# TODO: clean this up!
def create_declarations( model, regs, ints, params, arrays ):

  scode = ''

  # Print the reg declarations
  if regs:
    scode += '  // register declarations\n'
    regs = sorted( regs,
                   key=lambda x: x[0] if isinstance(x,tuple)
                                      else signal_to_str( x, None, model ) )

    for signal in regs:
      if isinstance( signal, tuple ):
        scode += '  integer {};\n'.format( signal[0] );
      else:
        scode += '  reg    [{:4}:0] {};\n'.format( signal.nbits-1,
            signal_to_str( signal, None, model ))
    scode += '\n'

  # Print the localparam declarations
  if params:
    params = sorted( params, key=lambda x: x[0] )
    scode += '  // localparam declarations\n'
    for param, value in params:
      rhs    = "{}'d{}".format( value.nbits, value.uint() ) \
               if hasattr( value, 'nbits' ) else \
               "{}"    .format( value )
      scode += '  localparam {} = {};\n'.format( param, rhs )
    scode += '\n'

  # Print the int declarations
  if ints:
    ints = sorted( ints )
    scode += '  // loop variable declarations\n'
    for signal in ints:
      scode += '  integer {};\n'.format( signal )
    scode += '\n'

  # Print the array declarations
  if arrays:
    arrays = sorted( arrays, key=lambda x: x[0] )
    scode += '  // array declarations\n'
    for name, ports in arrays:
      # Output Port
      if isinstance( ports[0], OutPort ):
        scode += '  reg    [{:4}:0] {}[0:{}];\n'.format(
            ports[0].nbits-1, name, len(ports)-1)
        for i, port in enumerate(ports):
          scode += '  assign {0} = {1}[{2:3}];\n'.format(
              signal_to_str( port, None, model ), name, i )
      # Input Port
      elif isinstance( ports[0], InPort ):
        scode += '  wire   [{:4}:0] {}[0:{}];\n'.format(
            ports[0].nbits-1, name, len(ports)-1)
        for i, port in enumerate(ports):
          scode += '  assign {1}[{2:3}] = {0};\n'.format(
              signal_to_str( port, None, model ), name, i )
      # TODO: for Wires, we should really be sensing if
      #       they are written or not to determine the
      #       array declaration.
      else:
        scode += '  reg    [{:4}:0] {}[0:{}];\n'.format(
            ports[0].nbits-1, name, len(ports)-1)
        for i, port in enumerate(ports):
          scode += '  assign {0} = {1}[{2:3}];\n'.format(
              signal_to_str( port, None, model ), name, i )
    scode += '\n'

  return scode
