#=======================================================================
# verilog_behavioral.py
#=======================================================================

import ast, _ast
import collections
import inspect
import StringIO
import textwrap

from ..ast_helpers   import get_method_ast, print_simple_ast
from ...model.signals import InPort, OutPort

# TODO: HACKY
from verilog_structural import signal_to_str
from exceptions         import VerilogTranslationError

import visitors

#-----------------------------------------------------------------------
# translate_logic_blocks
#-----------------------------------------------------------------------
def translate_logic_blocks( model ):

  blocks = ( model.get_posedge_clk_blocks()
           + model.get_combinational_blocks()
           + model.get_tick_blocks() )

  code  = ''

  # TODO: remove regs logic, move to own visitor that visits _ast.Store
  #       nodes!
  regs   = set()
  ints   = set()
  params = set()
  arrays = set()
  #temps = []

  for func in blocks:

    try:

      # Type Check the AST
      tree, src  = get_method_ast( func )
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

    # If we run into a VerilogTranslationError, provide some more debug
    # information for the user, then re-raise the exception
    except Exception as e:
      class_name = model.class_name
      func_name  = func.func_name
      msg  = 'Problem translating {}() in model {}:\n  {}' \
             .format( func_name, class_name, e.message )
      e.args = (msg,)
      raise

    code += block_code + '\n'

    # TODO: check for conflicts, ensure that signals are not written in
    #       two different behavioral blocks!

  return code, (regs, ints, params, arrays)

#-----------------------------------------------------------------------
# ast_pipeline
#-----------------------------------------------------------------------
# TODO:
# ? replace Subscript nodes with BitSlice if they reference a Bits
# ? replace Subscript nodes with ArrayIndex if they reference a list
# - flatten bitstructs
def ast_pipeline( tree, model, func ):

  #print_simple_ast( tree ) # DEBUG

  tree = visitors.AnnotateWithObjects( model, func ).visit( tree )
  tree = visitors.RemoveModule       (             ).visit( tree )
  tree = visitors.SimplifyDecorator  (             ).visit( tree )
  tree = visitors.RemoveValueNext    (             ).visit( tree )
  tree = visitors.RemoveSelf         ( model       ).visit( tree )
  tree = visitors.FlattenSubmodAttrs (             ).visit( tree )
  tree = visitors.FlattenPortBundles (             ).visit( tree )
  tree = visitors.FlattenListAttrs   (             ).visit( tree )
  tree = visitors.ThreeExprLoops     (             ).visit( tree )
  tree = visitors.ConstantToSlice    (             ).visit( tree )
  tree = visitors.InferTemporaryTypes( model       ).visit( tree )
  tree = visitors.PortListNameHack   ( model       ).visit( tree )
  tree = visitors.BitStructToSlice   (             ).visit( tree )

  #print_simple_ast( tree ) # DEBUG

  return tree

#-----------------------------------------------------------------------
# TranslateBehavioralVerilog
#-----------------------------------------------------------------------
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
    elif ('posedge_clk' in node.decorator_list or
          'tick_rtl'    in node.decorator_list):
      self.assign = '<='
      sensitivity = 'posedge clk'

    # Unsupported annotation
    else:
      raise VerilogTranslationError(
        'No valid decorator provided: {}'.format( node.decorator_list )
      )

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
    raise VerilogTranslationError("TODO: visit_Expr not implemented")
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

    return '{4}{0} {1} {0} {2} {3};\n'.format( lhs, self.assign, op, rhs,
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

    # Special handling of variable part-selects
    # TODO: make this more resilient?
    # http://www.sutherland-hdl.com/papers/2000-HDLCon-paper_Verilog-2000.pdf
    if isinstance( node.upper, _ast.BinOp ):
      assert isinstance( node.upper.op, (_ast.Add, _ast.Sub) )

      lower   = self.visit( node.lower      )
      left_op = self.visit( node.upper.left )
      assert lower == left_op

      # Widths for part selects can't be 0 (ie. select a single bit).
      # This is a hacky work around.
      try:
        if node.upper.right._object == 1:
          return '{}'.format( lower )
      # Num AST members dont have _objects...
      except AttributeError:
        assert isinstance( node.upper.right, _ast.Num )
        if node.upper.right.n == 1:
          return '{}'.format( lower )

      op      = opmap[type(node.upper.op)]
      upper   =  self.visit( node.upper.right )
      return '{} {}: {}'.format( lower, op, upper )

    # Normal slices
    lower = self.visit( node.lower )
    upper = self.visit( node.upper )
    return '({})-1:{}'.format( upper, lower )

  #-----------------------------------------------------------------------
  # visit_Assert
  #-----------------------------------------------------------------------
  # Currently skip Assert translations, add in the future?
  def visit_Assert(self, node):
    return ''

  #-----------------------------------------------------------------------
  # visit_Call
  #-----------------------------------------------------------------------
  def visit_Call(self, node):

    # Can only translate calls generated from Name nodes
    assert isinstance( node.func, _ast.Name )
    func_name = self.visit( node.func )

    # Handle sign extension
    if func_name  == 'sext':
      sig_name   = self.visit( node.args[0] )
      sig_nbits  = node.args[0]._object.nbits
      ext_nbits  = self.visit( node.args[1] )
      return '{{ {{ {3}-{1} {{ {0}[{2}] }} }}, {0}[{2}:0] }}' \
             .format( sig_name, sig_nbits, sig_nbits-1, ext_nbits )

    # Handle zero extension
    if func_name  == 'zext':
      sig_name   = self.visit( node.args[0] )
      sig_nbits  = node.args[0]._object.nbits
      ext_nbits  = self.visit( node.args[1] )
      return "{{ {{ {3}-{1} {{ 1'b0 }} }}, {0}[{2}:0] }}" \
             .format( sig_name, sig_nbits, sig_nbits-1, ext_nbits )

    # Handle concatentation
    if func_name  == 'concat':
      signal_names = [ self.visit(x) for x in node.args ]
      return "{{ {signals} }}" \
             .format( signals=','.join(signal_names) )

    # Handle reduce and
    if func_name  == 'reduce_and':
      sig_name = self.visit( node.args[0] )
      return "(&{sig_name})".format( sig_name=sig_name )

    # Handle reduce or
    if func_name  == 'reduce_or':
      sig_name = self.visit( node.args[0] )
      return "(|{sig_name})".format( sig_name=sig_name )

    # Handle reduce xor
    if func_name  == 'reduce_xor':
      sig_name = self.visit( node.args[0] )
      return "(^{sig_name})".format( sig_name=sig_name )

    # Handle Bits
    if func_name  == 'Bits':
      if isinstance( node.args[0], ast.Num ): nbits = node.args[0].n
      else:                                   nbits = node.args[0]._object
      assert isinstance( nbits, int )
      value = self.visit( node.args[1] ) if len(node.args) == 2 else '0'
      return "{nbits}'d{value}".format( nbits=nbits, value=value )

    raise TranslationError(
      "Function is not translatable: {}".format( func_name )
    )

  #-----------------------------------------------------------------------
  # visit_Raise
  #-----------------------------------------------------------------------
  def visit_Raise(self, node):
    return fmt( '$display("An Exception was raised!!!");', self.indent )

#-----------------------------------------------------------------------
# opmap
#-----------------------------------------------------------------------
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
