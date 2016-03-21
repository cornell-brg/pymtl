#=======================================================================
# verilog_structural.py
#=======================================================================
# Tool to translate PyMTL Models into Verilog HDL.

import re
import sys
import collections

from ...model.signals      import Signal, InPort, OutPort, Wire, Constant
from ...model.signal_lists import PortList, WireList
from exceptions            import VerilogTranslationError

#-----------------------------------------------------------------------
# header
#-----------------------------------------------------------------------
def header( model, symtab, enable_blackbox=False, verilator_xinit='zeros' ):
  # black box with custom module name
  if enable_blackbox and model.vbb_modulename != "":
    s = title_bar.format( model.vbb_modulename )
  else:
    s = title_bar.format( model.class_name )

  for name, value in model._args.items():
    value_str = '{}'.format( value )
    if 'instance at' in value_str:
      value_str = value_str.split(' at')[0] + '>'
    s += '// {}: {}'.format( name, value_str ) + endl

  dump_vcd = hasattr( model, 'vcd_file' ) and model.vcd_file != ''
  s   += '// dump-vcd: {}'.format( dump_vcd ) + endl

  s += '// verilator-xinit: {}'.format( verilator_xinit ) + endl

  if enable_blackbox:
    if model.vblackbox:
      s += '// This module is treated as a black box' + endl

  if model.vannotate_arrays:
    s += '// vannotate_arrays has annotated: {}'.format(
        str(model.vannotate_arrays.keys()) ) + endl

  if model.vmark_as_bram:
    s += '// vmark_as_bram: True' + endl

  s   += net_none + endl
  return s

#-----------------------------------------------------------------------
# port_declarations
#-----------------------------------------------------------------------
# Generate Verilog source for port declarations.
def port_declarations( model, symtab, enable_blackbox=False ):
  if not model.get_ports(): return ''
  regs = symtab[0]
  for port in model.get_ports():
    port._is_reg = port in regs
    if port._is_reg: regs.remove( port )

  sorted_ports = sorted( model.get_ports(), key=lambda x: x.name )

  # for black boxes, remove clk or reset if necessary
  if enable_blackbox and model.vblackbox:
    if model.vbb_no_reset:
      sorted_ports = [ p for p in sorted_ports if p.name != 'reset' ]
    if model.vbb_no_clk:
      sorted_ports = [ p for p in sorted_ports if p.name != 'clk'   ]

  port_list = [ port_decl( x ) for x in sorted_ports ]
  s  = start_ports + endl
  s += port_delim.join( port_list ) + endl
  s += end_ports + endl
  s += endl
  return s

#------------------------------------------------------------------------
# wire_declarations
#-----------------------------------------------------------------------
# Generate Verilog source for wire declarations.
def wire_declarations( model, symtab ):
  if not model.get_wires(): return ''
  regs = symtab[0]
  wires = [ wire_decl( x ) for x in model.get_wires() if x not in regs ]
  if not wires: return ''
  s  = '  // wire declarations' + endl

  # Generate declarations
  gen_declarations = not model.vmark_as_bram # unless marked as BRAM
  if gen_declarations:
    s += wire_delim.join( wires ) + wire_delim + endl

  s += endl
  return s

#-----------------------------------------------------------------------
# submodel_instances
#-----------------------------------------------------------------------
# Generate Verilog source for submodel instances.
def submodel_instances( model, symtab, enable_blackbox=False ):

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

      # if submodel is a black box, then remove reset and/or clk
      # if necessary

      if enable_blackbox and submodel.vblackbox:
        if submodel.vbb_no_reset and p.name == 'reset':
          continue
        if submodel.vbb_no_clk   and p.name == 'clk':
          continue

      connections.append( connection.format( port_name, temp_name ) )

    connections = pretty_align( connections, '(' )

    # Print the temporaries
    s += '  // {} temporaries'.format( submodel_name ) + endl
    s += wire_delim.join( temporaries ) + wire_delim + endl

    # Print the submodule instantiation
    if enable_blackbox and submodel.vbb_modulename != "":
      s += instance.format( submodel.vbb_modulename, submodel_name ) + endl
    else:
      s += instance.format( submodel.class_name, submodel_name ) + endl
    s += tab + start_ports + endl
    s += port_delim.join( connections ) + endl
    s += tab + end_ports + endl
    s += endl

  return s

