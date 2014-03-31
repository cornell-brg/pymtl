#=========================================================================
# cpp.py
#=========================================================================
# Tool to translate PyMTL Models into a C simulation object.

from new_pymtl     import *
from cpp_helpers   import gen_cheader, gen_cdef, gen_csim, gen_pywrapper
from ..ast_helpers import get_method_ast, print_simple_ast, print_ast
from ..SignalValue import SignalValueWrapper

import sys
import ast, _ast
import collections
import StringIO
import re

compiler = "g++ -O3 -fPIC -shared -o {libname} {csource}"

#-------------------------------------------------------------------------
# CLogicTransl
#-------------------------------------------------------------------------
# TODO: same as Verilog, reduce code dup
def CLogicTransl( model, o=sys.stdout ):

    # Create the python simulator
    sim = SimulationTool( model )

    c_functions = StringIO.StringIO()
    c_variables = StringIO.StringIO()

    # Visit tick functions, save register information
    ast_next  = []
    localvars = {}
    for func in sim._sequential_blocks:
      r, l = translate_func( func, c_functions )
      ast_next.extend( r )
      localvars.update( l )

    # Print signal declarations, use reg information
    top_ports, all_ports, shadows =  declare_signals( sim, ast_next, c_variables )

    inport_names   = ['top_'+mangle_name(x.name) for x in model.get_inports() ]
    outport_names  = ['top_'+mangle_name(x.name) for x in model.get_outports()]
    top_inports    = []
    top_outports   = []

    for x in model.get_ports():
      x.cpp_name = 'top_'+mangle_name( x.name )

    # Separate input and output ports
    for port in top_ports:
      name = port[0]
      if   name in inport_names:
        top_inports.append( port )
      elif name in outport_names:
        top_outports.append( port )
      #else:
      #    raise Exception("Unknown port detected!")

    # print locals
    print >> c_variables
    print >> c_variables, '/* LOCALS ' + '-'*60 + '*/'
    for var, obj in localvars.items():
      rvar = var.replace('.','_')
      if rvar not in all_ports:
        if   isinstance( obj, int ):
          var_type = get_type( obj, o )
          print >> c_variables, "{} {} = {};".format( var_type, rvar, obj )
        # TODO: super hacky handling of lists
        elif isinstance( obj, list ):
          var_type = get_type( obj[0], o )
          split = var.split('.')
          pfx = '_'.join( split[0:2] )
          sfx = '_'+'_'.join( split[2:]  ) if split[2:] else ''
          vx = [ '&{}_IDX{:03}{}'.format(pfx,i,sfx) for i in range(len(obj)) ]
          # Declare the variables if they don't exist yet
          for x in vx:
            if x[1:] not in all_ports:
              print >> c_variables, "{} {};".format( var_type, x[1:])
          print >> c_variables, "{} * {}[] = {{ {} }};".format(
              var_type, rvar, ', '.join(vx ) )
        else:
          var_type = get_type( obj, o )
          print >> c_variables, "{} {};".format( var_type, rvar )


    # Declare parameters
    params = []
    for name, net, type_ in top_inports[:2]:
      params.append( '    {}   _{}'.format( type_, name ) )
    params  .append( '    iface_t * top') 
    params = ',\n'.join( params )

    # Create the C header
    print >> o, '#include <stdio.h>'
    print >> o, '#include <assert.h>'
    print >> o, '#include <queue>'
    print >> o, '#define  True  true'
    print >> o, '#define  False false'
    print >> o

    print >> o, gen_cheader( params, top_ports[2:] )
    print >> o, c_variables.getvalue()
    print >> o, c_functions.getvalue()

    print   >> o, 'unsigned int ncycles;\n\n'

    # Create the cycle function
    print   >> o, '/* cycle */'
    print   >> o, 'void cycle({}) {{'.format( '\n'+params+'\n' )

    # Set input ports from params
    print   >> o
    print   >> o, '  /* Set inports */'
    print   >> o, '  top_clk   = _top_clk;'
    print   >> o, '  top_reset = _top_reset;'
    for name, _, _ in top_inports[2:]:
      print >> o, '  {} = top->{};'.format( name, name[4:] )

    # Execute all ticks
    print   >> o
    print   >> o, '  /* Execute all ticks */'
    for x in sim._sequential_blocks:
      print >> o, '  {}_{}();'.format( mangle_idxs(x._model.name), x.func_name)
    print   >> o, '  ncycles++;'

    # Update all registers
    print   >> o
    print   >> o, '  /* Update all registers */'
    for s in shadows:
      print >> o, '  {0} = {0}_next;'.format( s )

    # Update params from output ports
    print   >> o
    print   >> o, '  /* Assign all outputs */'
    for name, _, _ in top_outports:
      print >> o, '  top->{} = {};'.format( name[4:], name )

    print   >> o, '}'
    print   >> o

    # Create the cdef and Python wrapper
    cdef        = gen_cdef( params, top_ports[2:] )
    CSimWrapper = gen_pywrapper( top_inports, top_outports )

    return cdef, CSimWrapper


