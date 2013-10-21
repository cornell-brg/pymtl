#=========================================================================
# VerilogLogicTransl.py
#=========================================================================
# Tool to translate PyMTL Models into Verilog HDL.

from Model import *

from   ast_transformer import SimplifiedAST
from   ast_helpers     import get_method_ast, print_simple_ast, print_ast

import sys
import ast
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
    #print_simple_ast( new_tree )  # DEBUG
    TranslateLogic( sys.stdout ).visit( new_tree )



#-------------------------------------------------------------------------
# TranslateLogic
#-------------------------------------------------------------------------
class TranslateLogic( ast.NodeVisitor ):

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

  def __init__( self, o ):
    self.o     = o
    self.ident = 0

  def visit_FunctionDef(self, node):
    # Don't bother translating undecorated functions
    if not node.decorator_list:
      return

    self.block_type = None

    # Combinational Block          TODO: handle s or self
    if 's.combinational' in node.decorator_list:
      self.block_type = 's.combinational'
      always = '  always @ (*) begin'

    # Posedge Clock                TODO: handle s or self
    elif 's.posedge_clk' in node.decorator_list:
      self.block_type = 's.posedge_clk'
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


