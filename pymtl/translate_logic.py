#=========================================================================
# Verilog Translation Tool
#=========================================================================

from model import *
from PortBundle import PortBundle
import ast, _ast

#=========================================================================
# Python to Verilog Logic Translation
#=========================================================================

class TemporariesVisitor(ast.NodeVisitor):
  """Walks AST looking for temporary variables, infers wires."""

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model):
    """Construct a new TemporariesVisitor."""
    self.model       = model
    self.current_type = None
    self.in_logic     = False
    self.inferring    = False
    self.type_stack   = []
    self.func_ptr     = None

  #-----------------------------------------------------------------------
  # Function Definitions
  #-----------------------------------------------------------------------

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    # Non-decorated function, ignore
    if not node.decorator_list:
      return

    # Combinational and sequential logic blocks
    if node.decorator_list[0].id in ['posedge_clk', 'combinational']:

      # Keep a pointer to this function, need it to find global variables
      # which will be turned into localparams
      self.func_ptr = self.model.__getattribute__( node.name )

      # Visit each line in the function
      self.in_logic = True
      for x in node.body:
        self.visit(x)
      self.in_logic = False

  #-----------------------------------------------------------------------
  # For Loops
  #-----------------------------------------------------------------------

  def visit_For(self, node):
    if not self.in_logic:
      return
    # TODO: create new list of iterators?
    var_name = node.target.id
    self.model._loopvars.append( var_name )

  #-----------------------------------------------------------------------
  # Function Calls
  #-----------------------------------------------------------------------

  def visit_Call(self, node):
    if not self.inferring:
      return

    # TODO: clean this up!!!!
    func, debug = get_target_name( node.func )
    if func == 'zext':
      if not isinstance(node.args[0], _ast.Attribute):
        raise Exception("Parameter to function {}() cannot be an "
                        "expression! Must be a constant!".format(func))
      param, debug = get_target_name( node.args[0] )
      param_value = self.get_signal_type( param )
      self.type_stack.append( Bits(param_value) )
    else:
      raise Exception("Function {}() not supported for translation!"
                      "".format(func) )

  #-----------------------------------------------------------------------
  # Variable Assignments
  #-----------------------------------------------------------------------

  def visit_Assign(self, node):
    """Visit all stores to variables."""
    if not self.in_logic:
      return

    # TODO: implement multiple left hand targets?
    assert len(node.targets) == 1
    target = node.targets[0]
    target_name, debug = get_target_name(target)

    # if debug is false, this is a temporary (doesn't access .value/.next)
    if not debug:

      # Begin inference by walking the AST
      self.inferring = True
      self.visit( node.value )
      self.inferring = False

      # End of walk should result in a single type
      assert len( self.type_stack ) == 1
      temp_type = self.type_stack.pop()

      # Add a check to make sure we aren't overwriting a Port/Wire
      ports_wires = self.model._ports + self.model._wires
      if target_name in [x.name for x in ports_wires]:
        raise Exception("Trying to declare a temporary variable but the "
            "name {} is already used by a port/wire!".format(target_name)
            )

      # If target_name is not in our dict add it
      if target_name not in self.model._tempwires:
        wire = ImplicitWire( target_name, temp_type.width )
        self.model._tempwires[ target_name ] = wire
      # If it is, assert that the inferred types are the same
      elif not isinstance( temp_type, int ):
        current_width = self.model._tempwires[ target_name ].width
        assert temp_type.width == current_width

    # We are trying to write to a submodule's ports, mark these as regs
    # TODO: move to RegisterVisitor?
    # TODO: HACKY
    elif '$' in target_name:
      self.model._tempregs += [ target_name ]

    # TODO: move to RegisterVisitor?
    # TODO: HACKY
    self.visit( node.value )

  #-----------------------------------------------------------------------
  # Get Signal Type
  #-----------------------------------------------------------------------

  def get_signal_type(self, signal_name):

    if '$' in signal_name:
      module_name, signal = signal_name.split('$')
      module = self.model.__dict__[ module_name ]
    else:
      signal = signal_name
      module = self.model

    return module.__dict__[ signal ]

  #-----------------------------------------------------------------------
  # Variable Members
  #-----------------------------------------------------------------------

  def visit_UnaryOp(self, node):
    if self.inferring:
      self.visit(node.operand)
      # DO NOTHING: type of a unary op is just type of object it was op on

  def visit_BoolOp(self, node):
    if self.inferring:
      assert len(node.values) == 2
      self.visit(node.values[0])
      self.visit(node.values[1])
      a = self.type_stack.pop()
      b = self.type_stack.pop()
      c = Bits( max( a.width, b.width ) )
      self.type_stack.append( c )

  def visit_BinOp(self, node):
    if self.inferring:
      self.visit(node.left)
      self.visit(node.right)
      a = self.type_stack.pop()
      b = self.type_stack.pop()
      c = Bits( max( a.width, b.width ) )
      self.type_stack.append( c )

  def visit_Attribute(self, node):
    if self.inferring:
      rhs_name, rhs_debug = get_target_name(node)
      temp_type = self.get_signal_type( rhs_name )
      self.type_stack.append( temp_type )
    # TODO: HACKY, this is how we detect subscripts...
    #       see visit_Subscript()
    else:
      self.visit( node.value )

  # TODO: move to RegisterVisitor?
  # TODO: HACKY
  def visit_Name(self, node):
    # If we find global constants (all caps), make them localparams
    if node.id.isupper():
      node_value = self.func_ptr.func_globals[ node.id ]
      self.model._localparams.add( (node.id, node_value) )