#-----------------------------------------------------------------------
# signal_assignments
#-----------------------------------------------------------------------
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

#-----------------------------------------------------------------------
# verilog
#-----------------------------------------------------------------------
tab         = '  '
endl        = '\n'
div         = '//' + '-'*77
comment     = '// {}'
net_none    = '`default_nettype none'
net_wire    = '`default_nettype wire'
title_bar   = div + endl + comment + endl + div + endl
start_mod   = 'module {}'
end_mod     = 'endmodule // {}' + endl + net_wire
start_param = '#('
end_param   = ')'
start_ports = '('
end_ports   = ');'
instance    = tab + '{} {}'
connection  = tab + tab + '.{} ( {} )'
nbits_decl  = '[{:4}:0]'
onebit_decl = ' '*len(nbits_decl.format(0))
ioport_decl = tab + '{:6} {:4} {} {}'
signal_decl = tab + '{:6} {} {}'
port_delim  = ',' + endl
wire_delim  = ';' + endl
assignment  = tab + 'assign {} = {};'
def declare_bitwidth( nbits ):
  # TODO: need to figure out a way to detect when single-bit wires are
  #       array indexed to make this swap!
  #return nbits_decl.format( nbits ) if nbits else onebit_decl
  return nbits_decl.format( nbits )

#-----------------------------------------------------------------------
# port_decl
#-----------------------------------------------------------------------
def port_decl( port ):

  if   isinstance( port, InPort ):
    direction = 'input'
  elif isinstance( port, OutPort ):
    direction = 'output'

  type_ = 'reg' if port._is_reg else 'wire'
  nbits = port.nbits - 1
  name  = mangle_name( port.name )

  return ioport_decl.format( direction, type_, declare_bitwidth(nbits), name )

#-----------------------------------------------------------------------
# wire_decl
#-----------------------------------------------------------------------
def wire_decl( port ):

  type_ = 'wire'
  nbits = port.nbits - 1
  name  = mangle_name( port.name )

  return signal_decl.format( type_, declare_bitwidth(nbits), name )

#-----------------------------------------------------------------------
# pretty_align
#-----------------------------------------------------------------------
def pretty_align( assignment_list, char ):
  split = [ x.split( char ) for x in assignment_list ]
  pad   = max( [len(x) for x,y in split] )
  return [ "{0:<{1}}{2}{3}".format( x, pad, char, y ) for x,y in split ]

#-----------------------------------------------------------------------
# wire_to_str
#-----------------------------------------------------------------------
# utility function
# TODO: replace
def wire_to_str( port, slice_=None, parent=None ):
  return '  wire   {} {}'.format(
    declare_bitwidth(port.nbits-1),
    signal_to_str( port, slice_, parent )
  )

#-----------------------------------------------------------------------
# reg_to_str
#-----------------------------------------------------------------------
def reg_to_str( port, slice_=None, parent=None ):
  return '  reg    {} {}'.format(
    declare_bitwidth(port.nbits-1),
    signal_to_str( port, slice_, parent )
  )

#-----------------------------------------------------------------------
# mangle_name
#-----------------------------------------------------------------------
def mangle_name( name ):
  # Utility function
  def replacement_string( m ):
    return "${:03d}".format( int(m.group('idx')) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name.replace('.','_') )

# Regex to match list indexing
indexing = re.compile("(\[)(?P<idx>.*?)(\])")

#-----------------------------------------------------------------------
# signal_to_str
#-----------------------------------------------------------------------
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


#-----------------------------------------------------------------------
# create_declarations
#-----------------------------------------------------------------------
# TODO: clean this up!
def create_declarations( model, regs, ints, params, arrays ):

  scode = ''

  # Print the reg declarations
  if regs:
    scode += '  // register declarations\n'
    regs   = sorted( regs, key=lambda x: signal_to_str( x, None, model ) )

    for signal in regs:
      # If name also inferenced as an 'integer' type, declare as reg only
      if signal.parent == None and signal.name in ints:
        ints.remove( signal.name )
      scode += '  reg    [{:4}:0] {};\n' \
               .format( signal.nbits-1, signal_to_str( signal, None, model ))
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

  return scode

