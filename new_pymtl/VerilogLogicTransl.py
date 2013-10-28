#=========================================================================
# VerilogLogicTransl.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

#from Model import *

from   ast_typer       import TypeAST
from   ast_helpers     import get_method_ast, print_simple_ast, print_ast

import sys
import ast, _ast
import collections
import inspect

from signals import InPort, OutPort, Wire

#-------------------------------------------------------------------------
# VerilogLogicTransl
#-------------------------------------------------------------------------
class VerilogLogicTransl(object):

  def __init__(self, model, o=sys.stdout):

    # List of models to translate
    translation_queue = collections.OrderedDict()

    # Utility function to recursively collect all submodels in design
    def collect_all_models( m ):
      # Add the model to the queue
      translation_queue[ m.class_name ] = m

      for subm in m.get_submodules():
        collect_all_models( subm )

    # Collect all submodels in design and translate them
    collect_all_models( model )
    for k, v in translation_queue.items():
      translate_logic_blocks( v, o )

#-------------------------------------------------------------------------
# translate_logic_blocks
#-------------------------------------------------------------------------
def translate_logic_blocks( model, o ):

  blocks = ( model.get_posedge_clk_blocks()
           + model.get_combinational_blocks()
           + model.get_tick_blocks() )

  import StringIO
  behavioral_code = StringIO.StringIO()

  # TODO: remove regs logic, move to own visitor that visits _ast.Store
  #       nodes!
  regs  = []
  temps = []
  array = []

  for func in blocks:

    # Type Check the AST
    tree = get_method_ast( func )
    src  = inspect.getsource( func )
    #print_simple_ast( tree )    # DEBUG
    print src
    new_tree = TypeAST( model, func ).visit( tree )

    print_simple_ast( new_tree ) # DEBUG

    # Store the PyMTL source inline with the behavioral code
    print   >> behavioral_code, "  // PYMTL SOURCE:"
    for line in src.splitlines():
      print >> behavioral_code, "  // " + line

    # Print the Verilog translation
    visitor = TranslateLogic( model, behavioral_code )
    visitor.visit( new_tree )

    # TODO: check for conflicts, ensure that signals are not written in
    #       two different behavioral blocks!
    regs .extend( visitor.regs  )
    temps.extend( visitor.temps )
    array.extend( visitor.array )

  # Print the reg declarations
  if regs:
    print   >> o, '  // register declarations'
    for signal in regs:
      print >> o, '  reg    [{:4}:0] {};'.format( signal.nbits-1, signal.name )

  print >> o

  # Print the temporary declarations
  # TODO: this doesn't really work, need to set type of temp
  if temps:
    print   >> o, '  // temporary declarations'
    for signal in temps:
      print >> o, '  reg {};'.format( signal )

  # TODO: clean this up and move it somewhere else! Ugly!
  print >> o
  if array:
    print   >> o, '  // temporary arrays'
    for x in array:
      # declare the array
      nports = len( x )
      nbits  = x[0].nbits
      name   = x[0].name.split('[')[0]
      if   isinstance( x[0], InPort  ):
        print   >> o, '  wire   [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
        for i in range( nports ):
          print >> o, '  assign {0}[{1:3}] = {0}${1:03d};'.format( name, i )
      elif isinstance( x[0], OutPort ):
        print   >> o, '  reg    [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
        for i in range( nports ):
          print >> o, '  assign {0}${1:03d} = {0}[{1:3}];'.format( name, i )
      elif isinstance( x[0], Wire ):
        print   >> o, '  reg    [{:4}:0] {}[0:{}];'.format( nbits-1, name, nports-1 )
      else:
        raise Exception("Untranslatable array item!")

  # Print the temporary declarations

  # Print the behavioral block code
  print >> o
  print >> o, behavioral_code.getvalue()

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

