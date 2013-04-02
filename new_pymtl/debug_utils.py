#=========================================================================
# debug_utils.py
#=========================================================================
# Collection of utility functions used for debugging the PyMTL framework.

import Model as model
import sys
import ast, _ast

def port_walk(tgt, spaces=0, o=sys.stdout):
  pw = tgt._ports + tgt._wires
  for x in pw:
    print >> o, spaces*' ', x.parent.name, x.name, x
    for y in x.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      print >> o, spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname)
    print >> o, spaces*' ', '   value:', x._value, #x.value
    if isinstance(x._value, model.Slice):
      # TODO: handle this case in VerilogSlice instead?
      if x._value._value:
        print >> o, x.value
      else:
        print >> o, None
      print >> o, (spaces+1)*' ', '   slice:', x._value._value, bin(x._value.pmask)
    # TODO: handle this case in VerilogSlice instead?
    else:
      print >> o, x.value
  print >> o
  for x in tgt._submodules:
    print >> o, spaces*' ', x.name
    port_walk(x, spaces+3, o)

def print_connections(tgt, spaces=0, o=sys.stdout):
  pw = tgt._ports + tgt._wires
  for x in pw:
    print >> o, spaces*' ', x.parent.name, x.name, x
    for y in x.node.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      print >> o, spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname)
    print >> o, spaces*' ', '   value:', x.value
    if isinstance(x.node, model.Slice):
    #  # TODO: handle this case in VerilogSlice instead?
    #  print >> o, x.value
      print >> o, (spaces+1)*' ', '   slice:', x.value #, bin(x._value.pmask)
    ## TODO: handle this case in VerilogSlice instead?
    #else:
    #  print >> o, x.value
  print >> o
  for x in tgt._submodules:
    print >> o, spaces*' ', x.name
    port_walk(x, spaces+3, o)

port_walk = print_connections

def print_ast(ast_tree):
  """Debug utility which prints the provided AST tree."""
  print "="*35, "BEGIN AST", "="*35
  PrintVisitor().visit( ast_tree )
  print "="*35, " END AST ", "="*35

class PrintVisitor(ast.NodeVisitor):

  """AST Visitor class used by print_ast()."""

  def __init__(self):
    self.indent = 0

  def generic_visit(self, node):

    #off = "??"
    #if hasattr(node, 'col_offset'):
    #  off = node.col_offset
    #print "{0:2}".format(off),
    if isinstance(node, _ast.FunctionDef):
      print "FUNCTIONDEF:",
    elif isinstance(node, _ast.arguments):
      print "ARGUMENTS:  ",
    elif isinstance(node, _ast.Assign):
      print "ASSIGN:     ",
    elif isinstance(node, _ast.If):
      print "IFELSE: {0:4}".format(node.lineno),
    else:
      print "            ",

    print self.indent*' ', node,

    if isinstance(node, _ast.Module):
      print node.body
    elif isinstance(node, _ast.FunctionDef):
      print node.name, "FIXME"
      #print node.name, [('@'+x.id, x) for x in node.decorator_list]
    elif isinstance(node, _ast.Name):
      print node.id, "-----", type( node.ctx )
    elif isinstance(node, _ast.Attribute):
      print node.attr, "-----", type( node.ctx )
    elif isinstance(node, _ast.Assign):
      print node.targets, ' = ', node.value
    elif isinstance(node, _ast.AugAssign):
      print node.op
    elif isinstance(node, _ast.Call):
      print node.func
    elif isinstance(node, _ast.arguments):
      print node.args
    elif isinstance(node, _ast.If):
      print node.test, node.body, node.orelse
    elif isinstance(node, _ast.Subscript):
      #print node.value
      #print type(node.slice)#, '=>', type(node.slice.value)
      print type(node.slice), "-----", type( node.ctx )
    else:
      print node._attributes,
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
