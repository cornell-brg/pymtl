#=======================================================================
# verilog_behavioral.py
#=======================================================================

from __future__ import print_function

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
           + model.get_combinational_blocks() )

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
      endl = '\n'
      def fmt( x ):
        if x:  return ' '+x+endl # add extra space before lines w/ content
        else:  return       endl # ignore blank lines

      pymtl_src  = "  //".join([ fmt(x) for x in src.splitlines() ])
      block_code =("  // PYMTL SOURCE:"+endl+
                   "  //"              +endl+
                   "  //{}"            +endl ).format( pymtl_src )

      # Print the Verilog translation
      visitor     = TranslateBehavioralVerilog()
      block_code += visitor.visit( new_tree )

    # If we run into an assertion, just reraise it
    except AssertionError as e:
      raise

    # If we run into a VerilogTranslationError, provide some more debug
    # information for the user, then re-raise the exception
    except Exception as e:
      src, filelineno = inspect.getsourcelines( func )

      error      = str(e.message)
      file_name  = inspect.getfile(func)
      class_name = model.class_name
      func_name  = func.func_name
      if hasattr( e, 'lineno'):
        lineno   = filelineno + e.lineno - 1
        srcline  = src[e.lineno-1]
      else:
        error    = ('Unexpected error during VerilogTranslation!\n'
                    'Please contact the PyMTL devs!\n' + error )
        lineno   = '~{}'.format( filelineno - 1 )
        srcline  = '<unknown>\n'

      msg  = ('\n{error}\n\n'
              '> {srcline}\n'
              'File:      {file_name}\n'
              'Model:     {class_name}\n'
              'Function:  {func_name}\n'
              'Line:      {lineno}\n'
              .format( **locals() ) )
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
  tree = visitors.AnnotateAssignments(             ).visit( tree )
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
      sensitivity = '*'

    # Posedge Clock
    elif ('posedge_clk' in node.decorator_list or
          'tick_rtl'    in node.decorator_list):
      sensitivity = 'posedge clk'

    # Unsupported annotation
    else:
      def get_dec_name( dec ):
        if   hasattr( dec, 'id'   ): return dec.id
        elif hasattr( dec, 'attr' ): return dec.attr
        else:                        return dec
      raise VerilogTranslationError(
        'An invalid decorator was encountered!\nOnly @s.combinational,\n'
        '@s.tick_rtl, and @s.posedge_clk are currently translatable.\n'
        'Current decorators: {}'.format(
          [ get_dec_name( x ) for x in node.decorator_list ]
        ), node.lineno
      )

    # Visit the body of the function
    body = self.fmt_body( node.body )

    return fmt('''
    // logic for {}()
    always @ ({}) begin
    {}
    end
    ''', self.indent ).format( node.name, sensitivity, body )

  #-----------------------------------------------------------------------
  # visit_Expr
  #-----------------------------------------------------------------------
  def visit_Expr(self, node):
    raise VerilogTranslationError(
      'An unexpected Expr node was encountered!\n'
      'Please inform the PyMTL developers!',
      node.lineno
    )
    return '{}{};\n'.format( self.indent, self.visit(node.value) )

  #-----------------------------------------------------------------------
  # visit_Assign
  #-----------------------------------------------------------------------
  def visit_Assign(self, node):

    # NOTE: this should really be caught earlier
    if len(node.targets) != 1 or isinstance(node.targets[0], (ast.Tuple)):
      raise VerilogTranslationError(
        'Assignments can only have one item on the left-hand side!\n'
        'Please modify "x,y = ..." to be two separate lines.',
        node.lineno
      )

    lhs    = self.visit( node.targets[0] )
    rhs    = self.visit( node.value )
    assign = '=' if node._is_blocking else '<='
    indent = self.indent

    return '{indent}{lhs} {assign} {rhs};\n'.format(**vars())

  #-----------------------------------------------------------------------
  # visit_Tuple
  #-----------------------------------------------------------------------
  #def visit_Tuple(self, node):

  #-----------------------------------------------------------------------
  # visit_AugAssign
  #-----------------------------------------------------------------------
  def visit_AugAssign(self, node):

    lhs    = self.visit( node.target )
    rhs    = self.visit( node.value )
    op     = opmap[ type(node.op) ]
    assign = '=' if node._is_blocking else '<='
    indent = self.indent

    return '{indent}{lhs} {assign} {lhs} {op} {rhs};\n'.format(**vars())

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

    if not (isinstance( node.iter,   _ast.Slice ) or
            isinstance( node.target, _ast.Name  )):
      raise VerilogTranslationError(
        'An unexpected error occurred when translating a "for loop"!\n'
        'Please inform the PyMTL developers!',
        node.lineno
      )

    i     = self.visit( node.target )
    lower = self.visit( node.iter.lower )
    upper = self.visit( node.iter.upper )
    step  = self.visit( node.iter.step  )
    lt_gt = node.iter.lt_gt

    body  = self.fmt_body( node.body )

    x = fmt("""
    for ({i}={lower}; {i} {lt_gt} {upper}; {i}={i}+{step})
    begin
    {body}
    end
    """, self.indent ).format( **locals() )

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
    if len(node.ops) != 1:
      raise VerilogTranslationError(
        'Chained comparisons are currently not translatable!\n'
        'Please change "x < y < z" to the form "(x < y) and (y < z)!',
        node.lineno
      )
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
    if   node.id == 'True' : return "1'b1"
    elif node.id == 'False': return "1'b0"
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

    # FIXME: hack for type-inferenced objects incorrectly updating their
    #        parent subscript! Should handle this in TypeInference pass.
    if not node._object:
      node._object = node.value._object

    # notify slice/index of nbits so we can handle relative indexes
    try:
      node.slice._nbits = node._object.nbits
    except AttributeError:
      node.slice._nbits = len( node._object )

    # slices don't have lineno, add them for debug purposes
    node.slice.lineno = node.lineno

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
    if node.step:
      raise VerilogTranslationError(
        'An unexpected error when translating Slices was encountered!\n'
        'Please inform the PyMTL developers!',
        node.lineno
      )

    # handle open slices [:upper], [lower:], and [:]
    if node.lower == None: node.lower = ast.Num( 0 )
    if node.upper == None: node.upper = ast.Num( node._nbits )

    # Special handling of variable part-selects
    # TODO: make this more resilient?
    # http://www.sutherland-hdl.com/papers/2000-HDLCon-paper_Verilog-2000.pdf
    if isinstance( node.upper, _ast.BinOp ):

      if not isinstance( node.upper.op, (_ast.Add, _ast.Sub) ):
        raise VerilogTranslationError(
          'Slicing in behavioral blocks cannot contain arbitrary arithmetic!\n'
          'Variable slices must be of the form [x:x+N] or [x:x-N]!\n'
          '(and N must be constant!)\n',
          node.lineno
        )

      lower     = self.visit( node.lower      )
      left_op   = self.visit( node.upper.left )
      right_num = node.upper.right

      if lower != left_op:
        raise VerilogTranslationError(
          'Slicing in behavioral blocks cannot contain arbitrary arithmetic!\n'
          'Variable slices must be of the form [x:x+N] or [x:x-N]!\n'
          '(and N must be constant!)\n',
          node.lineno
        )

      # Determine the width of the part-select.
      # FIXME: elif needed b/c Num AST nodes dont have _objects...
      if   hasattr( right_num, '_object' ):          width = right_num._object
      elif isinstance( node.upper.right, _ast.Num ): width = right_num.n
      else:
        raise VerilogTranslationError(
          'Slicing in behavioral blocks cannot contain arbitrary arithmetic!\n'
          'Variable slices must be of the form [x:x+N] or [x:x-N]!\n'
          '(and N must be constant!)\n',
          node.lineno
        )

      # Widths for part selects can't be 0 (ie. select a single bit), work
      # around this limitation by converting into a normal index access.
      if width == 1:
        return '{}'.format( lower )
      else:
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
    if not isinstance( node.func, _ast.Name ):
      raise VerilogTranslationError(
        'Encountered a non-translatable function call!',
        node.lineno
      )
    if node.keywords:
      raise VerilogTranslationError(
        'Cannot translate function calls with keyword arguments!\n'
        'Please replace "f( a, argname=b )" with "f( a, b )".',
        node.lineno
      )
    if node.starargs:
      raise VerilogTranslationError(
        'Cannot translate function calls with arg unpacking!\n'
        'Please replace "f( *arg_list )" with "f( a, b )".',
        node.lineno
      )
    if node.kwargs:
      raise VerilogTranslationError(
        'Cannot translate function calls with kwarg unpacking!\n'
        'Please replace "f( **arg_dict )" with "f( a, b )".',
        node.lineno
      )

    # Handle sign extension
    func_name = self.visit( node.func )

    # Handle sign extension
    if func_name  == 'sext':
      if len(node.args) != 2:
        raise VerilogTranslationError(
          'Encountered a non-translatable sext call!\n'
          'sext(in, nbits) must have exactly two arguments!',
          node.lineno
        )
      try:
        if isinstance( node.args[1], ast.Num ): nbits = node.args[1].n
        else:                                   nbits = node.args[1]._object
        assert isinstance( nbits, int )
      except (AssertionError,AttributeError):
        raise VerilogTranslationError(
          'Encountered a non-translatable sext call!\n'
          'Argument "nbits" of sext(in,nbits) is not a constant int!',
          node.lineno
        )

      # This is to handle the special case that sign-extending a sliced
      # variable is incorrectly translated, by incorporating the slice
      # value which previously the code wasn't aware of.
      # Previously the slice [x:y] is a part of sig_name a[x:y] and every
      # variable has two layers of indices a[x:y][z].

      # Without this piece of code, the translation of
      # sext( a[31:32], 20 ) will look like
      #  { { 20-32 { a[(32)-1:31][31] } }, a[(32)-1:31][31:0] }
      # which is absolutely wrong.
      # The correct answer is { { 20-1 {a[31]} }, a[31:31] }

      if isinstance( node.args[0], ast.Subscript ):
        sig_name    = self.visit( node.args[0].value )

        slice_lower = self.visit( node.args[0].slice.value.lower )
        slice_upper = self.visit( node.args[0].slice.value.upper )
        sig_nbits   = slice_upper - slice_lower

        ext_nbits   = self.visit( node.args[1] )

        return '{{ {{ {2}-{1} {{ {0}[{3}] }} }}, {0}[{3}:{4}] }}' \
              .format( sig_name, sig_nbits, ext_nbits,
                       slice_upper-1, slice_lower )

      sig_name  = self.visit( node.args[0] )
      sig_nbits = node.args[0]._object.nbits
      ext_nbits = self.visit( node.args[1] )

      return '{{ {{ {3}-{1} {{ {0}[{2}] }} }}, {0}[{2}:0] }}' \
             .format( sig_name, sig_nbits, sig_nbits-1, ext_nbits )

    # Handle zero extension
    if func_name  == 'zext':
      if len(node.args) != 2:
        raise VerilogTranslationError(
          'Encountered a non-translatable zext call!\n'
          'zext(in, nbits) must have exactly two arguments!',
          node.lineno
        )
      try:
        if isinstance( node.args[1], ast.Num ): nbits = node.args[1].n
        else:                                   nbits = node.args[1]._object
        assert isinstance( nbits, int )
      except (AssertionError,AttributeError):
        raise VerilogTranslationError(
          'Encountered a non-translatable zext call!\n'
          'Argument "nbits" of zext(in,nbits) is not a constant int!',
          node.lineno
        )

      # This is to handle the special case that zero-extending a sliced
      # variable is incorrectly translated, by incorporating the slice
      # value which previously the code wasn't aware of.
      # Previously the slice [x:y] is a part of sig_name a[x:y] and every
      # variable has two layers of indices a[x:y][z].

      if isinstance( node.args[0], ast.Subscript ):
        sig_name    = self.visit( node.args[0].value )

        slice_lower = self.visit( node.args[0].slice.value.lower )
        slice_upper = self.visit( node.args[0].slice.value.upper )
        sig_nbits   = slice_upper - slice_lower

        ext_nbits   = self.visit( node.args[1] )

        return "{{ {{ {2}-{1} {{ 1'b0 }} }}, {0}[{3}:{4}] }}" \
              .format( sig_name, sig_nbits, ext_nbits,
                       slice_upper-1, slice_lower )

      sig_name  = self.visit( node.args[0] )
      sig_nbits = node.args[0]._object.nbits
      ext_nbits = self.visit( node.args[1] )

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
      if len(node.args) > 2:
        raise VerilogTranslationError(
          'Encountered a non-translatable Bits call!\n'
          'Bits(nbits,value) must have exactly two arguments!',
          node.lineno
        )
      if not isinstance( node.args[0], (ast.Num, ast.Name, ast.Attribute)):
        raise VerilogTranslationError(
          'Encountered a non-translatable Bits call!\n'
          'Argument "nbits" of Bits(nbits,value) is not a constant int!',
          node.lineno
        )
      if len(node.args) == 2 and \
         not isinstance( node.args[1], (ast.Num, ast.Name, ast.Attribute)):
        raise VerilogTranslationError(
          'Encountered a non-translatable Bits call!\n'
          'Argument "value" of Bits(nbits,value) is not a constant int!',
          node.lineno
        )

      try:
        if   isinstance( node.args[0], ast.Num ): nbits = node.args[0].n
        else:                                     nbits = node.args[0]._object
        if   len(node.args) == 1:                 value = 0
        elif isinstance( node.args[1], ast.Num ): value = node.args[1].n
        else:                                     value = node.args[1]._object
        assert isinstance( nbits, int )
        assert isinstance( value, int )
      except (AssertionError,AttributeError):
        raise VerilogTranslationError(
          'Encountered a non-translatable Bits call!\n'
          'Arguments of Bits(nbits,value) are not both constant ints!',
          node.lineno
        )

      return "{nbits}'d{value}".format( nbits=nbits, value=value )

    raise VerilogTranslationError(
      'Encountered a non-translatable function call: {}!'.format( func_name ),
      node.lineno
    )

  #-----------------------------------------------------------------------
  # visit_Raise
  #-----------------------------------------------------------------------
  def visit_Raise(self, node):
    return fmt( '$display("An Exception was raised!!!");', self.indent )

  #-----------------------------------------------------------------------
  # visit_Print
  #-----------------------------------------------------------------------
  def visit_Print(self, node):

    signals = [ self.visit( expr ) for expr in node.values ]
    fmt_str = ' ' .join( ['%d']*len(signals) )
    sig_lst = ', '.join( signals )
    msg     = '$display( "{}", {} );'.format( fmt_str, sig_lst )
    return fmt( msg, self.indent )

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
