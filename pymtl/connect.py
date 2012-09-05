#=========================================================================
# Connect
#=========================================================================

from Bits import *

#-------------------------------------------------------------------------
# Node
#-------------------------------------------------------------------------

class Node(object):
  def __init__(self, width, name='no_name'):
    """Construct a node with Node provided width."""
    self.width       = width
    self.name        = name
    # TODO: Bits specific! Fix!
    self._value      = Bits( width, None )
    self._next       = Bits( width, None )
    self.connections = []
    self._updating   = False #TODO: get rid of me
    self.sim         = None

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
    return self._value
  @value.setter
  def value(self, value):
    if self._value != value and not self._updating:
      # VALUE STUFF
      # TODO: this is Bits specific!
      self._value[:] = value
      # SIMULATOR STUFF
      # TODO: temp check for connect_tests
      if self.sim:
        self.sim.add_event(self) # TODO: make hook added by simulator
      # ADD VCD HERE
        if self.sim.vcd:
          if self.width == 1:
            print >> self.sim.o, "%d%s" % (self.value.uint, self._code)
          else:
            print >> self.sim.o, "s%s %s" % (self.value.uint, self._code)
      # TODO: notify all connections of update, fix _updating
      # CONNECTIVITY STUFF
      self._updating = True
      for x in self.connections:
        x.update( self )
      self._updating = False

  # TODO: make hook added by simulator?
  @property
  def next(self):
    """Next value stored by node, informs attached simulator of any write."""
    return self._next
  @next.setter
  def next(self, value):
    # TODO: temp check for connect_tests
    if self.sim:
      self.sim.rnode_callbacks += [self]
    # TODO: be careful!  _next = value passes the object, want to copy the value...
    # otherwise this fails!
    self._next[:] = value

  # TODO: make hook added by simulator?
  def clock(self):
    """Update value to store contents of next. Should only be called by sim."""
    self.value = self.next

  def update_from_slice(self, value, range):
    """Called by Slice to update its parent."""
    if not self._updating:
      # TODO: this is Bits specific!
      self._value[range] = value
      # TODO: notify all connections of update, fix _updating
      self._updating = True
      for x in self.connections:
        x.update( self )
      self._updating = False

  def update(self, caller):
    """Called by other Nodes/Slices, used to propagate values."""
    assert self.width == caller.width
    # Should automatically call update via setter
    self.value = caller.value

#-------------------------------------------------------------------------
# Slice
#-------------------------------------------------------------------------

class Slice(object):
  def __init__(self, parent_ptr, addr):
    """Construct a Slice pointing to subbits of Node parent_ptr."""
    self.parent_ptr  = parent_ptr
    self.parent      = parent_ptr # TODO: temporary, for port_walk
    self.connections = []
    # Special case Python slice operations vs integers
    self.addr        = addr
    if isinstance(addr, slice):
      assert not addr.step  # We dont support steps!
      self.width     = addr.stop - addr.start
      self.suffix    = '[{0}:{1}]'.format(self.addr.stop, self.addr.start)
    else:
      self.width     = 1
      self.suffix    = '[{0}]'.format(self.addr)

  def connect(self, target):
    """Connect this Node to another Node or Slice."""
    self.connections   += [ target ]
    target.connections += [ self   ]

  @property
  def node(self):
    """This attribute makes it so we don't have to special case Slices."""
    return self

  @property
  def value(self):
    """Value of the bits we are slicing."""
    return self.parent_ptr.value[self.addr]
  @value.setter
  def value(self, value):
    if self.value != value:
      self.parent_ptr.update_from_slice( value, self.addr )

  @property
  def name(self):
    """Return the name and bitrange of the Node we are slicing."""
    return self.parent_ptr.name + self.suffix

  def update(self, caller):
    """Called by other Nodes/Slices, used to propagate values."""
    # If our parent isnt the origin of the update call, write the parent
    if caller is not self.parent_ptr:
      assert caller.width == self.width
      self.value = caller.value
    # Propagate the update call
    for x in self.connections:
      # TODO: needed to prevent infinite loop. Better way to handle?
      if x is not caller:
        x.update( self )

#-------------------------------------------------------------------------
# Connect Utility Method
#-------------------------------------------------------------------------

def connect( port_A, port_B):
  """Connect Nodes/Slices to other Nodes/Slices."""
  if isinstance(port_A, Slice):
    port_B.connect( port_A )
  else:
    port_A.connect( port_B )
