import sys


# TODO: subclass ports or wires?
class VerilogSlice(object):
  def __init__(self, parent, width, addr):
    self.parent     = parent
    self.width      = width
    self.addr       = addr
    self.connection = parent.connection

  @property
  def name(self):
    suffix = '[%d]' % self.addr
    return self.parent.name + suffix

  @property
  def type(self):
    return self.parent.type

class VerilogPort(object):

  def __init__(self, type=None, width=None, name='???', str=None):
    self.type  = type
    self.width = width
    self.name  = name
    self.connection = None
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

  def __getitem__(self, addr):
    #print "@__getitem__", type(addr), addr, str(addr)
    # TODO: handle slices here or in Slice type?
    return VerilogSlice(self, 1, addr)

  def connect(self, target):
    # TODO: throw an exception if the other object is not a VerilogPort
    # TODO: support wires?
    # TODO: do we want to use an assert here
    if isinstance(target, int):
      self.connection = VerilogConstant(target, self.width)
    else:
      #if isinstance(target, VerilogPort)
      # or isinstance(target,VerilogSlice):
      assert self.width == target.width
      self.connection    = target
      target.connection  = self

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
      target.ports += [obj]
    # If object is a submodule, add it to our submodules list
    # TODO: change to be a special subclass?
    #elif isinstance(obj, ToVerilog):
    elif isinstance(obj, Synthesizable):
      obj.name = name
      # TODO: better way to do this?
      obj.type = obj.__class__.__name__
      # TODO: hack, passing None necessary since generate_new also does
      #       refactor to make this unnecessary.  Although... this does
      #       Potentially handle generating class .v files on demand...
      #obj.generate_new(None)
      self.elaborate( obj )
      target.submodules += [obj]
    # If object is a list, iterate through items and recursively call
    # check_type()
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

  def elaborate(self, target):
    # TODO: better way to set the name?
    target.type = target.__class__.__name__
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
    #if logic:  print logic.getvalue(),
    # End module
    print >> o, 'endmodule'

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
    for s in target.submodules:
      for p in s.ports:
        if (p.connection and p.connection.type != 'wire'
            and p.connection.type != 'constant'
            and p.type != p.connection.type):
          # TODO: figure out a way to get connection submodule name...
          wire_name = '{0}_{1}_TO_{2}'.format(s.name, p.name,
                                              p.connection.name)
          wire = VerilogWire(wire_name, p.width)
          p.connection.connection = wire
          p.connection = wire
          print >> o, '  %s' % wire
    print

  def gen_wire_decls(self, wires, o):
    for w in wires.values():
      print >> o, '  %s' % w

  def gen_module_insts(self, submodules, o):
    for s in submodules:
      print >> o, '  %s %s' % (s.type, s.name)
      # TODO: add params
      print >> o, '  ('
      self.gen_port_insts(s.ports, o)
      print >> o, '  );\n'

  def gen_port_insts(self, ports, o):
    for p in ports[:-1]:
      name = p.connection.name if p.connection else ' '
      print >> o , '    .%s (%s),' % (p.name, name)
    p = ports[-1]
    name = p.connection.name if p.connection else ' '
    print >> o, '    .%s (%s)' % (p.name, name)


#req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