#-------------------------------------------------------------------------
# TranslateLogic
#-------------------------------------------------------------------------
class TranslateLogic( ast.NodeVisitor ):


  def __init__( self, model, o ):
    self.model  = model
    self.o      = o
    self.ident  = 0
    self.elseif = False
    self.regs   = set()
    self.temps  = set()
    self.array  = []

    self.this_obj = None

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
  def visit_FunctionDef(self, node):
    # Don't bother translating undecorated functions
    if not node.decorator_list:
      return

    self.block_type = None

    # Combinational Block          TODO: handle s or self
    if 'combinational' in node.decorator_list:
      self.block_type = 's.combinational'
      self.assign     = '='
      always = '  always @ (*) begin'

    # Posedge Clock                TODO: handle s or self
    elif 'posedge_clk' in node.decorator_list:
      self.block_type = 's.posedge_clk'
      self.assign     = '<='
      always = '  always @ (posedge clk) begin'

    # Can't translate tick blocks  TODO: handle s or self
    elif  'tick' in node.decorator_list:
      raise Exception("Tick blocks can't be translated!")

    # Write
    if self.block_type:
      print >> self.o
      print >> self.o, '  // logic for {}()'.format( node.name )
      print >> self.o, always
      # Visit each line in the function, translate one at a time.
      self.ident += 2
      for x in node.body:
        self.visit(x)
      self.ident -= 2
      print >> self.o, '  end\n'

  #-----------------------------------------------------------------------
  # visit_Assign
  #-----------------------------------------------------------------------
  def visit_Assign(self, node):
    # TODO: implement multiple left hand targets?
    assert len(node.targets) == 1
    #if debug:
    print >> self.o, (self.ident+2)*" ",
    self.visit( node.targets[0] )
    print >> self.o, "{}".format( self.assign ),
    self.visit( node.value )
    print >> self.o, ';'

  #-----------------------------------------------------------------------
  # visit_AugAssign
  #-----------------------------------------------------------------------
  def visit_AugAssign(self, node):
    # TODO: implement multiple left hand targets?
    print >> self.o, (self.ident+2)*" ",
    self.visit( node.target )
    print >> self.o, self.assign,
    self.visit( node.target )
    print >> self.o, opmap[type(node.op)],
    self.visit(node.value)
    print >> self.o, ';'

  #-----------------------------------------------------------------------
  # visit_BinOp
  #-----------------------------------------------------------------------
  def visit_BinOp(self, node):
    print >> self.o, '(',
    self.visit(node.left)
    print >> self.o, opmap[type(node.op)],
    self.visit(node.right)
    print >> self.o, ')',

  #-----------------------------------------------------------------------
  # visit_BoolOp
  #-----------------------------------------------------------------------
  def visit_BoolOp(self, node):
    print >> self.o, '(',
    num_nodes = len(node.values)
    for i in range( num_nodes - 1 ):
      self.visit( node.values[i] )
      print >> self.o, opmap[type(node.op)],
    self.visit( node.values[ num_nodes - 1 ] )
    print >> self.o, ')',

  #-----------------------------------------------------------------------
  # visit_UnaryOp
  #-----------------------------------------------------------------------
  def visit_UnaryOp(self, node):
    print >> self.o, opmap[type(node.op)],
    self.visit(node.operand)

  #-----------------------------------------------------------------------
  # visit_IfExp
  #-----------------------------------------------------------------------
  # Ternary operators (w = x if y else z).
  def visit_IfExp(self, node):
    # TODO: verify this works
    self.visit(node.test)
    print >> self.o, '?',
    self.visit(node.body)
    print >> self.o, ':',
    self.visit(node.orelse)

  #-----------------------------------------------------------------------
  # visit_Compare
  #-----------------------------------------------------------------------
  def visit_Compare(self, node):
    assert len(node.ops) == 1
    # TODO: add debug check
    print >> self.o, "(",
    self.visit(node.left)
    op_symbol = opmap[type(node.ops[0])]
    print >> self.o, op_symbol,
    self.visit(node.comparators[0])
    print >> self.o, ")",

  #-----------------------------------------------------------------------
  # visit_ArrayIndex
  #-----------------------------------------------------------------------
  def visit_ArrayIndex(self, node):

    # We don't support ArrayIndexes being slices
    assert not isinstance( node.slice, _ast.Slice )

    # TODO: need to set ArrayIndex to point to list object
    # Ugly, by creating portlist?
    if node.value._object not in self.array:
      self.array.append( node.value._object )

    # Translate
    self.visit(node.value)
    print >> self.o, "[",
    self.visit(node.slice)
    print >> self.o, "]",

  #-----------------------------------------------------------------------
  # visit_BitSlice
  #-----------------------------------------------------------------------
  def visit_BitSlice(self, node):

    # Writes to slices need to add the signal as a reg
    if isinstance( node.ctx, _ast.Store ):
      self.regs.add( node.value._object )

    # TODO: add support for ranges!
    self.visit(node.value)
    print >> self.o, "[",
    self.visit(node.slice)
    print >> self.o, "]",

  #-----------------------------------------------------------------------
  # visit_Slice
  #-----------------------------------------------------------------------
  def visit_Slice(self, node):
    assert node.step == None
    upper = node.upper
    lower = node.lower
    if isinstance( upper, _ast.Num) and isinstance( lower, _ast.Num ):
      self.visit( node.upper )
      print >> self.o, '-1:',
      self.visit( node.lower )
    # TODO: Hacky attempt at implementing variable part-selects, as
    #       described here:
    #       http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-884-complex-digital-systems-spring-2005/related-resources/verilog_2k1paper.pdf
    elif isinstance( upper, _ast.BinOp ):
      assert isinstance( upper.op, (_ast.Add, _ast.Sub) )
      self.visit( node.lower )
      print >> self.o, '{}:'.format( opmap[type(node.upper.op)] ),
      self.visit( node.upper.right )
    else:
      self.visit( node.upper )
      print >> self.o, "-1:",
      self.visit( node.lower )
      #raise Exception( "Cannot translate this slice!" )

  #-----------------------------------------------------------------------
  # visit_Num
  #-----------------------------------------------------------------------
  def visit_Num(self, node):
    print >> self.o, node.n,

  #-----------------------------------------------------------------------
  # visit_Self
  #-----------------------------------------------------------------------
  # TODO: handle names properly
  #def visit_Self(self, node):
  #  self.this_obj = ThisObject( '', self.model )
  #  self.visit( node.value )
  #  print >> self.o, self.this_obj.name,

  #-----------------------------------------------------------------------
  # visit_Local
  #-----------------------------------------------------------------------
  # TODO: handle names properly
  #def visit_Local(self, node):
  #  obj = getattr( self.model, node.attr )
  #  self.this_obj = ThisObject( node.attr, obj )
  #  self.visit( node.value )
  #  print >> self.o, self.this_obj.name,

  #-----------------------------------------------------------------------
  # visit_Attribute
  #-----------------------------------------------------------------------
  # TODO: currently assuming all attributes are bits objects,
  #       need to fix for PortBundles and BitStructs
  def visit_Attribute(self, node):
    if isinstance( node.ctx, _ast.Store ):
      self.regs.add( node._object )

    # TODO: hacky
    if   isinstance( node._object, list ):
      print >> self.o, node._object[0].name.split('[')[0],
    # TODO:convert int attributes into contant nodes!
    elif isinstance( node._object, int ):
      print >> self.o, node._object,
    else:
      print >> self.o, node._object.name,

  #-----------------------------------------------------------------------
  # visit_Temp
  #-----------------------------------------------------------------------
  def visit_Temp(self, node):
    self.temps.add( node.id )
    print >> self.o, node.id,

  #-----------------------------------------------------------------------
  # visit_For
  #-----------------------------------------------------------------------
  # TODO: does this work?
  def visit_For(self, node):

    # TODO: fix to return string..
    assert isinstance( node.iter, _ast.Slice )
    i = node.target.id

    # TODO: add support for temporaries declared in for loop
    print >> self.o, (self.ident+2)*" " + "for ({}=".format(i),
    self.visit( node.iter.lower )
    print >> self.o, "; {}<".format(i),
    self.visit( node.iter.upper )
    print >> self.o, "; {0}={0}+".format(i),
    self.visit( node.iter.step )
    print >> self.o, ")"
    print >> self.o, (self.ident+2)*" " + "begin"
    for x in node.body:
      self.visit(x)
    print >> self.o, (self.ident+2)*" " + "end"

  #-----------------------------------------------------------------------
  # visit_If
  #-----------------------------------------------------------------------
  # TODO: cleanup
  def visit_If(self, node):
    # Write out the if block
    if not self.elseif:
      print >> self.o
      print >> self.o, self.ident*" " + "  if (",
    else:
      print >> self.o, self.ident*" " + "  else if (",
      self.elseif = False
    self.visit(node.test)
    print >> self.o, " ) begin"
    # Write out the body
    for body in node.body:
      self.ident += 2
      self.visit(body)
      self.ident -= 2
    print >> self.o, self.ident*" " + "  end"
    # Write out an an elif block
    if len(node.orelse) == 1 and isinstance(node.orelse[0], _ast.If):
      self.elseif = True
      self.visit(node.orelse[0])
    # Write out an else block
    elif node.orelse:
      print >> self.o, self.ident*" " + "  else begin"
      for orelse in node.orelse:
        self.ident += 2
        self.visit(orelse)
        self.ident -= 2
      print >> self.o, self.ident*" " + "  end"

  #-----------------------------------------------------------------------
  # visit_Assert
  #-----------------------------------------------------------------------
  def visit_Assert(self, node):
    print >> self.o, self.ident*" " + "  // ASSERT ",
    self.visit( node.test )
    print >> self.o

  #-----------------------------------------------------------------------
  # visit_Call
  #-----------------------------------------------------------------------
  #def visit_Call(self, node):
  #  if not self.write_names:
  #    return

  #  # TODO: clean this up!!!!
  #  func_list, debug = get_target_list( node.func )
  #  if func_list[-1] == 'zext':
  #    param, debug = get_target_name( node.args[0] )
  #    param_value = self.get_signal_type( param )
  #    signal_type = self.get_signal_type( func_list[0] )
  #    ext = param_value - signal_type.width
  #    # sext
  #    #print >> self.o, "{{ {{ {0} {{ {1}[{2}] }} }}, {3} }}".format(
  #    print >> self.o, "{{ {{ {0} {{ 1'b0 }} }}, {1} }}".format(
  #        ext, func_list[0] ),
  #    #self.type_stack.append( Bits(param_value) )
  #  else:
  #    raise Exception("Function {}() not supported for translation!"
  #                    "".format(func) )

class ThisObject( object ):
  def __init__( self, name, obj ):
    self.name = name
    self.obj  = obj