#=========================================================================
# Python to Verilog Logic Translation
#=========================================================================

class PyToVerilogVisitor(ast.NodeVisitor):
  """Hidden class for translating python AST into Verilog source.

  This class takes the AST tree of a Model class and looks for any
  functions annotated with the @combinational decorator. These functions are
  translated into Verilog source (in the form of assign statements).
  """

  #-----------------------------------------------------------------------
  # Supported Logic Operands
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

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model, o):
    """Construct a new PyToVerilogVisitor."""
    self.model       = model
    self.o           = o
    self.write_names = False
    self.block_type  = None
    self.ident       = 0
    self.elseif      = False

  #-----------------------------------------------------------------------
  # Function Definitions
  #-----------------------------------------------------------------------

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    #print node.name, node.decorator_list
    if not node.decorator_list:
      return
    if node.decorator_list[0].id == 'combinational':
      self.block_type = node.decorator_list[0].id
      print >> self.o, '  // logic for {}()'.format( node.name )
      print >> self.o, '  always @ (*) begin'
      # Visit each line in the function, translate one at a time.
      self.ident += 2
      for x in node.body:
        self.visit(x)
      self.ident -= 2
      print >> self.o, '  end\n'
    elif node.decorator_list[0].id == 'posedge_clk':
      self.block_type = node.decorator_list[0].id
      print >> self.o, '  // logic for {}()'.format( node.name )
      print >> self.o, '  always @ (posedge clk) begin'
      # Visit each line in the function, translate one at a time.
      self.ident += 2
      for x in node.body:
        self.visit(x)
      self.ident -= 2
      print >> self.o, '  end\n'

  #-----------------------------------------------------------------------
  # Binary Operators
  #-----------------------------------------------------------------------

  def visit_BinOp(self, node):
    """Visit all binary operators, convert into Verilog operators.

    Parenthesis are placed around every operator along with its args to ensure
    that the order of operations are preserved.
    """
    print >> self.o, '(',
    self.visit(node.left)
    print >> self.o, PyToVerilogVisitor.opmap[type(node.op)],
    self.visit(node.right)
    print >> self.o, ')',

  #-----------------------------------------------------------------------
  # Boolean Operators
  #-----------------------------------------------------------------------

  def visit_BoolOp(self, node):
    """Visit all boolean operators, convert into Verilog operators.

    Parenthesis are placed around every operator along with its args to ensure
    that the order of operations are preserved.
    """
    assert len(node.values) == 2
    print >> self.o, '(',
    self.visit(node.values[0])
    print >> self.o, PyToVerilogVisitor.opmap[type(node.op)],
    self.visit(node.values[1])
    print >> self.o, ')',

  #-----------------------------------------------------------------------
  # Unary Operators
  #-----------------------------------------------------------------------

  def visit_UnaryOp(self, node):
    """Visit all unary operators, convert into Verilog operators.

    Parenthesis are placed around every operator along with its args to ensure
    that the order of operations are preserved.
    """
    print >> self.o, PyToVerilogVisitor.opmap[type(node.op)],
    # node.operand should be either a name or an attribute
    self.visit(node.operand)

  #-----------------------------------------------------------------------
  # Variable Assignments
  #-----------------------------------------------------------------------

  def visit_Assign(self, node):
    """Visit all stores to variables."""
    self.write_names = True
    # TODO: implement multiple left hand targets?
    assert len(node.targets) == 1
    target = node.targets[0]
    target_name, debug = get_target_name(target)
    #if debug:
    if self.block_type == 'combinational':
      print >> self.o, (self.ident+2)*" " + target_name, '=',
      self.visit(node.value)
      print >> self.o, ';'
    elif self.block_type == 'posedge_clk':
      print >> self.o, (self.ident+2)*" " + target_name, '<=',
      self.visit(node.value)
      print >> self.o, ';'
    self.write_names = False

  #-----------------------------------------------------------------------
  # If Statements
  #-----------------------------------------------------------------------

  def visit_If(self, node):
    """Visit all if/elif blocks (not else!)."""
    # Write out the if block
    self.write_names = True
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
    self.write_names = False

  #-----------------------------------------------------------------------
  # Ternary Expressions
  #-----------------------------------------------------------------------

  def visit_IfExp(self, node):
    """Visit all ternary operators (w = x if y else z)."""
    # TODO: verify this works
    self.visit(node.test)
    print >> self.o, '?',
    self.visit(node.body)
    print >> self.o, ':',
    self.visit(node.orelse)

  #-----------------------------------------------------------------------
  # Comparisons
  #-----------------------------------------------------------------------

  def visit_Compare(self, node):
    """Visit all comparisons expressions."""
    # TODO: add write_names check, careful...
    assert len(node.ops) == 1
    # TODO: add debug check
    print >> self.o, "(",
    self.visit(node.left)
    op_symbol = PyToVerilogVisitor.opmap[type(node.ops[0])]
    print >> self.o, op_symbol,
    self.visit(node.comparators[0])
    print >> self.o, ")",

  #-----------------------------------------------------------------------
  # For Loops
  #-----------------------------------------------------------------------

  def visit_For(self, node):
    #if self.write_names:
    i = node.target.id
    iter = node.iter
    assert iter.func.id == 'range'
    assert len( iter.args ) == 1
    start = 0
    step  = 1
    if   isinstance(iter.args[0], _ast.Num):
      end   = iter.args[0].n
    elif isinstance(iter.args[0], _ast.Attribute):
      end   = iter.args[0].attr
    else:
      raise Exception("Unsupported parameter to range()!")
    templ = "    for( {0} = {1}; {0} < {2}; {0} = {0} + {3} )"
    #print >> self.o, "    integer {};".format( i ) # TODO: move above
    print >> self.o, templ.format( i, start, end, step )
    print >> self.o, "    begin"
    for x in node.body:
      self.visit(x)
    print >> self.o, "    end"
    #if self.write_names:
    #  #target_name, debug = get_target_name(node.value)
    #  #print >> self.o, "{}[".format( target_name ),
    #  #self.visit(node.slice)
    #  #print >> self.o, "]",
    #  ##print "  @@@@@",  node.slice

  #-----------------------------------------------------------------------
  # Bit Slices
  #-----------------------------------------------------------------------

  def visit_Subscript(self, node):
    """Visit all variables, convert into Verilog variables."""
    # TODO: add support for ranges!
    if self.write_names:
      target_name, debug = get_target_name(node.value)
      print >> self.o, "{}[".format( target_name ),
      self.visit(node.slice)
      print >> self.o, "]",
      #print "  @@@@@",  node.slice

  #-----------------------------------------------------------------------
  # Variable Names
  #-----------------------------------------------------------------------

  def visit_Name(self, node):
    """Visit all variables, convert into Verilog variables."""
    # TODO: check special cases...
    if self.write_names:
      print >> self.o, node.id,

  #-----------------------------------------------------------------------
  # Variable Members
  #-----------------------------------------------------------------------

  def visit_Attribute(self, node):
    """Visit all attributes, convert into Verilog variables."""
    if self.write_names:
      target_name, debug = get_target_name(node)
      print >> self.o, target_name,

  #-----------------------------------------------------------------------
  # Constants
  #-----------------------------------------------------------------------

  def visit_Num(self, node):
    """Visit all constants."""
    if self.write_names:
      print >> self.o, node.n,

  #-----------------------------------------------------------------------
  # Asserts
  #-----------------------------------------------------------------------

  def visit_Assert(self, node):
    """Visit all asserts."""
    pass
    #print >> self.o, "  // assert ",
    #self.visit( node.test )

  #-----------------------------------------------------------------------
  # Function Calls
  #-----------------------------------------------------------------------

  def visit_Call(self, node):
    if not self.write_names:
      return

    # TODO: clean this up!!!!
    func_list, debug = get_target_list( node.func )
    if func_list[-1] == 'zext':
      param, debug = get_target_name( node.args[0] )
      param_value = self.get_signal_type( param )
      signal_type = self.get_signal_type( func_list[0] )
      ext = param_value - signal_type.width
      # sext
      #print >> self.o, "{{ {{ {0} {{ {1}[{2}] }} }}, {3} }}".format(
      print >> self.o, "{{ {{ {0} {{ 1'b0 }} }}, {1} }}".format(
          ext, func_list[0] ),
      #self.type_stack.append( Bits(param_value) )
    else:
      raise Exception("Function {}() not supported for translation!"
                      "".format(func) )

  def get_signal_type(self, signal_name):

    if '$' in signal_name:
      module_name, signal = signal_name.split('$')
      module = self.model.__dict__[ module_name ]
    else:
      signal = signal_name
      module = self.model

    return module.__dict__[ signal ]