#-------------------------------------------------------------------------
# declare_signals
#-------------------------------------------------------------------------
def declare_signals( sim, ast_next, o ):

  clk_port     = None
  reset_port   = None
  top_ports    = []
  all_ports    = []

  shadows = []
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
      print >>o, '{} &{}      =  {};'      .format( type_, name, cname );

      # only create "next" if this signal was written to in @tick
      # NOTE: this will declare "net_next" twice if two different signals
      #       attached to the net write next; this is okay because that is
      #       invalid code!
      sig = re.sub('\[[0-9]*\]', '', signal.name)
      mod = mangle_idxs( signal.parent.name )
      fullname = mod + '.' + sig
      if fullname in ast_next:
        print >>o, '{}  {}_next = 0;'      .format( type_, cname );
        print >>o, '{} &{}_next = {}_next;'.format( type_, name, cname );
        shadows.append( name )

        all_ports.append( name+'_next' )
      all_ports.append( name )

      # ports attached to top will be exposed in the CSim wrapper
      # special case clock/reset, since they won't be exposed, want them
      # to be known locations in the cycle(...) function call
      if   name == 'top_clk':
        clk_port   = (name, cname, type_)
      elif name == 'top_reset':
        reset_port = (name, cname, type_)
      elif name.startswith('top'):
        print >>o, '{} *   _{}      = &{};'.format( type_, name[4:], cname );
        top_ports.append( (name, cname, type_) );

  top_ports = [clk_port, reset_port] + sorted(top_ports)

  return top_ports, all_ports, shadows

#-------------------------------------------------------------------------
# get_type
#-------------------------------------------------------------------------
from new_pmlib.queues import Queue
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
  elif isinstance( signal, list ):
    return get_type( signal[0], o ) + ' *'
  elif signal == None:
    return 'void *'
  # TODO: super hacky handling of generics
  elif isinstance( signal, Queue ):
    return 'std::queue<'+ get_type( signal._kind )+ '>'
  else:
    raise Exception( "UNTRANSLATABLE TYPE!")
    #print( "UNTRANSLATABLE TYPE!")

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

