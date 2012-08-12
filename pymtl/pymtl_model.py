"""Base modeling components for constructing hardware description models.

This module contains a collection of classes that can be used to construct MTL
(pronounced metal) models. Once constructed, a MTL model can be leveraged by
a number of tools for various purposes (simulation, translation into HDLs, etc).
"""

class Slice(object):

  """Hidden class implementing the ability to access sub-bits of a wire/port.

  This class automatically handles reading and writing the correct subset of
  bits in a Node. The Slice has been designed to be as
  transparent as possible so that logic generally does not have to behave
  differently when accessing a Slice vs. a  Port.
  """

  def __init__(self, parent_ptr, addr):
    """Constructor for a ValueSlice object.

    Parameters
    ----------
    parent_ptr: the port/wire instance we are slicing.
    width: number of bits we are slicing.
    addr: address range of bits we are slicing, either an int or slice object.
    """
    self.parent_ptr = parent_ptr
    self.connections = []
    self.inst_connection = None
    # TODO: add asserts that check the parent width, range, etc
    if isinstance(addr, slice):
      assert not addr.step  # We dont support steps!
      self.addr     = addr.start
      self.width    = addr.stop - addr.start
    else:
      self.addr     = addr
      self.width    = 1
    self.wmask = (1 << self.width) - 1
    self.pmask = self.wmask << self.addr

  @property
  def parent(self):
    """Return the parent of the port/wire we are slicing."""
    return self.parent_ptr.parent

  @property
  def name(self):
    """Return the name and bitrange of the port/wire we are slicing."""
    if self.width == 1:
      suffix = '[{0}]'.format(self.addr)
    else:
      suffix = '[{0}:{1}]'.format(self.addr+self.width-1, self.addr)
    return self.parent_ptr.name + suffix

  #TODO: hacky...
  @property
  def type(self):
    """Return the type of object we are slicing."""
    return self.parent_ptr.type

  @property
  def value(self):
    """Value of the bits we are slicing."""
    temp = (self.parent_ptr.value & self.pmask) >> self.addr
    return temp
  @value.setter
  def value(self, value):
    self.parent_ptr.value &= ~(self.pmask)
    # TODO: mask off upper bits of provided value?
    #temp = value & self.wmask
    self.parent_ptr.value |= (value << self.addr)

  @property
  def _value(self):
    """The ValueNode pointed to by the port/wire we are slicing."""
    return self.parent_ptr._value
  @_value.setter
  def _value(self, value):
    self.parent_ptr._value = value


class Port(object):

  """Hidden base class implementing a module port."""

  # TODO: get rid of str
  # TODO: get rid of type
  # TODO: get rid of name?
  def __init__(self, type=None, width=None, name='???', str=None):
    """Constructor for a Port object.

    Parameters
    ----------
    type: string indicated whether this is an 'input' or 'output' port.
    width: bitwidth of the port.
    name: (TODO: remove? Previously only used for intermediate values).
    str: initializes a Port given a string containing a  port
         declaration. (TODO: remove. Only used by From.)
    """
    self.type  = type
    self.width = width
    self.name  = name
    self.parent = None
    self.connections = []
    self.int_connections = []  # defined inside module implementation
    self.ext_connections = []  # defined during module instantiation
    self.inst_connection = None
    self._value     = None
    self.is_reg = False
    if str:
      self.type, self.width, self.name  = self.parse( str )

  def __ne__(self, target):
    """Connection operator (<>), calls connect()."""
    self.connect(target)

  def __getitem__(self, addr):
    """Bitfield access ([]). Returns a VeriogSlice object.

    TODO: only works for connectivity, not logic?
    """
    #print "@__getitem__", type(addr), addr, str(addr)
    if isinstance(addr, int):
      assert addr < self.width
    elif isinstance(addr, slice):
      assert addr.start < addr.stop
      assert addr.stop <= self.width
    return Slice(self, addr)

  def connect(self, target):
    """Creates a connection with a Port or Slice.

    TODO: implement connections with a Wire?
    """
    # TODO: throw an exception if the other object is not a Port
    # TODO: support wires?
    # TODO: do we want to use an assert here
    if isinstance(target, int):
      self._value          = Constant(target, self.width)
      # TODO: make an inst_connection or regular connection?
      self.inst_connection = Constant(target, self.width)
    elif isinstance(target, Slice):
      assert self.width == target.width
      self.connections              += [ target ]
      target.parent_ptr.connections += [ target ]
      target.connections            += [ self ]
      self._value                    = target
    else:
      #print "CONNECTING {0},{1} to {2},{3}".format(self.type, self.width, target.type, target.width)
      assert self.width == target.width
      self.connections   += [ target ]
      target.connections += [ self   ]
      # If we are connecting a port to another port which is itself a slice of
      # another object, make our value pointer also point to the slice
      if self.type == target.type:
        #print "  TARGETS? {0} to {1}".format(type(self._value), type(target._value))
        assert not (self._value and target._value)
        if self._value:   target._value = self._value
        else:               self._value = target._value

  @property
  def value(self):
    """Access the value on this port."""
    if self._value: return self._value.value
    else:           return self._value
  @value.setter
  def value(self, value):
    # TODO: remove this check?
    if not self._value:
      print "// WARNING: writing to unconnected node {0}.{1}!".format(
            self.parent, self.name)
      assert False
    else:
      self._value.value = value

  @property
  def next(self):
    """Access the shadow value on this port."""
    assert self._value
    return self._value.next
  @next.setter
  def next(self, value):
    assert self._value
    self._value.next = value