#=========================================================================
# Python to Verilog Logic Translation
#=========================================================================

class FindRegistersVisitor(ast.NodeVisitor):
  """Hidden class finding all registers in the AST of a MTL model.

  In order to translate synchronous @posedge_clk blocks into Verilog, we need
  to declare certain wires as registers.  This visitor looks for all ports
  written in @posedge_clk blocks so they can be declared as reg types.

  """

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model):
    self.model = model

  #-----------------------------------------------------------------------
  # Function Definitions
  #-----------------------------------------------------------------------

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    if not node.decorator_list:
      return
    elif node.decorator_list[0].id in ['posedge_clk', 'combinational']:
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)

  #-----------------------------------------------------------------------
  # Variable Assignments
  #-----------------------------------------------------------------------

  def visit_Assign(self, node):
    """Visit all assigns, searches for synchronous (registered) stores."""
    # @posedge_clk annotation, find nodes we need toconvert to registers
    #if self.add_regs and isinstance(node.op, _ast.LShift):
    assert len(node.targets) == 1
    target = node.targets[0]
    target_list, debug = get_target_list(target)
    if debug:
      # TODO: HACKY, fix me!
      # If len() == 1 this is a signal of the current module, mark is_reg
      # If len() > 1 this is signal either a) belongs to a submodule and
      # should NOT be marked is_reg, or b) belongs to an array of signals
      # and should be marked as is_reg, or c) belongs to a PortBundle and
      # should be markes as is_reg.
      if (len( target_list ) == 1 or isinstance( target_list[-1], int )
         or isinstance( get_target_ptr( self.model, target_list[:-1] ), PortBundle )):
        x = get_target_ptr( self.model, target_list )
        x.is_reg = True
      #else:
      #  print "## LEN > 1", target_list
      #  #self.model._tempregs += [ target_name ]

