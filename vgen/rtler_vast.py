import ast

class PyToVerilogVisitor(ast.NodeVisitor):
  opmap = {
      ast.Add      : '+',
      ast.Sub      : '-',
      ast.Mult     : '*',
      ast.Div      : '/',
      ast.Mod      : '%',
      ast.Pow      : '**',
      ast.LShift   : '<<',
      ast.RShift   : '>>>',
      ast.BitOr    : '|',
      ast.BitAnd   : '&',
      ast.BitXor   : '^',
      ast.FloorDiv : '/',
      ast.Invert   : '~',
      ast.Not      : '!',
      ast.UAdd     : '+',
      ast.USub     : '-',
      ast.Eq       : '==',
      ast.Gt       : '>',
      ast.GtE      : '>=',
      ast.Lt       : '<',
      ast.LtE      : '<=',
      ast.NotEq    : '!=',
      ast.And      : '&&',
      ast.Or       : '||',
  }

  def __init__(self, o):
    self.write_names = False
    self.o = o

  def visit_FunctionDef(self, node):
    """ Only parse functions that have the @always_comb decorator! """
    #print node.name, node.decorator_list
    if not node.decorator_list:
      return
    if node.decorator_list[0].id == 'always_comb':
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)

  def visit_BinOp(self, node):
    """ Place parens around every operator with args to ensure order
        of operations are preserved.
    """
    print >> self.o, '(',
    self.visit(node.left)
    print PyToVerilogVisitor.opmap[type(node.op)],
    self.visit(node.right)
    print >> self.o, ')',

  def visit_BoolOp(self, node):
    print 'Found BoolOp "%s"' % node.op

  def visit_UnaryOp(self, node):
    print 'Found UnaryOp "%s"' % node.op

  #def visit_Num(self, node):
  #  print 'Found Num', node.n

  def visit_AugAssign(self, node):
    """ Turn <<= symbols into assign statements. """
    # TODO: this turns all comparisons into assign statements! Fix!
    self.write_names = True
    print >> self.o, '  assign', node.target.id, '=',
    self.visit(node.value)
    print >> self.o, ';'
    self.write_names = False

  #def visit_LtE(self, node):
  #def visit_Compare(self, node):
  #  """ Turn <= symbols into assign statements. """
  #  # TODO: this turns all comparisons into assign statements! Fix!
  #  print >> self.o, '  assign', node.left.id, '=',
  #  self.visit(node.comparators[0])
  #  print >> self.o, ';'

  def visit_Name(self, node):
    if self.write_names: print >> self.o, node.id,

