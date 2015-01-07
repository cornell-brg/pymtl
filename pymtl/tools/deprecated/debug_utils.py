#=======================================================================
# debug_utils.py
#=======================================================================
# Collection of utility functions used for debugging models.

from __future__ import print_function

import ...model.Model as model
import sys
import ast, _ast
import functools

def port_walk(tgt, spaces=0, o=sys.stdout):

  printn = functools.partial( print, file=o )
  printl = functools.partial( print, file=o, end='' )

  pw = tgt._ports + tgt._wires
  for x in pw:
    printn( spaces*' ', x.parent.name, x.name, x )
    for y in x.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      printn( spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname) )
    printl( spaces*' ', '   value:', x._value, #x.value )
    if isinstance(x._value, model.Slice):
      # TODO: handle this case in VerilogSlice instead?
      if x._value._value:
        printn( x.value )
      else:
        printn( None )
      printn((spaces+1)*' ', '   slice:', x._value._value, bin(x._value.pmask))
    # TODO: handle this case in VerilogSlice instead?
    else:
      printn( x.value )
  printn()
  for x in tgt._submodules:
    printn( spaces*' ', x.name )
    port_walk(x, spaces+3, o)

def print_connections(tgt, spaces=0, o=sys.stdout):
  pw = tgt._ports + tgt._wires
  for x in pw:
    printn( spaces*' ', x.parent.name, x.name, x )
    for y in x.node.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      printn( spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname) )
    printn( spaces*' ', '   value:', x.value )
    if isinstance(x.node, model.Slice):
    #  # TODO: handle this case in VerilogSlice instead?
    #  printn( x.value )
      printn( (spaces+1)*' ', '   slice:', x.value #, bin(x._value.pmask) )
    ## TODO: handle this case in VerilogSlice instead?
    #else:
    #  printn( x.value )
  printn()
  for x in tgt._submodules:
    printn( spaces*' ', x.name )
    port_walk(x, spaces+3, o)

port_walk = print_connections

def print_ast(ast_tree):
  """Debug utility which prints the provided AST tree."""
  printn( "="*35, "BEGIN AST", "="*35 )
  PrintVisitor().visit( ast_tree )
  printn( "="*35, " END AST ", "="*35 )

class PrintVisitor(ast.NodeVisitor):

  """AST Visitor class used by print_ast()."""

  def __init__(self):
    self.indent = 0

  def generic_visit(self, node):

    #off = "??"
    #if hasattr(node, 'col_offset'):
    #  off = node.col_offset
    #printl( "{0:2}".format(off) )
    if isinstance(node, _ast.FunctionDef):
      printl( "FUNCTIONDEF:" )
    elif isinstance(node, _ast.arguments):
      printl( "ARGUMENTS:  " )
    elif isinstance(node, _ast.Assign):
      printl( "ASSIGN:     " )
    elif isinstance(node, _ast.If):
      printl( "IFELSE: {0:4}".format(node.lineno) )
    else:
      printl( "            " )

    printl( self.indent*' ', node )

    if isinstance(node, _ast.Module):
      print( node.body )
    elif isinstance(node, _ast.FunctionDef):
      print( node.name, "FIXME" )
      #print( node.name, [('@'+x.id, x) for x in node.decorator_list] )
    elif isinstance(node, _ast.Name):
      print( node.id, "-----", type( node.ctx ) )
    elif isinstance(node, _ast.Attribute):
      print( node.attr, "-----", type( node.ctx ) )
    elif isinstance(node, _ast.Assign):
      print( node.targets, ' = ', node.value )
    elif isinstance(node, _ast.AugAssign):
      print( node.op )
    elif isinstance(node, _ast.Call):
      print( node.func )
    elif isinstance(node, _ast.arguments):
      print( node.args )
    elif isinstance(node, _ast.If):
      print( node.test, node.body, node.orelse )
    elif isinstance(node, _ast.Subscript):
      #print( node.value )
      #print( type(node.slice)#, '=>', type(node.slice.value) )
      print( type(node.slice), "-----", type( node.ctx ) )
    else:
      printl( node._attributes )
      print


    self.indent += 3

    for item in ast.iter_child_nodes(node):
      self.visit(item)
    #for field, value in ast.iter_fields(node):
    #  if isinstance(value, list):
    #    for item in value:
    #      if isinstance(item, ast.AST):
    #        self.visit(item)
    #  elif isinstance(value, ast.AST):
    #    self.visit(value)

    self.indent -= 3
