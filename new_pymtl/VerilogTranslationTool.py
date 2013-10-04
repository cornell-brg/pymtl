#=========================================================================
# VerilogTranslationTool.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

from Model import *
import sys
import re

import inspect
#from   translate_logic import PyToVerilogVisitor
#from   translate_logic import FindRegistersVisitor
#from   translate_logic import TemporariesVisitor

#------------------------------------------------------------------------
# Verilog Translation Tool
#-------------------------------------------------------------------------

class VerilogTranslationTool(object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  # Generates Verilog source from a PyMTL model.
  def __init__(self, model, o=sys.stdout):

    # List of models to translate
    translation_queue = []

    # Utility function to recursively collect all submodels in design
    def collect_all_models( m ):
      # Add the model to the queue
      if m not in translation_queue:
        translation_queue.append( m )

      for subm in m.get_submodules():
        collect_all_models( subm )

    # Collect all submodels in design and translate them
    collect_all_models( model )
    for m in translation_queue:
      translate_module( m, o )

#------------------------------------------------------------------------
# translate_module
#-------------------------------------------------------------------------
def translate_module( model, o ):

  start_module      ( model, o )
  port_declarations ( model, o )
  wire_declarations ( model, o )
  submodel_instances( model, o )
  signal_connections( model, o )
  end_module        ( model, o )

#------------------------------------------------------------------------
# start_module
#-------------------------------------------------------------------------
def start_module( model, o ):

  # Module declaration
  print >> o, '//-{}'.format( 71*'-' )
  print >> o, '// {}'.format( model.class_name )
  print >> o, '//-{}'.format( 71*'-' )
  print >> o, 'module {}'.format( model.class_name )

#------------------------------------------------------------------------
# port_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for port declarations.
def port_declarations( model, o ):

  # utility function
  def port_to_str( port ):
    direction = 'input'  if isinstance( port, InPort ) else 'output'
    return '  {:6} [{:4}:0] {}'.format( direction, port.nbits-1,
                                        mangle_name( port.name ) )

  print >> o, '('
  for p in model.get_ports()[:-1]: print >> o, port_to_str( p ) + ','
  for p in model.get_ports()[-1:]: print >> o, port_to_str( p )
  print >> o, ');'
  print >> o

#------------------------------------------------------------------------
# wire_declarations
#-------------------------------------------------------------------------
# Generate Verilog source for wire declarations.
def wire_declarations( model, o ):

  if not model.get_wires(): return

  print >> o, '  // wire declarations'
  for p in model.get_wires(): print >> o, wire_to_str( p ) + ';'
  print >> o

#------------------------------------------------------------------------
# signal_connections
#-------------------------------------------------------------------------
# Generate Verilog source for signal.
def signal_connections( model, o ):

  if not model.get_connections(): return


  # Create all the assignment statements
  connection_list = []
  for c in model.get_connections():
    dest = signal_to_str( c.dest_node, c.dest_slice, model )
    src  = signal_to_str( c.src_node,  c.src_slice,  model )
    connection_list.append( '  assign {} = {};'.format( dest, src ) )

  # Print them in alphabetically sorted order (prettier)
  print >> o, '  // signal connections'
  for c in sorted( connection_list ): print >> o, c
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
    wires = []
    ports = []
    for p in submodel.get_ports():
      port_name = mangle_name( p.name )
      temp_name = submodel_name + '$' + port_name
      wires.append( wire_to_str( p, None, model ) )
      ports.append( '    .{} ({})'.format( port_name, temp_name ) )

    # Print the submodule instantiation
    for w in wires: print >> o, w + ';'
    print >> o
    print >> o, '  {} {}'.format( submodel.class_name, submodel_name )
    print >> o, '  ('
    for p in ports[:-1]: print >> o, p + ','
    for p in ports[-1:]: print >> o, p
    print >> o, '  );'
    print >> o

#------------------------------------------------------------------------
# end_module
#-------------------------------------------------------------------------
def end_module( model, o ):
  print >> o, 'endmodule // {}'.format( model.class_name )
  print >> o

#------------------------------------------------------------------------
# wire_to_str
#-------------------------------------------------------------------------
# utility function
def wire_to_str( port, slice_=None, parent=None ):
  return '  wire   [{:4}:0] {}'.format( port.nbits-1,
                                signal_to_str( port, slice_, parent ) )

#------------------------------------------------------------------------
# mangle_name
#-------------------------------------------------------------------------
def mangle_name( name ):
  # Utility function
  def replacement_string( m ):
    return "${:03d}".format( int(m.group(2)) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name )

# Regex to match list indexing
indexing = re.compile("(\[)(.*)(\])")

# Utility function
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