#-----------------------------------------------------------------------
# array_declarations
#-----------------------------------------------------------------------
def array_declarations( model, symtab ):

  if not symtab[-1]:
    return '\n'

  #---------------------------------------------------------------------
  # helper to generate arrays to output port assignments
  #---------------------------------------------------------------------
  def _gen_array_to_output( ports ):
    if isinstance( ports[0], (Wire,InPort,OutPort) ):

      # Annotate arrays if vannotate_arrays is available
      annotation = ''
      if model.vannotate_arrays:
        if ports.name in model.vannotate_arrays:
          annotation = model.vannotate_arrays[ports.name] + ' '

      stmts = '  {}reg    [{:4}:0] {}[0:{}];\n' \
              .format(annotation, ports[0].nbits-1, ports.name, len(ports)-1)

      # Generate declarations
      gen_declarations = not model.vmark_as_bram # unless marked as BRAM
      if gen_declarations:
        for i, port in enumerate(ports):
          stmts += '  assign {0} = {1}[{2:3}];\n' \
                   .format(signal_to_str(port, None, model), ports.name, i)

    elif isinstance( ports[0], (PortList,WireList) ):
      if not isinstance( ports[0][0], (Wire,InPort,OutPort) ):
        raise VerilogTranslationError(
          'Port lists with more than 2 dimenstions are not supported!'
        )
      stmts = '  reg    [{bw:4}:0] {name}[0:{sz0}][0:{sz1}];\n' \
              .format( bw   = ports[0][0].nbits-1,
                       name = ports.name,
                       sz0  = len(ports)-1,
                       sz1  = len(ports[0])-1 )
      for i, plist in enumerate(ports):
        for j, port in enumerate(plist):
          stmts += '  assign {0} = {1}[{2:3}][{3:3}];\n' \
                   .format(signal_to_str(port, None, model),
                           ports.name, i, j)

    else:
      raise VerilogTranslationError(
        'An internal error occured when translating array accesses!\n'
        'Expected a list of Wires or Ports, instead got: {}'
        .format( type(ports[0]) )
      )

    return stmts

  #---------------------------------------------------------------------
  # helper to generate input port to array assignments
  #---------------------------------------------------------------------
  def _gen_input_to_array( ports ):
    if isinstance( ports[0], (Wire,InPort,OutPort) ):
      stmts = '  wire   [{:4}:0] {}[0:{}];\n' \
              .format(ports[0].nbits-1, ports.name, len(ports)-1)
      for i, port in enumerate(ports):
        stmts += '  assign {1}[{2:3}] = {0};\n' \
                 .format(signal_to_str(port, None, model), ports.name, i)

    elif isinstance( ports[0], (PortList,WireList) ):
      if not isinstance( ports[0][0], (Wire,InPort,OutPort) ):
        raise VerilogTranslationError(
          'Port lists with more than 2 dimenstions are not supported!'
        )
      stmts = '  wire   [{bw:4}:0] {name}[0:{sz0}][0:{sz1}];\n' \
              .format( bw   = ports[0][0].nbits-1,
                       name = ports.name,
                       sz0  = len(ports)-1,
                       sz1  = len(ports[0])-1 )
      for i, plist in enumerate(ports):
        for j, port in enumerate(plist):
          stmts += '  assign {1}[{2:3}][{3:3}] = {0};\n' \
                   .format(signal_to_str(port, None, model),
                           ports.name, i, j)

    else:
      raise VerilogTranslationError(
        'An internal error occured when translating array accesses!\n'
        'Expected a list of Wires or Ports, instead got: {}'
        .format( type(ports[0]) )
      )
    return stmts

  #---------------------------------------------------------------------
  # print the array declarations
  #---------------------------------------------------------------------
  arrays = sorted( symtab[-1], key=lambda x: x.name )
  scode  = '  // array declarations\n'

  for ports in arrays:
    if ports.is_lhs: scode += _gen_array_to_output( ports )
    else:            scode += _gen_input_to_array ( ports )

  return scode + '\n'