#------------------------------------------------------------------------
# Signal Name Decoder
#-------------------------------------------------------------------------

def get_target_name(node):

  # Is this a number/constant? Return it.
  if isinstance(node, _ast.Num):
    raise Exception("Ran into a number/constant!")
    return node.n, True

  # Is this an attribute? Follow it until we find a Name.
  name = []
  while isinstance(node, (_ast.Attribute, _ast.Subscript)):
    if   isinstance(node, _ast.Attribute):
      name += [node.attr]
      node = node.value
    elif isinstance(node, _ast.Subscript):
      # assumes this is an integer, not a range
      if isinstance( node.slice.value, _ast.Num ):
        name += [ node.slice.value.n ]
        node = node.value
      elif isinstance( node.slice.value, _ast.Attribute ):
        slice_idx, debug = get_target_name( node.slice.value )
        name += [ [slice_idx] ]
        node = node.value
      elif isinstance( node.slice.value, _ast.Name ):
        name += [ [node.slice.value.id] ]
        node = node.value
      else:
        print type( node.slice.value )
        raise Exception("Untranslatable array/slice index!")

  # We've found the Name.
  assert isinstance(node, _ast.Name)
  name += [node.id]

  # If the target does not access .value or .next, tell the code to ignore it.
  if name[0] in ['value', 'next']:
    # TODO: very very hacky!!!! Fix me!
    try:
      return '$'.join( name[::-1][1:-1] ), True
    except TypeError:
      s = ''
      for x in name[::-1][1:-1]:
        if   isinstance(x, str):  s += '$' + x
        elif isinstance(x, list): s += 'IDX[' + x[0] + ']'
        else:                     s += 'IDX' + str(x)
      return s[1:], True
  elif name[0] in ['sext', 'zext']:
    # TODO: very very hacky!!!! Fix me!
    return name[0], True
  elif name[0] in ['uint', 'int']:
    # TODO: very very hacky!!!! Fix me!
    try:
      return '$'.join( name[::-1][1:-2] ), True
    except TypeError:
      s = ''
      for x in name[::-1][1:-2]:
        if   isinstance(x, str):  s += '$' + x
        elif isinstance(x, list): s += 'IDX[' + x[0] + ']'
        else:                     s += 'IDX' + str(x)
      return s[1:], True
  else:
    return name[0], False


