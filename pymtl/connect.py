#------------------------------------------------------------------------
# Node
#------------------------------------------------------------------------
class Node(object):
  def __init__(self, width, name='no_name'):
    """Construct a node with Node provided width."""
    self.width       = width
    self.name        = name
    self._value      = None
    self.connections = []

  def connect(self, target):
    """Connect this Node to another Node or Slice."""
    self.connections   += [ target ]
    target.connections += [ self   ]

  def __getitem__(self, addr):
    """Slice this Node to get subbits."""
    if isinstance(addr, int):
      assert addr < self.width
    elif isinstance(addr, slice):
      assert addr.start < addr.stop
      assert addr.stop <= self.width
    s = Slice(self, addr)
    # TODO: do we want this here?
    self.connections += [ s ]
    return s

  @property
  def value(self):
    """Access the value on this Node."""
    if self._value == None:
      return 0
    return self._value
  @value.setter
  def value(self, value):
    if self._value != value:
      self._value = value
      # TODO: notify all connections of update
      for x in self.connections:
        x.update( self )

  def update(self, caller):
    assert self.width == caller.width
    # Should automatically call update via setter
    self.value = caller.value

#------------------------------------------------------------------------
# Slice
#------------------------------------------------------------------------
class Slice(object):
  def __init__(self, parent_ptr, addr):
    """Construct a Slice pointing to subbits of Node parent_ptr."""
    self.parent_ptr  = parent_ptr
    self.connections = []
    # Special case Python slice operations vs integers
    if isinstance(addr, slice):
      assert not addr.step  # We dont support steps!
      self.addr      = addr.start
      self.width     = addr.stop - addr.start
    else:
      self.addr      = addr
      self.width     = 1
    # TODO: replace with Bits
    self.wmask       = (1 << self.width) - 1
    self.pmask       = self.wmask << self.addr
    # Create the name
    if self.width == 1:
      self.suffix    = '[{0}]'.format(self.addr)
    else:
      self.suffix    = '[{0}:{1}]'.format(self.addr+self.width-1, self.addr)

  def connect(self, target):
    """Connect this Node to another Node or Slice."""
    self.connections   += [ target ]
    target.connections += [ self   ]

  @property
  def value(self):
    """Value of the bits we are slicing."""
    # TODO: replace with Bits
    return (self.parent_ptr.value & self.pmask) >> self.addr
  @value.setter
  def value(self, value):
    # TODO: replace with Bits
    if self.value != value:
      self.parent_ptr.value &= ~(self.pmask)
      self.parent_ptr.value |= (value << self.addr)
      # TODO: add connections

  @property
  def name(self):
    """Return the name and bitrange of the Node we are slicing."""
    return self.parent_ptr.name + self.suffix

  def update(self, caller):
    # If our parent isnt the origin of the update call, write the parent
    if caller is not self.parent_ptr:
      assert caller.width == self.width
      self.value = caller.value
    # Propagate the update call
    for x in self.connections:
      # TODO: needed to prevent infinite loop. Better way to handle?
      if x is not caller:
        x.update( self )

#------------------------------------------------------------------------
# Constant
#------------------------------------------------------------------------
#class Constant(object):

#------------------------------------------------------------------------
# Connect Method
#------------------------------------------------------------------------
def connect( port_A, port_B):
  if isinstance(port_A, Slice):
    port_B.connect( port_A )
  else:
    port_A.connect( port_B )