def translate_func( func, o, model=None ):

  import StringIO
  behavioral_code = StringIO.StringIO()

  # Type Check the AST
  tree, src = get_method_ast( func )
  if not model:
    model = func._model

  tree = RemoveCopy().visit( tree )
  tree = ReorderSubscriptNext().visit( tree )
  #print_simple_ast( tree )                         # DEBUG
  InferTypes( model, func ).visit( tree )
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

  regs      = []
  localvars = {}
  for f in visitor.funcs:
    x, y = translate_func( f, o, model )
    regs.extend( x )
    localvars.update( y )

  # print behavioral code to passed in
  print >> o
  print >> o, behavioral_code.getvalue()

  # return regs
  regs.extend( visitor.regs )
  localvars.update( visitor.localvars )
  return regs, localvars

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
    self.arrays    = []
    self.funcs     = []

    self.assign = '='

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
  def visit_FunctionDef(self, node):
    assert node.args.vararg == None
    assert node.args.kwarg  == None
    # TODO: hacky typing: first argument should be self=<returntype>
    #                     following args should have default value

    if node.args.args:
      rtype = 'int'
      args = []
      stash = self.o
      self.o = StringIO.StringIO()
      for x, y in zip(node.args.defaults[1:], node.args.args[1:]):
        self.visit( x )
        args.append( "{} {}".format( 'int', y.id ) )
      self.o = stash
    else:
      rtype = 'void'
      args  = []

    print >> self.o
    print >> self.o, '  // logic for {}()'.format( self.model.name, node.name )
    print >> self.o, '  {} {}_{}( {} ) {{'.format(
        rtype,
        mangle_idxs(self.model.name),
        node.name,
        ', '.join(args)
        )
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
    name = mangle_idxs( VariableName( self ).visit( node ) )

    # TODO: SUPER HACKY
    if   name.endswith('.n'):
      name = name[:-2]+'.next'
    elif name.endswith('.v'):
      name = name[:-2]
    elif name.endswith('.value'):
      name = name[:-6]
    # TODO: SUPER HACKY

    if   name.endswith('.next'):
      self.regs.append( name[:-5] )

    # TODO: more super hacky
    if name not in self.localvars:
      #TypeAST( self.model, self.func ).visit( node )
      self.localvars[name] = node._object

    print >> self.o, name.replace('.','_'),

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
    print >> self.o, '(*',
    self.visit( node.value )
    print >> self.o, '[',
    self.visit( node.slice )
    print >> self.o, '])',

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
    node._object = int( node.n )
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
  #-----------------------------------------------------------------------
  # visit_For
  #-----------------------------------------------------------------------
  # TODO: does this work?
  def visit_For(self, node):

    #try:
      if node.iter.func.id != 'range':
        raise AttributeError()

      args    = node.iter.args
      lower   = args[0] if len( args ) > 1 else _ast.Num(0)
      upper   = args[1] if len( args ) > 1 else args[0]
      step    = args[2] if len( args ) > 2 else _ast.Num(1)
      i       = node.target.id

      print  >> self.o, (self.ident+2)*" " + "for (int {}=".format(i),
      self.visit( lower )
      print  >> self.o, "; {}<".format(i),
      self.visit( upper )
      print  >> self.o, "; {0}={0}+".format(i),
      self.visit( step )
      print  >> self.o, ") { "
      for x in node.body:
        self.visit(x)
      print  >> self.o, (self.ident+2)*" " + "}"

    #except AttributeError as e:
    #  raise Exception("For can only loop over range()! " + e.message)


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
      print >> self.o, ';'
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
        print >> self.o, ';'
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

  #-----------------------------------------------------------------------
  # visit_Assert
  #-----------------------------------------------------------------------
  def visit_Assert(self, node):
    print >> self.o, self.ident*' ' + '  assert(',
    self.visit( node.test )
    print >> self.o, ')',

  #-----------------------------------------------------------------------
  # visit_Return
  #-----------------------------------------------------------------------
  def visit_Return(self, node):
    print >> self.o, self.ident*' ' + '  return ',
    if node.value:
      self.visit( node.value )
    print >> self.o, ';'

  #-----------------------------------------------------------------------
  # visit_Call
  #-----------------------------------------------------------------------
  def visit_Call(self, node):

    # Free function calls
    if   isinstance( node.func, _ast.Name ):
      if   node.func.id == 'zext':
        self.visit( node.args[0] )
      elif node.func.id == 'hex':
        self.visit( node.args[0] )
      elif node.func.id == 'len':
        print >> self.o, "(",
        self.visit( node.args[0] )
        print >> self.o, ".size())",
      else:
        raise Exception('Unsupported free function: {}'.format(node.func.id))

    # Method Calls
    elif isinstance( node.func, _ast.Attribute ):

      if hasattr( self.model, node.func.attr ):
        self.funcs.append( getattr( self.model, node.func.attr ) )
        fname = node.func.attr
        print >> self.o, "{}_{}(".format( mangle_idxs(self.model.name),
                                          fname ),
        for i, arg in enumerate( node.args ):
          if i != 0: print >> self.o, ","
          self.visit( node.args[i] )
        print >> self.o, ")",
        return

      print >> self.o, "(",
      self.visit( node.func.value )

      # TODO
      # print "METHODCALL", node.func.attr,
      # node.func.value._object.__class__.__name__
      if   node.func.attr == 'popleft':
        print >> self.o, ".pop()",
      elif node.func.attr == 'append':
        print >> self.o, ".push("
        self.visit( node.args[0] )
        print >> self.o, ")",
      # Queue
      elif node.func.attr == 'is_full':
        maxlen = node.func.value._object.data.maxlen
        print >> self.o, ".size() == {}".format(maxlen),
      elif node.func.attr == 'is_empty':
        print >> self.o, ".empty()",
      elif node.func.attr == 'peek':
        print >> self.o, ".front()",
      elif node.func.attr == 'deq':
        print >> self.o, ".pop()",
      elif node.func.attr == 'enq':
        print >> self.o, ".push(",
        self.visit( node.args[0] )
        if isinstance( node.func.value._object, list ):
          for i in node.func.value._object:
            i._kind = node.args[0]._object
        else:
          node.func.value._object._kind = node.args[0]._object
        print >> self.o, ")",
      else:
        raise Exception('Unsupported method: {}'.format(node.func.attr))

      print >> self.o, ")",

    else:
      raise Exception('Attempting to call a non-name! {}\n'
                      .format(node.func))

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

class VariableName( ast.NodeVisitor ):
  def __init__( self, parent ):
    self.parent = parent
    self.model  = self.parent.model

  def visit_Attribute( self, node ):
    return self.visit( node.value ) + '.' + node.attr

  def visit_Subscript( self, node ):
    stash = self.parent.o
    import StringIO
    self.parent.o = StringIO.StringIO()
    self.parent.visit( node )
    val = self.parent.o.getvalue()
    self.parent.o = stash
    return val

  def visit_Self( self, node ):
    return self.model.name

  def visit_Name( self, node ):
    if node.id in ['s', 'self']:
      return self.model.name
    else:
      return node.id