# TODO: SUPER HACKY, replace
def get_target_list(node):

  # Is this a number/constant? Return it.
  if isinstance(node, _ast.Num):
    raise Exception("Ran into a number/constant!")
    return node.n, True

  # Is this an attribute? Follow it until we find a Name.
  name = []
  while isinstance(node, (_ast.Attribute, _ast.Subscript)):
    if   isinstance(node, _ast.Attribute):
      name += [node.attr]
      node = node.value
    elif isinstance(node, _ast.Subscript):
      # TODO: assumes this is an integer, not a range
      if (isinstance( node.slice, _ast.Index) and
          isinstance( node.slice.value, _ast.Num )):
        name += [ node.slice.value.n ]
        node = node.value
      else:
        name += [ '?' ]
        node = node.value

  # We've found the Name.
  assert isinstance(node, _ast.Name)
  name += [node.id]

  # If the target does not access .value or .next, tell the code to ignore it.
  if name[0] in ['value', 'next']:
    return name[::-1][1:-1], True
  else:
    return name[::-1][1:], False

# TODO: SUPER HACKY, replace
def get_target_ptr( model, target_list ):
  obj = model
  for attr in target_list:
    if isinstance(attr, int):
      obj = obj[ attr ]
    else:
      obj = obj.__getattribute__( attr )
  return obj
