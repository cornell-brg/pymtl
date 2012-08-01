"""Tool for translating MTL models to and from HDL source.

This module contains classes which translate between MTL models and various
hardware description languages, such as Verilog.
"""

from pymtl_model import *
import inspect
import ast, _ast

class ToVerilog(object):

  """User visible class for translating MTL models into Verilog source."""

  def __init__(self, model):
    """Construct a Verilog translator from a MTL model.

    Parameters
    ----------
    model: an instantiated MTL model (Model).
    """
    self.model = model
    self.generated = set()

  def generate(self, o, target=None):
    """Generates Verilog source from a MTL model.

    Calls gen_port_decls(), gen_impl_wires(), gen_module_insts(), and gen_ast()
    as necessary.

    Parameters
    ----------
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    if not target:
      target = self.model
    print >> o, 'module %s' % target.class_name
    # Declare Params
    #if self.params: self.gen_param_decls( self.params, o )
    # Find Registers
    self.get_regs( target, o )
    # Declare Ports
    if target._ports: self.gen_port_decls( target._ports, o )
    # Wires & Instantiations
    self.gen_impl_wires( target, o )
    #if self.wires: self.gen_wire_decls( self.wires, o )
    if target._submodules: self.gen_module_insts( target._submodules, o )
    # Logic
    self.gen_ast( target, o )
    # Port assignments
    self.gen_port_assigns( target, o )
    # End module
    print >> o, '\nendmodule\n'

    self.generated.add( target.class_name )
    for m in target._submodules:
      if m.class_name not in self.generated:
        self.generate(o, m)

  def gen_port_decls(self, ports, o):
    """Generate Verilog source for port declarations.

    Parameters
    ----------
    ports: list of VerilogPort objects.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    print >> o, '('
    for p in ports[:-1]:
      print >> o , '  %s,' % self.port_to_str(p)
    p = ports[-1]
    print >> o, '  %s' % self.port_to_str(p)
    print >> o, ');\n'

  def gen_param_decls(self, params, o):
    """Generate Verilog source for parameter declarations.

    Parameters
    ----------
    params: list of VerilogParam objects.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    print >> o, '#('
    for p in params[:-1]:
      print >> o, '  %s,' % p
    p = params[-1]
    print >> o, '  %s' % p
    print >> o, ')'

  def gen_impl_wires(self, target, o):
    """Creates a list of implied wire objects from connections in the MTL model.

    The MTL modeling framework allows you to make certain connections between
    ports without needing to explicitly declare intermediate wires. In some
    cases Verilog requires these wire declarations to be explicit. This utility
    method attempts to infer these implicit wires, generate Wire objects
    from them, and then add them to the connectivity lists of the necessary
    ports.

    Parameters
    ----------
    target: a Model instance.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    for submodule in target._submodules:
      for port in submodule._ports:
        if isinstance(port.connections, Wire):
          break
        c = self.get_parent_connection(port)
        # If we found a parent connection, no wire is required
        if c:
          port.inst_connection = c
        # If there's no parent connection, create a wire
        # TODO: why is this a loop? Shouldnt there only be one?
        else:
          for c in port.connections:
            if (not port.inst_connection
                and c.type != 'wire'
                and c.type != 'constant'
                and c.type != port.type):
              # set names based on directionality
              if isinstance(port, OutPort):
                wire_name = '{0}_{1}_TO_{2}_{3}'.format(
                    submodule.name, port.name, c.parent.name, c.name)
              else:
                wire_name = '{0}_{1}_TO_{2}_{3}'.format(
                    c.parent.name, c.name, submodule.name, port.name)
              wire = Wire(wire_name, port.width)
              c.inst_connection = wire
              port.inst_connection = wire
              # TODO: move to gen_wire_decls
              print >> o, '  %s' % self.wire_to_str(wire)

  def gen_wire_decls(self, wires, o):
    """Generate Verilog source for wire declarations.

    Parameters
    ----------
    wires: list of Wire objects.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    for w in wires.values():
      print >> o, '  %s' % self.wire_to_str(w)

  def gen_port_assigns(self, target, o):
    """Generate Verilog source for assigning values to output ports.

    Infers which output ports require assign statements based on connectivity,
    then generates source as necessary.

    Parameters
    ----------
    target: a Model instance.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    # Utility function
    def needs_assign(port, connection):
      if isinstance(connection, Slice):
        return port.parent == connection.connections[0].parent
      else:
        return port.parent == connection.parent
    # Get all output ports
    output_ports = [x for x in target._ports if isinstance(x,OutPort)]
    for port in output_ports:
      output_assigns = [x for x in port.connections if needs_assign(port, x)]
      for assign in output_assigns:
        # Handle the case where we are assigning to an output slice...
        if assign.type == 'output':
          assert len(assign.connections) == 1
          left  = assign.name
          right = assign.connections[0].name
        else:
          left  = port.name
          right = assign.name
        print  >> o, "  assign {0} = {1};".format(left, right)

  def gen_module_insts(self, submodules, o):
    """Generate Verilog source for instantiated submodules.

    Parameters
    ----------
    submodules: list of Model objects.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    for s in submodules:
      print >> o, ''
      print >> o, '  %s %s' % (s.class_name, s.name)
      # TODO: add params
      print >> o, '  ('
      self.gen_port_insts(s._ports, o)
      print >> o, '  );'

  def gen_port_insts(self, ports, o):
    """Generate Verilog source for submodule port instances.

    Parameters
    ----------
    ports: list of VerilogPort objects.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    # TODO: hacky! fix p.connection
    for p in ports[:-1]:
      name = p.inst_connection.name if p.inst_connection else ' '
      print >> o , '    .%s (%s),' % (p.name, name)
    p = ports[-1]
    name = p.inst_connection.name if p.inst_connection else ' '
    print >> o, '    .%s (%s)' % (p.name, name)

  def get_parent_connection(self, port):
    """Utility method to find the parent connection in the connection list.

    Currently all VerilogPort objects maintain a list of all other ports they
    are connected to.  If a given VerilogPort is in the middle of a hierarchy,
    ie. when a module A instantiates submodule B, and submodule B instantiates
    another submodule C, the connections list will contain connections to both
    parents and children.  When printing out the instantiation of submodule B,
    we need to know which of the connections leads to the parent so we can
    attach it to module B's port list.  This method attempts to find the parent
    connection by walking though all the port connections and checking them
    one-by-one.

    Parameters
    ----------
    port: a VerilogPort object.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    # TODO: separate connections into inst_cxt and impl_cxn
    # No connection, return none
    if not port.connections:
      return None
    # Look in connections for any parent connections
    for connection in port.connections:
      if port.parent.parent == connection.parent:
        return connection
    # No parent connections
    return None

  def port_to_str(self, p):
    """Generate Verilog source for a port declaration.

    Parameters
    ----------
    p: a Port object.
    """
    reg = 'reg' if p.is_reg else ''
    if p.width == 1:
      return "%s %s %s" % (p.type, reg, p.name)
    else :
      return "%s %s [%d:0] %s" % (p.type, reg, p.width-1, p.name)

  def wire_to_str(self, w):
    """Generate Verilog source for a wire declaration.

    Parameters
    ----------
    w: a Wire object.
    """
    if w.width == 1:
      return "wire %s;" % (w.name)
    else :
      return "wire [%d:0] %s;" % (w.width-1, w.name)

  def get_regs(self, v, o):
    """Find which wires/ports should be Verilog reg type.

    Parameters
    ----------
    target: a Model instance.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    reg_stores = set()

    model_class = v.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    FindRegistersVisitor( reg_stores ).visit(tree)
    for reg_name in reg_stores:
      port_ptr = v.__getattribute__(reg_name)
      port_ptr.is_reg = True

  def gen_ast(self, v, o):
    """Generate Verilog source from decorated python functions.

    Currently supports the @combinational and @posedge_clk decorators.

    Parameters
    ----------
    target: a Model instance.
    o: the output object to write Verilog source to (ie. sys.stdout).
    """
    #print inspect.getsource( v )  # Doesn't work? Wtf...
    #for x,y in inspect.getmembers(v, inspect.ismethod):
    for x,y in inspect.getmembers(v, inspect.isclass):
      src = inspect.getsource( y )
      tree = ast.parse( src )
      PyToVerilogVisitor( o ).visit(tree)


