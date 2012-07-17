from rtler_vbase import *
import ast

class ToVerilog(object):

  def check_type(self, target, name, obj):
    # If object is a port, add it to our ports list
    if isinstance(obj, VerilogPort):
      obj.name = name
      obj.parent = target.name
      target.ports += [obj]
    # If object is a submodule, add it to our submodules list
    # TODO: change to be a special subclass?
    #elif isinstance(obj, ToVerilog):
    elif isinstance(obj, Synthesizable):
      #obj.name = name
      # TODO: better way to do this?
      obj.type = obj.__class__.__name__
      # TODO: hack, passing None necessary since generate_new also does
      #       refactor to make this unnecessary.  Although... this does
      #       Potentially handle generating class .v files on demand...
      #obj.generate_new(None)
      self.elaborate( obj, name )
      target.submodules += [obj]
    # If object is a list, iterate through items and recursively call
    # check_type()
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

  def elaborate(self, target, iname='toplevel'):
    # TODO: better way to set the name?
    target.class_name = target.__class__.__name__
    target.name = iname
    target.wires = []
    target.ports = []
    target.submodules = []
    # TODO: do all ports first?
    # Get the names of all ports and submodules
    for name, obj in target.__dict__.items():
      # TODO: make ports, submodules, wires _ports, _submodules, _wires
      if (name is not 'ports' and name is not 'submodules'):
        self.check_type(target, name, obj)
    # Verify connections.
    # * All nets that include an input port as a node will use the
    #   the input port as the net name.
    # * All nets that connect a module to an output port will use the
    #   output port as the net name.
    #   Note: is this more complicated than just creating a wire?
    # * All nets that wire two submodule ports together need to create
    #   a wire.

    # PORTS
    # MODULES
    # WIRES

  def generate(self, target, o):
    print >> o, 'module %s' % target.class_name
    # Declare Params
    #if self.params: self.gen_param_decls( self.params, o )
    # Declare Ports
    if target.ports: self.gen_port_decls( target.ports, o )
    # Wires & Instantiations
    self.gen_impl_wires( target, o )
    #if self.wires: self.gen_wire_decls( self.wires, o )
    if target.submodules: self.gen_module_insts( target.submodules, o )
    # Logic
    self.gen_ast( target, o )
    # End module
    print >> o, '\nendmodule\n'

  def gen_port_decls(self, ports, o):
    print >> o, '('
    for p in ports[:-1]:
      print >> o , '  %s,' % p
    p = ports[-1]
    print >> o, '  %s' % p
    print >> o, ');\n'

  def gen_param_decls(self, params, o):
    print >> o, '#('
    for p in params[:-1]:
      print >> o, '  %s,' % p
    p = params[-1]
    print >> o, '  %s' % p
    print >> o, ')'

  def gen_impl_wires(self, target, o):
    for submodule in target.submodules:
      for port in submodule.ports:
        if isinstance(port.connection, VerilogWire):
          break
        for c in port.connection:
          if (    c.type != 'wire'
              and c.type != 'constant'
              and c.type != port.type):
            # TODO: figure out a way to get connection submodule name...
            wire_name = '{0}_{1}_TO_{2}_{3}'.format(submodule.name, port.name,
                                                    c.parent, c.name)
            wire = VerilogWire(wire_name, port.width)
            c.connection = [wire]
            port.connection = [wire]
            print >> o, '  %s' % wire
    #print

  def gen_wire_decls(self, wires, o):
    for w in wires.values():
      print >> o, '  %s' % w

  def gen_module_insts(self, submodules, o):
    for s in submodules:
      print >> o, ''
      print >> o, '  %s %s' % (s.class_name, s.name)
      # TODO: add params
      print >> o, '  ('
      self.gen_port_insts(s.ports, o)
      print >> o, '  );'

  def gen_port_insts(self, ports, o):
    # TODO: hacky! fix p.connection
    for p in ports[:-1]:
      assert len(p.connection) <= 1
      name = p.connection[0].name if p.connection else ' '
      print >> o , '    .%s (%s),' % (p.name, name)
    p = ports[-1]
    assert len(p.connection) <= 1
    name = p.connection[0].name if p.connection else ' '
    print >> o, '    .%s (%s)' % (p.name, name)

  def test_mod(self, v):
    import inspect
    for x,y in inspect.getmembers(v, inspect.ismethod):
      print "Class: ", y.im_class.__name__
      print "Func:  ", y.im_func.__name__
      print y.func_code.co_varnames
      print y.func_globals
      print y.func_globals
      #src = inspect.getsource( y.im_func )
      #print src
      #print ast.parse( src )
      print

  def gen_ast(self, v, o):
    import inspect

      #def visit_Attribute(self, node):
      #  print 'Found Attribute "%s"' % node.s

    #print inspect.getsource( v )  # Doesn't work? Wtf...
    for x,y in inspect.getmembers(v, inspect.isclass):
      src = inspect.getsource( y )
      tree = ast.parse( src )
      PyToVerilogVisitor( o ).visit(tree)
      #for z in ast.walk(tree):
      #  print z, type(z)


