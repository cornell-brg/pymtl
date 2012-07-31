"""Base modeling components for constructing hardware description models.

This module contains a collection of classes that can be used to construct MTL
(pronounced metal) models. Once constructed, a MTL model can be leveraged by
a number of tools for various purposes (simulation, translation into HDLs, etc).
"""

class Node(object):

  """Hidden class implementing a node storing value (like a net in ).

  Connected ports and wires have a pointer to the same Node
  instance, such that reads and writes remain consistent. Can be either treated
  as a wire or a register depending on use, but not both.
  """

  def __init__(self, width, value=0, sim=None):
    """Constructor for a Node object.

    Parameters
    ----------
    width: bitwidth of the node.
    value: initial value of the node. Only set by Constant objects.
    sim: simulation object to register events with on write.
    """
    self.sim = sim
    self.width = width
    self._value = value

  @property
  def value(self):
    """Value stored by node. Informs the attached simulator on any write."""
    return self._value
  @value.setter
  def value(self, value):
    self.sim.add_event(self)
    self._value = value

  def clock(self):
    """Update value to store contents of next. Should only be called by sim."""
    self._value = self.next


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
    self.inst_connection = None
    self._value     = None
    self.is_reg = False
    if str:
      self.type, self.width, self.name  = self.parse( str )

  # TODO: add id?
  #def __repr__(self):
  #  return "Port(%s, %s, %s)" % (self.type, self.width, self.name)

  def __str__(self):
    reg = 'reg' if self.is_reg else ''
    if isinstance(self.width, str):
      return "%s %s %s %s" % (self.type, reg, self.width, self.name)
    elif isinstance(self.width, int):
      if self.width == 1:
        return "%s %s %s" % (self.type, reg, self.name)
      else :
        return "%s %s [%d:0] %s" % (self.type, reg, self.width-1, self.name)

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
      #self.connections += [Constant(target, self.width)]
      #self._value     = ValueNode(self.width, target)
      self._value     = Constant(target, self.width)
      #print "CreateConstValueNode:", self.parent, self.name, self._value
    elif isinstance(target, Slice):
      assert self.width == target.width
      self.connections              += [ target ]
      target.parent_ptr.connections += [ target ]
      target.connections            += [ self ]
      self._value                    = target
      #if target._value:
      #  self._value = target
      #else:
      #  self._value = target
      #  target._value = ValueNode(target.parent_ptr.width)
      #  #print "CreateValueNode:", self.parent, self.name, target._value
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
      #if target._value:
      #  self._value = target._value
      #else:
      #  self._value = ValueNode(self.width)
      #  #print "CreateValueNode:", self.parent, self.name, self._value
      #  target._value = self._value

  @property
  def value(self):
    """Value on the port."""
    if self._value: return self._value.value
    else:           return self._value
  @value.setter
  def value(self, value):
    # TODO: add as debug?
    #print "PORT:", self.parent.name+'.'+self.name
    #if isinstance(self, Slice):
    #  print "  writing", 'SLICE.'+self.name, ':   ', value
    #else:
    #  print "  writing", self.parent.name+'.'+self.name, ':   ', value
    # TODO: change how ValueNode instantiation occurs
    if not self._value:
      print "// WARNING: writing to unconnected node {0}.{1}!".format(
            self.parent, self.name)
      self._value = ValueNode(self.width, value)
    else:
      self._value.value = value


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


class Module(object):

  """User visible base class for hardware models.

  Provides utility classes for elaborating connectivity between components,
  giving instantiated subcomponents proper names, and building datastructures
  that can be leveraged by various MTL tools.

  Any user implemented model that wishes to make use of the various MTL tools
  should subclass this.
  """

  def elaborate(self, iname='toplevel'):
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
    target.wires = []
    target.ports = []
    target.submodules = []
    # TODO: do all ports first?
    # Get the names of all ports and submodules
    for name, obj in target.__dict__.items():
      # TODO: make ports, submodules, wires _ports, _submodules, _wires
      if (name is not 'ports' and name is not 'submodules'):
        self.check_type(target, name, obj)

  def check_type(self, target, name, obj):
    """Utility method to specialize elaboration actions based on object type."""
    # If object is a port, add it to our ports list
    if isinstance(obj, Port):
      obj.name = name
      obj.parent = target
      target.ports += [obj]
    # If object is a submodule, add it to our submodules list and recursively
    # call elaborate() on it
    elif isinstance(obj, Module):
      # TODO: change obj.type to obj.inst_type?
      obj.type = obj.__class__.__name__
      obj.elaborate( name )
      obj.parent = target
      target.submodules += [obj]
    # If the object is a list, iterate through each item in the list and
    # recursively call the check_type() utility function
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