class PyToVerilogVisitor(ast.NodeVisitor):
  """Hidden class for translating python AST into Verilog source.

  This class takes the AST tree of a Model class and looks for any
  functions annotated with the @combinational decorator. These functions are
  translated into Verilog source (in the form of assign statements).

  TODO: change assign statements to "always @ *" blocks?
  """

  opmap = {
      ast.Add      : '+',
      ast.Sub      : '-',
      ast.Mult     : '*',
      ast.Div      : '/',
      ast.Mod      : '%',
      ast.Pow      : '**',
      ast.LShift   : '<<',
      ast.RShift   : '>>>',
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

  def __init__(self, o):
    """Construct a new PyToVerilogVisitor.

    Parameters
    ----------
    o: the output object to write to (ie. sys.stdout).
    """
    self.write_names = False
    self.block_type  = None
    self.o = o

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    #print node.name, node.decorator_list
    if not node.decorator_list:
      return
    if node.decorator_list[0].id == 'combinational':
      self.block_type = node.decorator_list[0].id
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)
    elif node.decorator_list[0].id == 'posedge_clk':
      self.block_type = node.decorator_list[0].id
      print >> self.o, ' always @ (posedge clk) begin'
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)
      print >> self.o, ' end'

  def visit_BinOp(self, node):
    """Visit all binary operators, convert into Verilog operators.

    Parenthesis are placed around every operator along with its args to ensure
    that the order of operations are preserved.
    """
    print >> self.o, '(',
    self.visit(node.left)
    print PyToVerilogVisitor.opmap[type(node.op)],
    self.visit(node.right)
    print >> self.o, ')',

  def visit_BoolOp(self, node):
    """Visit all boolean operators, TODO: UNIMPLEMENTED."""
    print 'Found BoolOp "%s"' % node.op

  def visit_UnaryOp(self, node):
    """Visit all unary operators, TODO: UNIMPLEMENTED."""
    print 'Found UnaryOp "%s"' % node.op

  #def visit_Num(self, node):
  #  print 'Found Num', node.n

  def visit_AugAssign(self, node):
    """Visit all special assigns, convert <<= ops into assign statements.

    TODO: instead of assign statements, convert into "always @ *" assignments.
    """
    # TODO: this turns all comparisons into assign statements! Fix!
    self.write_names = True
    if self.block_type == 'combinational':
      print >> self.o, '  assign', node.target.id, '=',
      self.visit(node.value)
      print >> self.o, ';'
    elif self.block_type == 'posedge_clk':
      print >> self.o, ' ', node.target.id, '<=',
      self.visit(node.value)
      print >> self.o, ';'
    self.write_names = False

  #def visit_Compare(self, node):
  #  """Visit all comparisons assigns, convert into Verilog operators."""
  #  print 'Found Comparison "%s"' % node.op

  def visit_Name(self, node):
    """Visit all variables, convert into Verilog variables."""
    if self.write_names: print >> self.o, node.id,


class FindRegistersVisitor(ast.NodeVisitor):
  """Hidden class finding all registers in the AST of a MTL model.

  In order to translate synchronous @posedge_clk blocks into Verilog, we need
  to declare certain wires as registers.  This visitor looks for all ports
  written in @posedge_clk blocks so they can be declared as reg types.

  TODO: factor this and SensitivityListVisitor into same file?
  """
  def __init__(self, reg_stores):
    """Construct a new SensitivityListVisitor.

    Parameters
    ----------
    reg_stores: a set() object, (var_name, func_name) tuples will be added to
                this set for all variables updated inside @posedge_clk blocks
                (via the <<= operator)
    """
    self.reg_stores = reg_stores

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    if not node.decorator_list:
      return
    elif node.decorator_list[0].id == 'posedge_clk':
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)

  def visit_AugAssign(self, node):
    """Visit all aug assigns, searches for synchronous (registered) stores."""
    # @posedge_clk annotation, find nodes we need toconvert to registers
    #if self.add_regs and isinstance(node.op, _ast.LShift):
    if isinstance(node.op, _ast.LShift):
      self.reg_stores.add( node.target.id )


#req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
