class TempPort(object):
  def __init__(self, type, width, name):
    self.type  = type
    self.width = width
    self.name  = name
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

class VerilogPort(object):

  def __init__(self, line):
    self.type, self.width, self.name = self.parse(line)

  def __repr__(self):
    return "Port(%s, %s, %s)" % (self.type, self.width, self.name)

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
        self.name = line.split()[1]
      # Parse parameters
      if in_module and 'parameter' in line:
        self.params += [ VerilogParam( line ) ]
      # Parse inputs
      elif in_module and 'input' in line:
        self.ports += [ VerilogPort( line ) ]
      # Parse outputs
      elif in_module and 'output' in line:
        self.ports += [ VerilogPort( line ) ]
      # End module definition
      elif in_module and end_token in line:
        in_module = False

class ToVerilog(object):

  def generate(self, o):
    print >> o, 'module %s' % self.name
    # Declare Params
    #if self.params: self.gen_params( self.params, o )
    # Declare Ports
    if self.ports: self.gen_ports( self.ports, o )
    # Wires & Instantiations
    #if logic:  print logic.getvalue(),
    # End module
    print >> o, 'endmodule'

  def gen_ports(self, ports, o):
    print >> o, '('
    for p in ports[:-1]:
      print >> o , '  %s,' % p
    p = ports[-1]
    print >> o, '  %s' % p
    print >> o, ');'

  def gen_params(params, o):
    print >> o, '#('
    for p in params[:-1]:
      print >> o, '  %s,' % p
    p = params[-1]
    print >> o, '  %s' % p
    print >> o, ')'


req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
print req_resp_port
print req_resp_port.clk
