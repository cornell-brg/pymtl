#=========================================================================
# CLogicTransl_test.py
#=========================================================================
# Tool to translate PyMTL Models into a C simulation object.

from   ast_typer       import TypeAST
from   ast_helpers     import get_method_ast, print_simple_ast, print_ast
from   SimulationTool  import SimulationTool

import sys
import ast, _ast
import collections
import inspect
import StringIO

from signals       import InPort, OutPort, Wire, Constant
from ast_visitor   import GetVariableName
from Bits          import Bits
from BitStruct     import BitStruct
from SignalValue   import SignalValueWrapper
from CLogicHelpers import gen_cheader, gen_cdef, gen_csim, gen_pywrapper

from VerilogTranslationTool import mangle_name

#-------------------------------------------------------------------------
# CLogicTransl
#-------------------------------------------------------------------------
# TODO: same as Verilog, reduce code dup
def CLogicTransl( model, o=sys.stdout ):

    # Create the python simulator
    sim = SimulationTool( model )

    c_functions = StringIO.StringIO()
    c_variables = StringIO.StringIO()
    c_variables = StringIO.StringIO()

    # Visit tick functions, save register information
    regs = []
    localvars = {}
    for func in sim._sequential_blocks:
      r, l = translate_func( func, c_functions )
      regs.extend( r )
      localvars.update( l )

    # Print signal declarations, use reg information
    top_ports, all_ports =  declare_signals( sim, regs, c_variables )

    # print locals
    print >> c_variables
    print >> c_variables, '/* LOCALS ' + '-'*60 + '*/'
    #import pprint
    #pprint.pprint( all_ports)
    for var, obj in localvars.items():
      #print var, var in all_ports
      if var not in all_ports:
        var_type = get_type( obj, o )
        print >> c_variables, "{} {};".format( var_type, var )

    # Create the C header
    print >> o, '#include <stdio.h>'
    print >> o, '#define  True  true'
    print >> o, '#define  False false'
    print >> o

    print >> o, gen_cheader( top_ports )
    print >> o, c_variables.getvalue()
    print >> o, c_functions.getvalue()

    # Create the cycle function
    print   >> o, 'unsigned int ncycles;\n'
    print   >> o, '/* cycle */'
    print   >> o, 'void cycle() {'
    for x in sim._sequential_blocks:
      print >> o, '  {}_{}();'.format( x._model.name, x.func_name)
    print   >> o, '  ncycles++;'
    print   >> o, '}'
    print   >> o

    # Create the reset function
    print   >> o, '/* cycle */'
    print   >> o, 'void reset() {'
    print   >> o, '  top_reset = 1;'
    print   >> o, '  cycle();'
    print   >> o, '  flop();'
    print   >> o, '  cycle();'
    print   >> o, '  flop();'
    print   >> o, '  top_reset = 0;'
    print   >> o, '}'
    print   >> o

    # Create the flop function
    print   >> o, '/* flop */'
    print   >> o, 'void flop() {'
    for reg in regs:
      print >> o, ' {0} = {0}_next;'.format( reg )
    print   >> o,   '}'
    print   >> o

    # Create a temporary test thingy
    #print >> o, '// main'
    #print >> o, 'int main () { cycle(); }'

    cdef        = gen_cdef( top_ports )
    CSimWrapper = gen_pywrapper( top_ports )
    return cdef, CSimWrapper


