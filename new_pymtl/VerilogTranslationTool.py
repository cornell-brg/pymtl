#=========================================================================
# VerilogTranslationTool.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

from Model import *

import re
import sys
import collections

from VerilogLogicTransl import translate_logic_blocks

#-------------------------------------------------------------------------
# VerilogTranslationTool
#-------------------------------------------------------------------------
class VerilogTranslationTool(object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  # Generates Verilog source from a PyMTL model.
  def __init__(self, model, o=sys.stdout):

    # List of models to translate
    translation_queue = collections.OrderedDict()

    # Utility function to recursively collect all submodels in design
    def collect_all_models( m ):
      # Add the model to the queue
      translation_queue[ m.class_name ] = m

      for subm in m.get_submodules():
        collect_all_models( subm )

    # Collect all submodels in design and translate them
    collect_all_models( model )
    for k, v in translation_queue.items():
      translate_module( v, o )

#-------------------------------------------------------------------------
# translate_module
#-------------------------------------------------------------------------
def translate_module( model, o ):

  print >> o, header   .format( model.class_name )
  print >> o, start_mod.format( model.class_name )

  # Structural Verilog
  port_declarations ( model, o )
  wire_declarations ( model, o )
  submodel_instances( model, o )
  signal_assignments( model, o )

  # Behavioral Verilog
  translate_logic_blocks( model, o )

  print >> o, end_mod  .format( model.class_name )
  print >> o

#-------------------------------------------------------------------------
# port_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for port declarations.
def port_declarations( model, o ):
  if not model.get_ports(): return
  port_list = [ port_decl( x ) for x in model.get_ports() ]
  print >> o, start_ports
  print >> o, port_delim.join( port_list )
  print >> o, end_ports
  print >> o

#------------------------------------------------------------------------
# wire_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for wire declarations.
def wire_declarations( model, o ):
  if not model.get_wires(): return
  wires = [ wire_decl( x ) for x in model.get_wires() ]
  print >> o, '  // wire declarations'
  print >> o, wire_delim.join( wires ) + wire_delim
  print >> o

#-------------------------------------------------------------------------
# submodel_instances
#-------------------------------------------------------------------------
# Generate Verilog source for submodel instances.
def submodel_instances( model, o ):

  if not model.get_submodules(): return

  for submodel in model.get_submodules():

    # Create strings for port connections
    submodel_name = mangle_name( submodel.name )
    temporaries = []
    connections = []
    for p in submodel.get_ports():
      port_name = mangle_name( p.name )
      temp_name = signal_to_str( p, None, model )
      temporaries.append( wire_to_str( p, None, model ) )
      connections.append( connection.format( port_name, temp_name ) )

    connections = pretty_align( connections, '(' )
    # Print the submodule instantiation
    print >> o, '  // {} temporaries'.format( submodel_name )
    print >> o, wire_delim.join( temporaries ) + wire_delim
    print >> o, instance.format( submodel.class_name, submodel_name )
    print >> o, tab + start_ports
    print >> o, port_delim.join( connections )
    print >> o, tab + end_ports
    print >> o

#-------------------------------------------------------------------------
# signal_assignments
#-------------------------------------------------------------------------
# Generate Verilog source for signal connections.
def signal_assignments( model, o ):
  if not model.get_connections(): return

  # Create all the assignment statements
  assignment_list = []
  for c in model.get_connections():
    dest = signal_to_str( c.dest_node, c.dest_slice, model )
    src  = signal_to_str( c.src_node,  c.src_slice,  model )
    assignment_list.append( assignment.format( dest, src ) )

  assignment_list = pretty_align( assignment_list, '=' )
  # Print them in alphabetically sorted order (prettier)
  print >> o, '  // signal connections'
  print >> o, endl.join( sorted( assignment_list ) )
  print >> o

#------------------------------------------------------------------------
# verilog
#-------------------------------------------------------------------------
tab         = '  '
endl        = '\n'
div         = '//' + '-'*72
comment     = '// {}'
header      = div + endl + comment + endl + div
start_mod   = 'module {}'
end_mod     = 'endmodule // {}'
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
# mangle_name
#-------------------------------------------------------------------------
def mangle_name( name ):
  # Utility function
  def replacement_string( m ):
    return "${:03d}".format( int(m.group(2)) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name.replace('.','_') )

# Regex to match list indexing
indexing = re.compile("(\[)(.*)(\])")

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
    prefix = '{}$'.format( node.parent.name )

  # If this is a slice, we need to provide the slice indexing
  suffix = ''
  if isinstance( addr, slice ):
    suffix = '[{}:{}]'.format( addr.stop - 1, addr.start )
  elif isinstance( addr, int ):
    suffix = '[{}]'.format( addr )

  # Return the string
  return prefix + mangle_name( node.name ) + suffix