class InPort(Port):
  """User visible implementation of an input port."""

  def __init__(self, width=None):
    """Constructor for an InPort object.

    Parameters
    ----------
    width: bitwidth of the port.
    """
    super(InPort, self).__init__('input', width)


class OutPort(Port):

  """User visible implementation of an output port."""

  def __init__(self, width=None):
    """Constructor for an InPort object.

    Parameters
    ----------
    width: bitwidth of the port.
    """
    super(OutPort, self).__init__('output', width)


class UWire(object):

  """Hidden base class implementing a module port."""

  def __init__(self, width):
    """Constructor for a Port object.

    Parameters
    ----------
    type: string indicated whether this is an 'input' or 'output' port.
    width: bitwidth of the port.
    name: (TODO: remove? Previously only used for intermediate values).
    str: initializes a Port given a string containing a  port
         declaration. (TODO: remove. Only used by From.)
    """
    self.type  = 'wire'
    self.width = width
    self.name  = '???'
    self.parent = None
    self.connections = []
    self.int_connections = []  # defined inside module implementation
    self.ext_connections = []  # defined during module instantiation
    self.inst_connection = None
    self._value     = None
    self.is_reg = False

  def __ne__(self, target):
    """Connection operator (<>), calls connect()."""
    self.connect(target)

  def __getitem__(self, addr):
    """Bitfield access ([]). Returns a VeriogSlice object.

    TODO: only works for connectivity, not logic?
    """
    #print "@__getitem__", type(addr), addr, str(addr)
    if isinstance(addr, int):
      assert addr < self.width
    elif isinstance(addr, slice):
      assert addr.start < addr.stop
      assert addr.stop <= self.width
    return Slice(self, addr)

  def connect(self, target):
    """Creates a connection with a Port or Slice.

    TODO: implement connections with a Wire?
    """
    # TODO: throw an exception if the other object is not a Port
    # TODO: support wires?
    # TODO: do we want to use an assert here
    if isinstance(target, int):
      self._value          = Constant(target, self.width)
      # TODO: make an inst_connection or regular connection?
      self.inst_connection = Constant(target, self.width)
    elif isinstance(target, Slice):
      assert self.width == target.width
      self.connections              += [ target ]
      target.parent_ptr.connections += [ target ]
      target.connections            += [ self ]
      self._value                    = target
    else:
      #print "CONNECTING {0},{1} to {2},{3}".format(self.type, self.width, target.type, target.width)
      assert self.width == target.width
      self.connections   += [ target ]
      target.connections += [ self   ]
      # If we are connecting a port to another port which is itself a slice of
      # another object, make our value pointer also point to the slice
      if self.type == target.type:
        #print "  TARGETS? {0} to {1}".format(type(self._value), type(target._value))
        assert not (self._value and target._value)
        if self._value:   target._value = self._value
        else:               self._value = target._value

  @property
  def value(self):
    """Access the value on this port."""
    if self._value: return self._value.value
    else:           return self._value
  @value.setter
  def value(self, value):
    # TODO: remove this check?
    if not self._value:
      print "// WARNING: writing to unconnected node {0}.{1}!".format(
            self.parent, self.name)
      assert False
    else:
      self._value.value = value

  @property
  def next(self):
    """Access the shadow value on this port."""
    assert self._value
    return self._value.next
  @next.setter
  def next(self, value):
    assert self._value
    self._value.next = value


