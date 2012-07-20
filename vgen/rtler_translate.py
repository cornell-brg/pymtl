from rtler_vbase import *
import ast

class ToVerilog(object):

  def __init__(self, model):
    self.model = model

  def generate(self, o):
    target = self.model
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
        if isinstance(port.connections, VerilogWire):
          break
        for c in port.connections:
          if (    c.type != 'wire'
              and c.type != 'constant'
              and c.type != port.type):
            # TODO: figure out a way to get connection submodule name...
            wire_name = '{0}_{1}_TO_{2}_{3}'.format(submodule.name, port.name,
                                                    c.parent.name, c.name)
            wire = VerilogWire(wire_name, port.width)
            c.connections = [wire]
            port.connections = [wire]
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
      name = self.get_parent_connection(p)
      #assert len(p.connections) <= 1
      #name = p.connections[0].name if p.connections else ' '
      print >> o , '    .%s (%s),' % (p.name, name)
    p = ports[-1]
    name = self.get_parent_connection(p)
    #assert len(p.connections) <= 1
    #name = p.connections[0].name if p.connections else ' '
    print >> o, '    .%s (%s)' % (p.name, name)

  # TODO: separate connections into inst_cxt and impl_cxn
  def get_parent_connection(self, port):
    if not port.connections:
      return ''
    if len(port.connections) == 1:
      return port.connections[0].name
    for connection in port.connections:
      if port.parent.parent == connection.parent:
        return connection.name


  def gen_ast(self, v, o):
    import inspect

      #def visit_Attribute(self, node):
      #  print 'Found Attribute "%s"' % node.s

    #print inspect.getsource( v )  # Doesn't work? Wtf...
    #for x,y in inspect.getmembers(v, inspect.ismethod):
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
    if node.decorator_list[0].id == 'combinational':
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
