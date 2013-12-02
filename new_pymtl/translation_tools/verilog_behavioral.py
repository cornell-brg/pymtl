#=========================================================================
# verilog_behavioral.py
#=========================================================================

import ast, _ast
import collections
import inspect
import StringIO

from ..ast_helpers import get_method_ast, print_simple_ast

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
  regs  = set()
  temps = []
  array = []

  for func in blocks:

    # Type Check the AST
    tree, src  = get_method_ast( func )
    new_tree   = ast_pipeline( tree, model, func )
    regs      |= visitors.GetRegsTempsArrays().get( new_tree )


    # Store the PyMTL source inline with the behavioral code
    block_code = ("  // PYMTL SOURCE:\n"
                  "  // {}\n\n").format( "\n  // ".join( src.splitlines()))

    # Print the Verilog translation
    visitor     = TranslateBehavioralVerilog()
    block_code += visitor.visit( new_tree )

    print >> behavioral_code, block_code

    # TODO: check for conflicts, ensure that signals are not written in
    #       two different behavioral blocks!

  print regs

  # Print the reg declarations
  if regs:
    print   >> o, '  // register declarations'
    for signal in regs:
      print >> o, '  reg    [{:4}:0] {};'.format( signal.nbits-1,
          signal_to_str( signal, None, model ))

  print >> o

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
def ast_pipeline( tree, model, func ):

  print_simple_ast( tree ) # DEBUG

  tree = visitors.AnnotateWithObjects( model, func ).visit( tree )
  tree = visitors.RemoveModule       (             ).visit( tree )
  tree = visitors.SimplifyDecorator  (             ).visit( tree )
  tree = visitors.RemoveValueNext    (             ).visit( tree )
  tree = visitors.RemoveSelf         ( model       ).visit( tree )

  print_simple_ast( tree ) # DEBUG

  return tree

  # TODO:
  # ? remove index nodes (replace with integer?)
  # ? replace Subscript nodes with BitSlice if they reference a Bits
  # ? replace Subscript nodes with ArrayIndex if they reference a list
  # - flatten port bundles
  # - flatten bitstructs

#-------------------------------------------------------------------------
# TranslateBehavioralVerilog
#-------------------------------------------------------------------------
class TranslateBehavioralVerilog( ast.NodeVisitor ):

  def __init__( self ):
    self.ident = 0

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

    body = '    '.join( [ self.visit(x) for x in node.body ] )

    s = ('  // logic for {}()\n'
         '  always @ ({}) begin\n'
         '    {}'
         '  end\n').format( node.name, sensitivity, body )

    return s

  #-----------------------------------------------------------------------
  # visit_Assign
  #-----------------------------------------------------------------------
  def visit_Assign(self, node):

    # TODO: implement multiple left hand targets?
    assert len(node.targets) == 1
    lhs = self.visit( node.targets[0] )
    rhs = self.visit( node.value )

    return '{} {} {};\n'.format( lhs, self.assign, rhs )

  #-----------------------------------------------------------------------
  # visit_AugAssign
  #-----------------------------------------------------------------------
  def visit_AugAssign(self, node):

    lhs = self.visit( node.target )
    rhs = self.visit( node.value )
    op  = opmap[ type(node.op) ]

    return '{0} {1} {0} {2} {3};\n'.format( lhs, self.assign, op, rhs )

  #-----------------------------------------------------------------------
  # visit_BinOp
  #-----------------------------------------------------------------------
  def visit_BinOp(self, node):

    op  = opmap[ type(node.op) ]
    return '({}{}{})'.format( node.left, op, node.right )

  #-----------------------------------------------------------------------
  # visit_BoolOp
  #-----------------------------------------------------------------------
  def visit_BoolOp(self, node):

    op  = opmap[ type(node.op) ]
    abc = op.join( node.values )
    return '({})'.format( abc )

  #-----------------------------------------------------------------------
  # visit_UnaryOp
  #-----------------------------------------------------------------------
  def visit_UnaryOp(self, node):

    op  = opmap[ type(node.op) ]
    return '{}{}'.format( op, node.operand )

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

