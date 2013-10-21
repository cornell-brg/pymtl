#=========================================================================
# VerilogLogicTransl.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

from Model import *

from   ast_transformer import SimplifiedAST
from   ast_helpers     import get_method_ast, print_simple_ast, print_ast

import sys
import ast, _ast
import collections

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
      translate_module( v, o )

#-------------------------------------------------------------------------
# translate_module
#-------------------------------------------------------------------------
def translate_module( model, o ):

  blocks = ( model.get_posedge_clk_blocks()
           + model.get_combinational_blocks()
           + model.get_tick_blocks() )

  for func in blocks:
    tree     = get_method_ast( func )
    new_tree = SimplifiedAST().visit( tree )
    print_simple_ast( new_tree )    # DEBUG
    print; print inspect.getsource( func ) # DEBUG
    TranslateLogic( sys.stdout ).visit( new_tree )


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


  def __init__( self, o ):
    self.o      = o
    self.ident  = 0
    self.elseif = False

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
  def visit_FunctionDef(self, node):
    # Don't bother translating undecorated functions
    if not node.decorator_list:
      return

    self.block_type = None

    # Combinational Block          TODO: handle s or self
    if 's.combinational' in node.decorator_list:
      self.block_type = 's.combinational'
      self.assign     = '='
      always = '  always @ (*) begin'

    # Posedge Clock                TODO: handle s or self
    elif 's.posedge_clk' in node.decorator_list:
      self.block_type = 's.posedge_clk'
      self.assign     = '<='
      always = '  always @ (posedge clk) begin'

    # Can't translate tick blocks  TODO: handle s or self
    elif  's.tick' in node.decorator_list:
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
    target = node.targets[0]._name
    #if debug:
    print >> self.o, (self.ident+2)*" ",
    print >> self.o, "{} {}".format( target, self.assign ),
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
  # visit_Subscript
  #-----------------------------------------------------------------------
  #def visit_Subscript(self, node):
  #  # TODO: add support for ranges!
  #  target_name, debug = get_target_name(node.value)
  #  print >> self.o, "{}[".format( target_name ),
  #  self.visit(node.slice)
  #  print >> self.o, "]",
  #  #print "  @@@@@",  node.slice

  #-----------------------------------------------------------------------
  # visit_Num
  #-----------------------------------------------------------------------
  def visit_Num(self, node):
    print >> self.o, node.n,

  #-----------------------------------------------------------------------
  # visit_Self
  #-----------------------------------------------------------------------
  # TODO: handle names properly
  def visit_Self(self, node):
    print >> self.o, node._name,

  #-----------------------------------------------------------------------
  # visit_Local
  #-----------------------------------------------------------------------
  # TODO: handle names properly
  def visit_Local(self, node):
    print >> self.o, node._name,

  #-----------------------------------------------------------------------
  # visit_For
  #-----------------------------------------------------------------------
  # TODO: does this work?
  def visit_For(self, node):
    raise Exception( "For not implemented!" )
    # TODO: create new list of iterators?
    var_name = node.target.id
    #if var_name not in self.model._loopvars:
    #  self.model._loopvars.append( var_name )
    # TODO: add support for temporaries declared in for loop
    for x in node.body:
      self.visit(x)

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
