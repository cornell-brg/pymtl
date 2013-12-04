#=========================================================================
# verilog_behavioral.py
#=========================================================================

import ast, _ast
import collections
import inspect
import StringIO
import textwrap

from ..ast_helpers import get_method_ast, print_simple_ast
from ..signals     import InPort, OutPort

# TODO: HACKY
from verilog_structural import signal_to_str

import visitors

#-------------------------------------------------------------------------
# translate_logic_blocks
#-------------------------------------------------------------------------
def translate_logic_blocks( model, o ):

  blocks = ( model.get_posedge_clk_blocks()
           + model.get_combinational_blocks()
           + model.get_tick_blocks() )

  behavioral_code = StringIO.StringIO()

  # TODO: remove regs logic, move to own visitor that visits _ast.Store
  #       nodes!
  regs   = set()
  ints   = set()
  params = set()
  arrays = set()
  #temps = []

  for func in blocks:

    # Type Check the AST
    tree, src  = get_method_ast( func )
    print src
    new_tree   = ast_pipeline( tree, model, func )
    r,i,p,a    = visitors.GetRegsIntsParamsTempsArrays().get( new_tree )

    regs      |= r
    ints      |= i
    params    |= p
    arrays    |= a

    # Store the PyMTL source inline with the behavioral code
    block_code = ("  // PYMTL SOURCE:\n"
                  "  // {}\n\n").format( "\n  // ".join( src.splitlines()))

    # Print the Verilog translation
    visitor     = TranslateBehavioralVerilog()
    block_code += visitor.visit( new_tree )

    print >> behavioral_code, block_code

    # TODO: check for conflicts, ensure that signals are not written in
    #       two different behavioral blocks!

  # Print the reg declarations
  if regs:
    print   >> o, '  // register declarations'
    for signal in regs:
      print >> o, '  reg    [{:4}:0] {};'.format( signal.nbits-1,
          signal_to_str( signal, None, model ))

  # Print the parameter declarations
  if params:
    print   >> o, '  // param declarations'
    for param, value in params:
      print >> o, '  parameter {} = {};'.format( param, value )

  # Print the int declarations
  if ints:
    print   >> o, '  // loop variable declarations'
    for signal in ints:
      print >> o, '  integer {};'.format( signal )

  # Print the array declarations
  if arrays:
    print   >> o, '  // array declarations'
    for name, ports in arrays:
      # Output Port
      if isinstance( ports[0], OutPort ):
        print >> o, '  reg    [{:4}:0] {}[0:{}];'.format(
            ports[0].nbits-1, name, len(ports)-1)
        for i, port in enumerate(ports):
          print >> o, '  assign {0} = {1}[{2:3}];'.format(
              signal_to_str( port, None, model ), name, i )
      # Input Port
      else:
        print >> o, '  wire   [{:4}:0] {}[0:{}];'.format(
            ports[0].nbits-1, name, len(ports)-1)
        for i, port in enumerate(ports):
          print >> o, '  assign {1}[{2:3}] = {0};'.format(
              signal_to_str( port, None, model ), name, i )



  ## Print the temporary declarations
  ## TODO: this doesn't really work, need to set type of temp
  #if temps:
  #  print   >> o, '  // temporary declarations'
  #  for signal in temps:
  #    print >> o, '  reg {};'.format( signal )

  ## TODO: clean this up and move it somewhere else! Ugly!
  #print >> o
  #if array:
  #  print   >> o, '  // temporary arrays'
  #  for x in array:
  #    # declare the array
  #    nports = len( x )
  #    nbits  = x[0].nbits
  #    name   = x[0].name.split('[')[0]
  #    if   isinstance( x[0], InPort  ):
  #      print   >> o, '  wire   [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
  #      for i in range( nports ):
  #        print >> o, '  assign {0}[{1:3}] = {0}${1:03d};'.format( name, i )
  #    elif isinstance( x[0], OutPort ):
  #      print   >> o, '  reg    [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
  #      for i in range( nports ):
  #        print >> o, '  assign {0}${1:03d} = {0}[{1:3}];'.format( name, i )
  #    elif isinstance( x[0], Wire ):
  #      print   >> o, '  reg    [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
  #    else:
  #      raise Exception("Untranslatable array item!")

  ## Print the temporary declarations

  # Print the behavioral block code
  print >> o
  print >> o, behavioral_code.getvalue()