#-------------------------------------------------------------------------
# ReorderSubscriptNext
#-------------------------------------------------------------------------
class ReorderSubscriptNext( ast.NodeTransformer ):
  def __init__( self ):
    self.call = False

  def visit_Call( self, node ):
    # TODO: specially handle self.visit( node.func ) if attr
    #       currently not visiting at all!
    args     = [self.visit(x) for x in node.args]
    keywords = [self.visit(x) for x in node.keywords]
    if node.starargs:
      starargs = [self.visit(x) for x in node.starargs]
    else:
      starargs = None
    if node.kwargs:
      kwargs = [self.visit(x) for x in node.kwargs]
    else:
      kwargs = None

    return _ast.Call(func=node.func,
                     args=args,
                     keyword=keywords,
                     starargs=starargs,
                     kwargs=kwargs)

  def visit_Attribute( self, node ):
    self.generic_visit( node )
    if isinstance(node.value, _ast.Subscript):
      subscript       = node.value
      node.value      = subscript.value
      subscript.value = node
      return ast.copy_location( subscript, node )

    return node

class RemoveCopy( ast.NodeTransformer ):

  def visit_Call( self, node ):
    self.generic_visit( node )
    if isinstance(node.func, _ast.Name) and node.func.id == "copy":
      return ast.copy_location( node.args[0], node )
    return node

#-------------------------------------------------------------------------
# InferTypes
#-------------------------------------------------------------------------
class InferTypes( ast.NodeVisitor ):

  def __init__( self, model, func ):
    self.model       = model
    self.func        = func
    self.closed_vars = get_closure_dict( func )
    self.current_obj = None
    if not self.closed_vars:
      self.closed_vars['s'] = model

  def visit_Subscript( self, node ):
    self.visit( node.slice )
    self.visit( node.value )
    node._object = node.value._object[0]

    return node

  def visit_Attribute( self, node ):
    # First visit all children
    self.generic_visit( node )

    # TODO: temporary, only handle objects that are live
    assert self.current_obj != None

    # Try to get the object by loading it
    try:
      x = self.current_obj.getattr( node.attr )
      self.current_obj.update( node.attr, x )
    except AttributeError:
      if node.attr not in ['next', 'value', 'n', 'v']:
        raise Exception("Error: Unknown attribute for this object: {}"
                        .format( node.attr ) )


    node._object = self.current_obj.inst if self.current_obj else None
    return node

  def visit_Name( self, node ):

    # TODO: temporary, don't handle local temporaries
    if node.id in self.closed_vars:
      new_node = node
      new_obj  = PyObj( node.id, self.closed_vars[ node.id ] )
    else:
      print "WARNING: variable {} type is unknown".format( node.id )
      new_obj  = None

    self.current_obj = new_obj
    node._object = self.current_obj.inst if self.current_obj else None


class PyObj( object ):
  def __init__( self, name, inst ):
    self.name  = name
    self.inst  = inst
  def update( self, name, inst ):
    self.name += name
    self.inst  = inst
  def getattr( self, name ):
    if isinstance( self.inst, list ):
      # TODO: super hacky, not sure why this works for forloop
      if name not in ['next', 'value', 'n', 'v']:
        return [getattr( x, name ) for x in self.inst]
      return getattr( self.inst, name )
    return getattr( self.inst, name )
  def __repr__( self ):
    return "PyObj( name={} inst={} )".format( self.name, type(self.inst) )

#------------------------------------------------------------------------
# get_closure_dict
#------------------------------------------------------------------------
# http://stackoverflow.com/a/19416942
def get_closure_dict( fn ):
  if fn.func_closure:
    closure_objects = [c.cell_contents for c in fn.func_closure]
    return dict( zip( fn.func_code.co_freevars, closure_objects ))
  else: return dict()

#------------------------------------------------------------------------
# mangle_idxs
#------------------------------------------------------------------------
indexing = re.compile("(\[)(?P<idx>.*?)(\])")
def mangle_idxs( name ):
  def replacement_string( m ):
    return "_IDX{:03d}".format( int(m.group('idx')) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name )

#-------------------------------------------------------------------------
# mangle_name
#-------------------------------------------------------------------------
def mangle_name( name ):
  # Utility function
  def replacement_string( m ):
    return "_IDX{:03d}".format( int(m.group('idx')) )
  # Return the mangled name
  return re.sub( indexing, replacement_string, name.replace('.','_') )

# Regex to match list indexing
indexing = re.compile("(\[)(?P<idx>.*?)(\])")


