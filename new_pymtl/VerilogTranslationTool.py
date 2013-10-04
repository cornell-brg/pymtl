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

    start_module     ( model, o )
    port_declarations( model, o )
    port_connections ( model, o )
    end_module       ( model, o )

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
    return '  {:6} [{:3}:0] {}'.format( direction, port.nbits-1,
                                        mangle_name( port ) )

  print >> o, '('
  for p in model.get_ports()[:-1]: print >> o, port_to_str( p ) + ','
  for p in model.get_ports()[-1:]: print >> o, port_to_str( p )
  print >> o, ');'

#------------------------------------------------------------------------
# port_connections
#-------------------------------------------------------------------------
# Generate Verilog source for port declarations.
def port_connections( model, o ):

  # Utility function
  def signal_to_str( node, addr, context ):

    # Special case constants
    if isinstance( node, Constant ): return node.name

    # If the node's parent module isn't the same as the current module
    # we need to prefix the signal name with the module name
    prefix = ''
    if node.parent != context and node.parent != None:
      prefix = '{}_M_'.format( node.parent.name )

    # If this is a slice, we need to provide the slice indexing
    suffix = ''
    if isinstance( addr, slice ):
      suffix = '[{}:{}]'.format( addr.stop - 1, addr.start )
    elif isinstance( addr, int ):
      suffix = '[{}]'.format( addr )

    # Return the string
    return prefix + mangle_name( node ) + suffix

  print >> o, '  // port_connections'
  for c in model.get_connections():
    dest = signal_to_str( c.dest_node, c.dest_slice, model )
    src  = signal_to_str( c.src_node,  c.src_slice,  model )
    print >> o, '  assign {} = {};'.format( dest, src )
  print >> o

#------------------------------------------------------------------------
# end_module
#-------------------------------------------------------------------------
def end_module( model, o ):
  print >> o, 'endmodule // {}'.format( model.class_name )
  print >> o

#------------------------------------------------------------------------
# mangle_name
#-------------------------------------------------------------------------
def mangle_name( p ):
  # Utility function
  def replacement_string( m ):
    return "${:03d}".format( int(m.group(2)) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, p.name )

# Regex to match list indexing
indexing = re.compile("(\[)(.*)(\])")