#-------------------------------------------------------------------------
# ast_pipeline
#-------------------------------------------------------------------------
# TODO:
# ? remove index nodes (replace with integer?)
# ? replace Subscript nodes with BitSlice if they reference a Bits
# ? replace Subscript nodes with ArrayIndex if they reference a list
# - flatten port bundles
# - flatten bitstructs
def ast_pipeline( tree, model, func ):

  print_simple_ast( tree ) # DEBUG

  tree = visitors.AnnotateWithObjects( model, func ).visit( tree )
  tree = visitors.RemoveModule       (             ).visit( tree )
  tree = visitors.SimplifyDecorator  (             ).visit( tree )
  tree = visitors.RemoveValueNext    (             ).visit( tree )
  tree = visitors.RemoveSelf         ( model       ).visit( tree )
  tree = visitors.ThreeExprLoops     (             ).visit( tree )

  print_simple_ast( tree ) # DEBUG

  return tree

#-------------------------------------------------------------------------
# TranslateBehavioralVerilog
#-------------------------------------------------------------------------
def fmt( string, indent ):
  y  = textwrap.dedent( string )
  yl = y.split('\n')
  z  = ''
  for i, x in enumerate( yl ):
    # TODO: kind of hacky
    skip = x.startswith('{') and x.endswith('}')
    if   skip : z +=          x
    elif x    : z += indent + x + '\n'
  return z