#-------------------------------------------------------------------------
# declare_signals
#-------------------------------------------------------------------------
def declare_signals( sim, regs, o ):

  top_ports    = []
  all_ports    = []

  for id_, n in enumerate( sim._nets ):

    # each net is a set, convert it to a list
    net   = list( n )

    # returns the type, if it is an object/class generate the C def
    type_ = get_type( net[0].msg_type(), o ) # TODO: add obj decl to extern

    # declare the net
    cname = 'net_{:05}'.format( id_ )
    print   >>o, '{}  {} = 0;'.format( type_, cname);

    # create references for each signal connected to the net
    for signal in net:

      name = mangle_name( signal.fullname )
      print >>o, '{} &{}      = {};'     .format( type_, name, cname );

      # only create "next" if this signal was written to in @tick
      # NOTE: this will declare "net_next" twice if two different signals
      #       attached to the net write next; this is okay because that is
      #       invalid code!
      if name in regs:
        print >>o, '{}  {}_next = 0;'      .format( type_, cname );
        print >>o, '{} &{}_next = {}_next;'.format( type_, name, cname );

        all_ports.append( name+'_next' )
      all_ports.append( name )

      # ports attached to top will be exposed in the CSim wrapper
      if name.startswith('top'):
        top_ports.append( (name, cname, type_) );

  return top_ports, all_ports

#-------------------------------------------------------------------------
# get_type
#-------------------------------------------------------------------------
def get_type( signal, o=None ):
  if   isinstance( signal, bool ):
    return 'bool'
  elif isinstance( signal, int ):
    return 'unsigned int'
  elif isinstance( signal, Bits ):
    assert not isinstance( signal, BitStruct )
    return 'unsigned int'    # TODO: make a setbitwidth object
  elif isinstance( signal, SignalValueWrapper ):
    if not o:
      raise Exception( "NESTED TYPES NOT ALLOWED" )
    return declare_class( signal, o )
  else:
    raise Exception( "UNTRANSLATABLE TYPE!")

#-------------------------------------------------------------------------
# declare_class
#-------------------------------------------------------------------------
classes = set()
def declare_class( signal, o ):
  class_name = signal._data.__class__.__name__
  if class_name in classes:
    return class_name
  classes.add( class_name )
  print   >> o, "class {} {{".format( class_name )
  print   >> o, "  public:"
  for name, value in signal._data.__dict__.items():
    print >> o, "    {} {};".format( get_type(value), name );
  print   >> o, "};"
  return class_name

#-------------------------------------------------------------------------
# translate_func
#-------------------------------------------------------------------------

def translate_func( func, o ):

  import StringIO
  behavioral_code = StringIO.StringIO()

  # Type Check the AST
  tree  = get_method_ast( func )
  src   = inspect.getsource( func )
  model = func._model

  #print_simple_ast( tree )                         # DEBUG
  #print src                                        # DEBUG
  #new_tree = TypeAST( model, func ).visit( tree )  # DEBUG
  #print_simple_ast( new_tree )                     # DEBUG

  # Store the PyMTL source inline with the behavioral code
  print   >> behavioral_code, "  // PYMTL SOURCE:"
  for line in src.splitlines():
    print >> behavioral_code, "  // " + line

  # Print the Verilog translation
  visitor = TranslateLogic( model, func, behavioral_code )
  #visitor.visit( new_tree )
  visitor.visit( tree )

  # print behavioral code to passed in
  print >> o
  print >> o, behavioral_code.getvalue()

  # return regs
  return visitor.regs, visitor.localvars

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


  def __init__( self, model, func, o ):
    self.model  = model
    self.func   = func

    self.o      = o
    self.ident  = 0
    self.elseif = False

    self.regs      = []
    self.localvars = {}

    self.assign = '='

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
  def visit_FunctionDef(self, node):

    print >> self.o
    print >> self.o, '  // logic for {}()'.format( self.model.name, node.name )
    print >> self.o, '  void {}_{}() {{'.format( self.model.name, node.name )
    #print >> self.o, '    printf("EXECUTING {}_{}\\n");'.format(
    #                             self.model.name, node.name )
    # Visit each line in the function, translate one at a time.
    self.ident += 2
    for x in node.body:
      self.visit(x)
    self.ident -= 2
    print >> self.o, '  }\n'

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
  # visit_Attribute
  #-----------------------------------------------------------------------
  def visit_Attribute( self, node ):
    name = VariableName( self ).visit( node ).replace('.', '_')

    # TODO: SUPER HACKY
    if   name.endswith('_n'):
      name = name[:-2]+'_next'
    elif name.endswith('_v'):
      name = name[:-2]
    elif name.endswith('_value'):
      name = name[:-6]
    # TODO: SUPER HACKY

    if   name.endswith('_next'):
      self.regs.append( name[:-5] )

    # TODO: more super hacky
    if name not in self.localvars:
      TypeAST( self.model, self.func ).visit( node )
      self.localvars[name] = node._object

    print >> self.o, name,

  #-----------------------------------------------------------------------
  # visit_Name
  #-----------------------------------------------------------------------
  def visit_Name( self, node ):
    name = VariableName( self ).visit( node ).replace('.', '_')

    print >> self.o, name,

  #-----------------------------------------------------------------------
  # visit_Subscript
  #-----------------------------------------------------------------------
  def visit_Subscript( self, node ):
    name = VariableName( self ).visit( node ).replace('.', '_')
    print >> self.o, name,