class FromVerilog(object):

  def __init__(self, filename):
    fd = open( filename )
    self.params = []
    self.ports  = []
    self.parse_file( fd )
    # TODO: do the same for params?
    for port in self.ports:
      self.__dict__[port.name] = port

  def __repr__(self):
    return "Module(%s)" % self.name

  def parse_file(self, fd):
    start_token = "module"
    end_token   = ");"

    in_module = False
    for line in fd.readlines():
      # Find the beginning of the module definition
      if not in_module and line.startswith( start_token ):
        in_module = True
        self.type = line.split()[1]
        self.name = None
      # Parse parameters
      if in_module and 'parameter' in line:
        self.params += [ VerilogParam( line ) ]
      # Parse inputs
      elif in_module and 'input' in line:
        self.ports += [ VerilogPort( str=line ) ]
      # Parse outputs
      elif in_module and 'output' in line:
        self.ports += [ VerilogPort( str=line ) ]
      # End module definition
      elif in_module and end_token in line:
        in_module = False


class PyToVerilogVisitor(ast.NodeVisitor):
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
    self.write_names = False
    self.o = o

  def visit_FunctionDef(self, node):
    """ Only parse functions that have the @always_comb decorator! """
    #print node.name, node.decorator_list
    if not node.decorator_list:
      return
    if node.decorator_list[0].id == 'always_comb':
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)

  def visit_BinOp(self, node):
    """ Place parens around every operator with args to ensure order
        of operations are preserved.
    """
    print >> self.o, '(',
    self.visit(node.left)
    print PyToVerilogVisitor.opmap[type(node.op)],
    self.visit(node.right)
    print >> self.o, ')',

  def visit_BoolOp(self, node):
    print 'Found BoolOp "%s"' % node.op

  def visit_UnaryOp(self, node):
    print 'Found UnaryOp "%s"' % node.op

  #def visit_Num(self, node):
  #  print 'Found Num', node.n

  def visit_AugAssign(self, node):
    """ Turn <<= symbols into assign statements. """
    # TODO: this turns all comparisons into assign statements! Fix!
    self.write_names = True
    print >> self.o, '  assign', node.target.id, '=',
    self.visit(node.value)
    print >> self.o, ';'
    self.write_names = False

  #def visit_LtE(self, node):
  #def visit_Compare(self, node):
  #  """ Turn <= symbols into assign statements. """
  #  # TODO: this turns all comparisons into assign statements! Fix!
  #  print >> self.o, '  assign', node.left.id, '=',
  #  self.visit(node.comparators[0])
  #  print >> self.o, ';'

  def visit_Name(self, node):
    if self.write_names: print >> self.o, node.id,


#req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