class TranslateBehavioralVerilog( ast.NodeVisitor ):

  def __init__( self ):
    self.indent = '  '
    self.elseif = False

  def fmt_body( self, body ):
    self.indent += '  '
    text = ''.join((self.visit(x) for x in body))
    self.indent  = self.indent[:-2]
    return text

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
  def visit_FunctionDef(self, node):

    # Don't bother translating undecorated functions
    if not node.decorator_list:
      return

    # Combinational Block
    if 'combinational' in node.decorator_list:
      self.assign = '='
      sensitivity = '*'

    # Posedge Clock
    elif 'posedge_clk' in node.decorator_list:
      self.assign = '<='
      sensitivity = 'posedge clk'

    # Unsupported annotation
    else:
      raise Exception("Untranslatable block!")

    # Visit the body of the function
    body = self.fmt_body( node.body )

    return fmt("""
    // logic for {}()
    always @ ({}) begin
    {}
    end
    """, self.indent ).format( node.name, sensitivity, body )

  #-----------------------------------------------------------------------
  # visit_Expr
  #-----------------------------------------------------------------------
  def visit_Expr(self, node):
    raise Exception("TODO: visit_Expr not implemented")
    return '{}{};\n'.format( self.indent, self.visit(node.value) )

  #-----------------------------------------------------------------------
  # visit_Assign
  #-----------------------------------------------------------------------
  def visit_Assign(self, node):

    # TODO: implement multiple left hand targets?
    assert len(node.targets) == 1
    lhs = self.visit( node.targets[0] )
    rhs = self.visit( node.value )

    return '{}{} {} {};\n'.format( self.indent, lhs, self.assign, rhs )

  #-----------------------------------------------------------------------
  # visit_AugAssign
  #-----------------------------------------------------------------------
  def visit_AugAssign(self, node):

    lhs = self.visit( node.target )
    rhs = self.visit( node.value )
    op  = opmap[ type(node.op) ]

    return '{4}{0} {1} {0} {2} {3};'.format( lhs, self.assign, op, rhs,
                                             self.indent )

  #-----------------------------------------------------------------------
  # visit_If
  #-----------------------------------------------------------------------
  def visit_If(self, node):

    # Visit the body of the function
    cond   = self.visit( node.test )
    body   = self.fmt_body( node.body   )
    orelse = self.fmt_body( node.orelse )

    x = fmt("""
    if ({}) begin
    {}
    end
    else begin
    {}
    end
    """, self.indent ).format( cond, body, orelse )

    return x

  #-----------------------------------------------------------------------
  # visit_For
  #-----------------------------------------------------------------------
  def visit_For(self, node):

    assert isinstance( node.iter,   _ast.Slice )
    assert isinstance( node.target, _ast.Name  )

    i     = self.visit( node.target )
    lower = self.visit( node.iter.lower )
    upper = self.visit( node.iter.upper )
    step  = self.visit( node.iter.step  )

    body  = self.fmt_body( node.body )

    x = fmt("""
    for ({0}={1}; {0} < {2}; {0}={0}+{3})
    begin
    {4}
    end
    """, self.indent ).format( i, lower, upper, step, body )

    return x

  #-----------------------------------------------------------------------
  # visit_BinOp
  #-----------------------------------------------------------------------
  def visit_BinOp(self, node):

    left  = self.visit( node.left )
    op    = opmap[ type(node.op) ]
    right = self.visit( node.right )
    return '({}{}{})'.format( left, op, right )

  #-----------------------------------------------------------------------
  # visit_BoolOp
  #-----------------------------------------------------------------------
  def visit_BoolOp(self, node):

    op     = opmap[ type(node.op) ]
    values = op.join( [self.visit(x) for x in node.values] )
    return '({})'.format( values )

  #-----------------------------------------------------------------------
  # visit_UnaryOp
  #-----------------------------------------------------------------------
  def visit_UnaryOp(self, node):

    op  = opmap[ type(node.op) ]
    return '{}{}'.format( op, self.visit(node.operand) )

  #-----------------------------------------------------------------------
  # visit_IfExp
  #-----------------------------------------------------------------------
  # Ternary operators (w = x if y else z).
  def visit_IfExp(self, node):

    test  = self.visit( node.test )
    true  = self.visit( node.body )
    false = self.visit( node.orelse )

    return '{} ? {} : {}'.format( test, true, false )

  #-----------------------------------------------------------------------
  # visit_Compare
  #-----------------------------------------------------------------------
  def visit_Compare(self, node):
    assert len(node.ops) == 1
    left  = self.visit( node.left )
    op    = opmap[ type(node.ops[0]) ]
    right = self.visit( node.comparators[0] )
    return '({} {} {})'.format( left, op, right )

  #-----------------------------------------------------------------------
  # visit_Attribute
  #-----------------------------------------------------------------------
  def visit_Attribute(self, node):
    return node.attr

  #-----------------------------------------------------------------------
  # visit_Name
  #-----------------------------------------------------------------------
  def visit_Name(self, node):
    return node.id

  #-----------------------------------------------------------------------
  # visit_Num
  #-----------------------------------------------------------------------
  def visit_Num(self, node):
    return node.n

  #-----------------------------------------------------------------------
  # visit_Subscript
  #-----------------------------------------------------------------------
  def visit_Subscript(self, node):
    signal = self.visit( node.value )
    index  = self.visit( node.slice )
    return '{}[{}]'.format( signal, index )

  #-----------------------------------------------------------------------
  # visit_Index
  #-----------------------------------------------------------------------
  def visit_Index(self, node):
    return self.visit( node.value )

  #-----------------------------------------------------------------------
  # visit_Slice
  #-----------------------------------------------------------------------
  def visit_Slice(self, node):
    assert not node.step
    assert     node.lower
    assert     node.upper
    lower = self.visit( node.lower )
    upper = self.visit( node.upper )
    return '({})-1:{}'.format( upper, lower )

  #-----------------------------------------------------------------------
  # visit_Assert
  #-----------------------------------------------------------------------
  def visit_Assert(self, node):
    return '{}// assert {}\n'.format( self.indent, self.visit(node.test) )


#-------------------------------------------------------------------------
# opmap
#-------------------------------------------------------------------------
opmap = {
    ast.Add      : '+',
    ast.Sub      : '-',
    ast.Mult     : '*',
    ast.Div      : '/',
    ast.Mod      : '%',
    ast.Pow      : '**',
    ast.LShift   : '<<',
    #ast.RShift   : '>>>',
    ast.RShift   : '>>',
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

