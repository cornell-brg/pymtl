import pymtl_model
import sys
import ast, _ast

def port_walk(tgt, spaces=0, o=sys.stdout):
  for x in tgt._ports:
    print >> o, spaces*' ', x.parent.name, x
    for y in x.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      print >> o, spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname)
    print >> o, spaces*' ', '   value:', x._value, #x.value
    if isinstance(x._value, pymtl_model.Slice):
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

    if isinstance(node, _ast.FunctionDef):
      print "FUNCTIONDEF:",
    elif isinstance(node, _ast.arguments):
      print "ARGUMENTS:  ",
    elif isinstance(node, _ast.Assign):
      print "ASSIGN:     ",
    else:
      print "            ",

    print self.indent*' ', node,

    if isinstance(node, _ast.Module):
      print node.body
    elif isinstance(node, _ast.FunctionDef):
      print node.name, [('@'+x.id, x) for x in node.decorator_list]
    elif isinstance(node, _ast.Name):
      print node.id
    elif isinstance(node, _ast.Attribute):
      print node.attr
    elif isinstance(node, _ast.Assign):
      print node.targets, ' = ', node.value
    elif isinstance(node, _ast.AugAssign):
      print node.op
    elif isinstance(node, _ast.Call):
      print node.func
    elif isinstance(node, _ast.arguments):
      print node.args
    else:
      print node._attributes,
      print


    self.indent += 3


    for field, value in ast.iter_fields(node):
      if isinstance(value, list):
        for item in value:
          if isinstance(item, ast.AST):
            self.visit(item)
      elif isinstance(value, ast.AST):
        self.visit(value)

    self.indent -= 3
