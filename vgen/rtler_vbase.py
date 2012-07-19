import sys
import ast

class ValueNode(object):
  # TODO: handle X values
  # TODO: add sim
  #def __init__(self, width, value='X'):
  def __init__(self, width, value=0):
    self.sim = None
    self.width = width
    self._value = value

  @property
  def value(self):
    return self._value
  @value.setter
  def value(self, value):
    # TODO: debug_reg_eventqueue
    #print "    VALUE:", self, bin(value)
    # TODO: nodes not in the vnode_callback list dont have a sim object! Fix!
    if self.sim: self.sim.add_event(self)
    else:        print "// warning: writing a node with no simulator pointer!"
    self._value = value

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
  def value(self):
    temp = ((self.parent_ptr.value) & (1 << self.addr)) >> self.addr
    return temp
  @value.setter
  def value(self, value):
    self.parent_ptr.value |= (value << self.addr)

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
    if str:
      self.type, self.width, self.name  = self.parse( str )

  # TODO: add id?
  #def __repr__(self):
  #  return "Port(%s, %s, %s)" % (self.type, self.width, self.name)

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
    # TODO: returns an int, not a port. Is this okay?
    #temp = VerilogPort(name='xor_temp') #temp.value = self.value ^ target.value
    temp = self.value ^ target.value
    return temp

  def __rxor__(self, target):
    temp = self.value ^ target
    return temp

  def __and__(self, target):
    # TODO: returns an int, not a port. Is this okay?
    #temp = VerilogPort(name='and_temp') #temp.value = self.value & target.value
    temp = self.value & target.value
    return temp

  def __or__(self, target):
    # TODO: returns an int, not a port. Is this okay?
    #temp = VerilogPort(name='or_temp') #temp.value = self.value | target.value
    temp = self.value | target.value
    return temp

  def __ilshift__(self, target):
    # TODO: debug_assign
    #print type(self), self.parent+'.'+self.name, self.value, '<<=',
    # TODO: handles both int and VerilogPort. Better way?
    if not isinstance(target, int): self.value = target.value
    else:                           self.value = target
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
      #print "CreateConstValueNode:", self.parent, self.name, self._value
    elif isinstance(target, VerilogSlice):
      assert self.width == target.width
      self.connection.append(   target )
      target.connection.append( self   )
      if target._value:
        self._value = target
      else:
        self._value = target
        target._value = ValueNode(target.parent_ptr.width)
        #print "CreateValueNode:", self.parent, self.name, target._value
    else:
      assert self.width == target.width
      self.connection.append(   target )
      target.connection.append( self   )
      if target._value:
        self._value = target._value
      else:
        self._value = ValueNode(self.width)
        #print "CreateValueNode:", self.parent, self.name, self._value
        target._value = self._value

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
    # TODO: add as debug?
    #if isinstance(self, VerilogSlice):
    #  print "  writing", 'SLICE.'+self.name, ':   ', self.value
    #else:
    #  print "  writing", self.parent+'.'+self.name, ':   ', self.value
    # TODO: change how ValueNode instantiation occurs
    if not self._value:
      print "// WARNING: writing to unconnected node {0}.{1}!".format(
            self.parent, self.name)
      self._value = ValueNode(self.width, value)
    else:
      self._value.value = value
      #sim.add_event(self, self.connection)

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


class VerilogModule(object):

  def check_type(self, target, name, obj):
    # If object is a port, add it to our ports list
    if isinstance(obj, VerilogPort):
      obj.name = name
      obj.parent = target.name
      target.ports += [obj]
    # If object is a submodule, add it to our submodules list
    # TODO: change to be a special subclass?
    #elif isinstance(obj, ToVerilog):
    elif isinstance(obj, VerilogModule):
      #obj.name = name
      # TODO: better way to do this?
      obj.type = obj.__class__.__name__
      # TODO: hack, passing None necessary since generate_new also does
      #       refactor to make this unnecessary.  Although... this does
      #       Potentially handle generating class .v files on demand...
      #obj.generate_new(None)
      #self.elaborate( obj, name )
      obj.elaborate( name )
      target.submodules += [obj]
    # If object is a list, iterate through items and recursively call
    # check_type()
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

  def elaborate(self, iname='toplevel'):
    target = self
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

