#=========================================================================
# verilog_behavioral.py
#=========================================================================

import ast, _ast
import collections
import inspect
import StringIO

from ..ast_helpers import get_method_ast, print_simple_ast

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
  regs  = []
  temps = []
  array = []

  for func in blocks:

    # Type Check the AST
    tree, src = get_method_ast( func )
    new_tree  = ast_pipeline( tree, model, func )


    # Store the PyMTL source inline with the behavioral code
    print   >> behavioral_code, "  // PYMTL SOURCE:"
    for line in src.splitlines():
      print >> behavioral_code, "  // " + line

  #  # Print the Verilog translation
  #  visitor = TranslateLogic( model, behavioral_code )
  #  visitor.visit( new_tree )

  #  # TODO: check for conflicts, ensure that signals are not written in
  #  #       two different behavioral blocks!
  #  regs .extend( visitor.regs  )
  #  temps.extend( visitor.temps )
  #  array.extend( visitor.array )

  ## Print the reg declarations
  #if regs:
  #  print   >> o, '  // register declarations'
  #  for signal in regs:
  #    print >> o, '  reg    [{:4}:0] {};'.format( signal.nbits-1,
  #        signal_to_str( signal, None, model ))

  #print >> o

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

  ## Print the behavioral block code
  #print >> o
  #print >> o, behavioral_code.getvalue()



#-------------------------------------------------------------------------
# opmap
#-------------------------------------------------------------------------
def ast_pipeline( tree, model, func ):

  print_simple_ast( tree ) # DEBUG
  tree = visitors.AnnotateWithObjects( model, func ).visit( tree )
  tree = visitors.RemoveModule       (             ).visit( tree )
  tree = visitors.SimplifyDecorator  (             ).visit( tree )
  tree = visitors.RemoveValueNext    (             ).visit( tree )
  tree = visitors.AddTempSelf        ( model, func ).visit( tree )
  # TODO:
  # ? remove index nodes (replace with integer?)
  # ? replace Subscript nodes with BitSlice if they reference a Bits
  # ? replace Subscript nodes with ArrayIndex if they reference a list
  # - flatten signals so that s.out becomes out
  # - flatten port bundles
  # - flatten bitstructs
  print_simple_ast( tree ) # DEBUG










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
