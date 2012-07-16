import sys
import ast
from rtler_vast import PyToVerilogVisitor
from rtler_sim import LogicSim

sim = LogicSim()
debug = False

class ValueNode(object):
  #def __init__(self, width, value='X'):
  def __init__(self, width, value=0):
    self.width = width
    self.value = value
    self.funcs = set()

class VerilogSlice(object):
  def __init__(self, parent_ptr, width, addr):
    self.parent_ptr = parent_ptr
    self.width      = width
    self.addr       = addr

  @property
  def parent(self):
    return self.parent_ptr.parent

  @property
  def name(self):
    suffix = '[%d]' % self.addr
    return self.parent_ptr.name + suffix

  #TODO: hacky...
  @property
  def type(self):
    return self.parent_ptr.type

  @property
  def connection(self):
    return self.parent_ptr.connection
  @connection.setter
  def connection(self, target):
    self.parent_ptr.connection += [target]

  @property
  def funcs(self):
    return self.parent_ptr.funcs
  #@funcs.setter
  #def funcs(self, value):
  #  self.parent_ptr.funcs = value

  @property
  def value(self):
    if self.parent_ptr.value != 'X':
      temp = ((self.parent_ptr.value) & (1 << self.addr)) >> self.addr
      return temp
    else:
      return self.parent_ptr.value
  @value.setter
  def value(self, value):
    if self.parent_ptr.value != 'X':
      self.parent_ptr.value |= (value << self.addr)
    else:
      self.parent_ptr.value = value

  @property
  def _value(self):
    return self.parent_ptr._value
  @_value.setter
  def _value(self, value):
    self.parent_ptr._value = value

class VerilogPort(object):

  def __init__(self, type=None, width=None, name='???', str=None):
    self.type  = type
    self.width = width
    self.name  = name
    self.parent = '???'
    self.connection = []
    self._value     = None
    self.funcs      = set()
    if str:
      self.type, self.width, self.name  = self.parse( str )

  def __repr__(self):
    return "Port(%s, %s, %s)" % (self.type, self.width, self.name)

  def __str__(self):
    if isinstance(self.width, str):
      return "%s %s %s" % (self.type, self.width, self.name)
    elif isinstance(self.width, int):
      if self.width == 1:
        return "%s %s" % (self.type, self.name)
      else :
        return "%s [%d:0] %s" % (self.type, self.width-1, self.name)

  def __ne__(self, target):
    self.connect(target)

  def __xor__(self, target):
    # TODO: super hacky!!!!
    #temp = VerilogPort(name='xor_temp')
    #print type(self), self.parent+'.'+self.name, self.value, 'xor',
    #print type(target), target.parent+'.'+target.name, target.value
    #temp.value = self.value ^ target.value
    temp = self.value ^ target.value
    return temp

  def __rxor__(self, target):
    #print type(self), self.parent+'.'+self.name, self.value, 'rxor',
    #print type(target), target
    temp = self.value ^ target
    return temp

  def __and__(self, target):
    # TODO: super hacky!!!!
    #temp = VerilogPort(name='and_temp')
    #print type(self), self.parent+'.'+self.name, self.value, 'and',
    #print type(target), target.parent+'.'+target.name, target.value
    #temp.value = self.value & target.value
    temp = self.value & target.value
    return temp

  def __or__(self, target):
    # TODO: super hacky!!!!
    #temp = VerilogPort(name='or_temp')
    #print type(self), self.parent+'.'+self.name, self.value, 'or',
    #print type(target), target.parent+'.'+target.name, target.value
    #temp.value = self.value | target.value
    temp = self.value | target.value
    return temp

  def __ilshift__(self, target):
    if debug: print type(self), self.parent+'.'+self.name, self.value, '<<=',
    if not isinstance(target, int):
      if debug: print target.value
      self.value = target.value
    else:
      if debug: print target
      self.value = target
    return self

  def __getitem__(self, addr):
    #print "@__getitem__", type(addr), addr, str(addr)
    # TODO: handle slices here or in Slice type?
    return VerilogSlice(self, 1, addr)

  def connect(self, target):
    # TODO: throw an exception if the other object is not a VerilogPort
    # TODO: support wires?
    # TODO: do we want to use an assert here
    if isinstance(target, int):
      self.connection += [VerilogConstant(target, self.width)]
      self._value     = ValueNode(self.width, target)
    elif isinstance(target, VerilogSlice):
      assert self.width == target.width
      self.connection.append(   target )
      target.connection.append( self   )
      if target._value:
        self._value = target
      else:
        self._value = target
        target._value = ValueNode(target.parent_ptr.width)
        # Add the target callbacks
        target._value.funcs.update( target.funcs )
      # Add our callbacks
      target._value.funcs.update( self.funcs )
    else:
      assert self.width == target.width
      self.connection.append(   target )
      target.connection.append( self   )
      if target._value:
        self._value = target._value
      else:
        self._value = ValueNode(self.width)
        target._value = self._value
        # Add the target callbacks
        self._value.funcs.update( target.funcs )
      # Add the target callbacks
      self._value.funcs.update( self.funcs )

  def parse(self, line):
    tokens = line.strip().strip(',').split()
    type = tokens[0]
    if len(tokens) == 2:
      name  = tokens[1]
      width = 1
    elif len(tokens) == 3:
      name = tokens[2]
      width = tokens[1]
    return type, width, name

  @property
  def value(self):
    if self._value:
      return self._value.value
    else:
      return self._value
  @value.setter
  def value(self, value):
    #print "PORT:", self.parent+'.'+self.name
    #if isinstance(self, VerilogSlice):
    #  print "  writing", 'SLICE.'+self.name, ':   ', self.value,
    #else:
    #  print "  writing", self.parent+'.'+self.name, ':   ', self.value,
    if not self._value:
      print "// WARNING: writing to unconnected node {0}.{1}!".format(
            self.parent, self.name)
      self._value = ValueNode(self.width, value)
    else:
      self._value.value = value
      sim.add_event(self, self.connection)