##  #-----------------------------------------------------------------------
##  # visit_ArrayIndex
##  #-----------------------------------------------------------------------
##  def visit_ArrayIndex(self, node):
##
##    # We don't support ArrayIndexes being slices
##    assert not isinstance( node.slice, _ast.Slice )
##
##    # TODO: need to set ArrayIndex to point to list object
##    # Ugly, by creating portlist?
##    if node.value._object not in self.array:
##      self.array.append( node.value._object )
##
##    # Translate
##    self.visit(node.value)
##    print >> self.o, "[",
##    self.visit(node.slice)
##    print >> self.o, "]",
##
##  #-----------------------------------------------------------------------
##  # visit_BitSlice
##  #-----------------------------------------------------------------------
##  def visit_BitSlice(self, node):
##
##    # Writes to slices need to add the signal as a reg
##    if isinstance( node.ctx, _ast.Store ):
##      self.regs.add( node.value._object )
##
##    # TODO: add support for ranges!
##    self.visit(node.value)
##    print >> self.o, "[",
##    self.visit(node.slice)
##    print >> self.o, "]",
##
##  #-----------------------------------------------------------------------
##  # visit_Slice
##  #-----------------------------------------------------------------------
##  def visit_Slice(self, node):
##    assert node.step == None
##    upper = node.upper
##    lower = node.lower
##    if isinstance( upper, _ast.Num) and isinstance( lower, _ast.Num ):
##      self.visit( node.upper )
##      print >> self.o, '-1:',
##      self.visit( node.lower )
##    # TODO: Hacky attempt at implementing variable part-selects, as
##    #       described here:
##    #       http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-884-complex-digital-systems-spring-2005/related-resources/verilog_2k1paper.pdf
##    elif isinstance( upper, _ast.BinOp ):
##      assert isinstance( upper.op, (_ast.Add, _ast.Sub) )
##      self.visit( node.lower )
##      print >> self.o, '{}:'.format( opmap[type(node.upper.op)] ),
##      self.visit( node.upper.right )
##    else:
##      self.visit( node.upper )
##      print >> self.o, "-1:",
##      self.visit( node.lower )
##      #raise Exception( "Cannot translate this slice!" )
##
  #-----------------------------------------------------------------------
  # visit_Num
  #-----------------------------------------------------------------------
  def visit_Num(self, node):
    print >> self.o, node.n,