class Constant(object):

  """Hidden class for storing a constant valued node."""

  def __init__(self, value, width):
    """Constructor for a Constant object.

    Parameters
    ----------
    value: value of the constant.
    width: bitwidth of the constant.
    """
    self.value = value
    self.width = width
    self.type  = 'constant'
    self.name  = "%d'd%d" % (self.width, self.value)
    self.parent = None


class Wire(object):

  """User visible (?) class to represent wire/connection objects.

  Not sure if VerilogWire objects should be user visible, or should always be
  inferred based on connectivity/logic.  Currently only inferred based on
  connectivity...
  """

  def __init__(self, name, width):
    """Constructor for a VerilogWire object.

    Parameters
    ----------
    name: name of the wire.
    width: bitwidth of the wire.
    """
    self.name  = name
    self.width = width
    self.type  = "wire"


class Model(object):

  """User visible base class for hardware models.

  Provides utility classes for elaborating connectivity between components,
  giving instantiated subcomponents proper names, and building datastructures
  that can be leveraged by various MTL tools.

  Any user implemented model that wishes to make use of the various MTL tools
  should subclass this.
  """

  def elaborate(self):
    self.recurse_elaborate('toplevel')
    self.recurse_connections()

  def recurse_elaborate(self, iname):
    """Elaborate a MTL model (construct hierarchy, name modules, etc.).

    The elaborate() function must be called on an instantiated toplevel module
    before it is passed to any MTL tools!
    """
    # TODO: call elaborate() in the tools?
    target = self
    # TODO: better way to set the name?
    target.class_name = target.__class__.__name__
    target.parent = None
    target.name = iname
    target._wires = []
    target._ports = []
    target._submodules = []
    target._senses = []
    target._localparams = []
    # TODO: do all ports first?
    # Get the names of all ports and submodules
    for name, obj in target.__dict__.items():
      if not name.startswith('_'):
        self.check_type(target, name, obj)

  def check_type(self, target, name, obj):
    """Utility method to specialize elaboration actions based on object type."""
    # If object is a port, add it to our ports list
    if isinstance(obj, Port):
      obj.name = name
      obj.parent = target
      target._ports += [obj]
      if obj.type == 'input':
        target._senses += [obj]
    elif isinstance(obj, UWire):
      obj.name = name
      obj.parent = target
      target._wires += [obj]
      target._senses += [obj]
    # If object is a submodule, add it to our submodules list and recursively
    # call elaborate() on it
    elif isinstance(obj, Model):
      # TODO: change obj.type to obj.inst_type?
      obj.type = obj.__class__.__name__
      obj.recurse_elaborate( name )
      obj.parent = target
      target._submodules += [obj]
    # We've found a constant assigned to a global variable.
    # TODO: add support for floats?
    elif isinstance(obj, int):
      target._localparams += [(name, obj)]
    # If the object is a list, iterate through each item in the list and
    # recursively call the check_type() utility function
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

  def recurse_connections(self):
    for port in self._ports:
      #print port.parent.name, port.name
      for c in port.connections:
        #print '  :::', c.parent.name, c.name,
        if c.parent == port.parent or c.parent in self._submodules:
          #print 'int'
          port.int_connections += [c]
        else:
          #print 'ext'
          port.ext_connections += [c]
    for submodule in self._submodules:
      submodule.recurse_connections()


# Decorators

def combinational(func):
  # Normally a decorator returns a wrapped function, but here we return
  # func unmodified.  We only use the decorator as a flag for the ast
  # parsers.
  return func

def posedge_clk(func):
  return func