class InPort(VerilogPort):
  def __init__(self, width=None):
    super(InPort, self).__init__('input', width)

class OutPort(VerilogPort):
  def __init__(self, width=None):
    super(OutPort, self).__init__('output', width)


class VerilogConstant(object):
  def __init__(self, value, width):
    self.value = value
    self.width = width
    self.type  = 'constant'
    self.name  = "%d'd%d" % (self.width, self.value)
    self.parent = ''
  def __repr__(self):
    return "Constant(%s, %s)" % (self.value, self.width)
  def __str__(self):
    return self.name

class VerilogWire(object):

  def __init__(self, name, width):
    self.name  = name
    self.width = width
    self.type  = "wire"

  def __repr__(self):
    return "Wire(%s, %s)" % (self.name, self.width)

  def __str__(self):
    # TODO: this seems weird.
    if isinstance(self.width, str):
      return "wire %s %s;" % (self.width, self.name)
    elif isinstance(self.width, int):
      if self.width == 1:
        return "wire %s;" % (self.name)
      else :
        return "wire [%d:0] %s;" % (self.width-1, self.name)


class VerilogParam(object):

  def __init__(self, name, value):
    self.name  = name
    self.value = value

  def __init__(self, line):
    self.name, self.value = self.parse(line)

  def __repr__(self):
    return "Param(%s = %s)" % (self.name, self.value)

  def parse(self, line):
    tokens = line.strip().split()
    name  = tokens[1]
    value = tokens[3].strip(',')
    return name, value


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


class Synthesizable(object):
  pass


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
    target.type = target.__class__.__name__
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
    print >> o, 'module %s' % target.type
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
      print >> o, '  %s %s' % (s.type, s.name)
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

#req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