#  #-----------------------------------------------------------------------
#  # visit_Self
#  #-----------------------------------------------------------------------
#  # TODO: handle names properly
#  #def visit_Self(self, node):
#  #  self.this_obj = ThisObject( '', self.model )
#  #  self.visit( node.value )
#  #  print >> self.o, self.this_obj.name,
#
#  #-----------------------------------------------------------------------
#  # visit_Local
#  #-----------------------------------------------------------------------
#  # TODO: handle names properly
#  #def visit_Local(self, node):
#  #  obj = getattr( self.model, node.attr )
#  #  self.this_obj = ThisObject( node.attr, obj )
#  #  self.visit( node.value )
#  #  print >> self.o, self.this_obj.name,
#
#  #-----------------------------------------------------------------------
#  # visit_Attribute
#  #-----------------------------------------------------------------------
#  # TODO: currently assuming all attributes are bits objects,
#  #       need to fix for PortBundles and BitStructs
#  def visit_Attribute(self, node):
#    if isinstance( node.ctx, _ast.Store ):
#      self.regs.add( node._object )
#
#    # TODO: hacky
#    if   isinstance( node._object, list ):
#      print >> self.o, node._object[0].name.split('[')[0],
#    # TODO:convert int attributes into contant nodes!
#    elif isinstance( node._object, int ):
#      print >> self.o, node._object,
#    else:
#      print >> self.o, signal_to_str( node._object, None, self.model ),
#
#  #-----------------------------------------------------------------------
#  # visit_Temp
#  #-----------------------------------------------------------------------
#  def visit_Temp(self, node):
#    self.temps.add( node.id )
#    print >> self.o, node.id,
#
##  #-----------------------------------------------------------------------
##  # visit_For
##  #-----------------------------------------------------------------------
##  # TODO: does this work?
##  def visit_For(self, node):
##
##    # TODO: fix to return string..
##    assert isinstance( node.iter, _ast.Slice )
##    i = node.target.id
##
##    # TODO: add support for temporaries declared in for loop
##    print >> self.o, (self.ident+2)*" " + "for ({}=".format(i),
##    self.visit( node.iter.lower )
##    print >> self.o, "; {}<".format(i),
##    self.visit( node.iter.upper )
##    print >> self.o, "; {0}={0}+".format(i),
##    self.visit( node.iter.step )
##    print >> self.o, ")"
##    print >> self.o, (self.ident+2)*" " + "begin"
##    for x in node.body:
##      self.visit(x)
##    print >> self.o, (self.ident+2)*" " + "end"

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
    print >> self.o, " ) {"
    # Write out the body
    for body in node.body:
      self.ident += 2
      self.visit(body)
      self.ident -= 2
    print >> self.o, self.ident*" " + "  }"
    # Write out an an elif block
    if len(node.orelse) == 1 and isinstance(node.orelse[0], _ast.If):
      self.elseif = True
      self.visit(node.orelse[0])
    # Write out an else block
    elif node.orelse:
      print >> self.o, self.ident*" " + "  else {"
      for orelse in node.orelse:
        self.ident += 2
        self.visit(orelse)
        self.ident -= 2
      print >> self.o, self.ident*" " + "  }"

  #--------------------------------------------------------------------
  # visit_While
  #-----------------------------------------------------------------------
  # TODO: does this work?
  def visit_While(self, node):
    print >> self.o, self.ident*" " + "  while( ",
    self.visit( node.test )
    print >> self.o, ") {"
    self.ident += 2
    for line in node.body:
      self.visit( line )
    self.ident -= 2
    print >> self.o, self.ident*" " + "  }"

##  #-----------------------------------------------------------------------
##  # visit_Assert
##  #-----------------------------------------------------------------------
##  def visit_Assert(self, node):
##    print >> self.o, self.ident*" " + "  // ASSERT ",
##    self.visit( node.test )
##    print >> self.o

  #-----------------------------------------------------------------------
  # visit_Call
  #-----------------------------------------------------------------------
  def visit_Call(self, node):

    try:
      if node.func.id not in ['zext']:
        raise Exception('Unsupported function: {}'.format(node.func.id))

      self.visit( node.args[0] )

    except AttributeError as e:
      raise AttributeError('Function call is not a name node!\n'
                           + e.message )

  #-----------------------------------------------------------------------
  # visit_Print
  #-----------------------------------------------------------------------
  def visit_Print( self, node ):
    print >> self.o, self.ident*' ' + 'printf("',
    print >> self.o, '%x '*len( node.values ) + '\\n"',
    for v in node.values:
      print >> self.o, ', ',
      self.visit( v )
    print >> self.o, ' );'

class VariableName( GetVariableName ):
  def __init__( self, parent ):
    self.parent = parent
    self.model  = self.parent.model
  def visit_Name( self, node ):
    if node.id in ['s', 'self']:
      return self.model.name
    else:
      return node.id

