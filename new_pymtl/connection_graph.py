#=========================================================================
# Connection Graph
#=========================================================================
# TODO: Add comments!

#-------------------------------------------------------------------------
# Constant
#-------------------------------------------------------------------------
# Hidden class for storing a constant valued node.
class Constant( object ):


  def __init__(self, value, nbits ):
    """Constructor for a Constant object.

    Parameters
    ----------
    value: value of the constant.
    nbits: bitwidth of the constant.
    """
    self._addr  = None
    self.value  = value
    self.nbits  = nbits
    self.type   = 'constant'
    self.name   = "%d'd%d" % ( nbits, value )
    self.parent = None
    # TODO: hack to ensure Constants can be treated as either port or node
    self.connections = []

#-------------------------------------------------------------------------
# ConnectionSlice
#-------------------------------------------------------------------------
class ConnectionSlice(object):
  def __init__( self, port, addr ):
    self.parent_port = port
    self._addr       = addr
    if isinstance(addr, slice):
      assert not addr.step  # We dont support steps!
      self.nbits     = addr.stop - addr.start
    else:
      self.nbits     = 1

  def connect(self, target):
    connection_edge = ConnectionEdge( self, target )
    self.parent_port.connections   += [ connection_edge ]
    # TODO: figure out a way to get rid of this special case
    if not isinstance( target, Constant ):
      target.parent_port.connections += [ connection_edge ]

  @property
  def connections(self):
    return self.parent_port.connections
  @connections.setter
  def connections(self, value):
    self.parent_port.connections = value

  @property
  def width( self ):
    """Temporary"""
    return self.nbits

#-------------------------------------------------------------------------
# Connectivity Exceptions
#-------------------------------------------------------------------------
class ConnectionError(Exception):
  pass

#-------------------------------------------------------------------------
# ConnectionEdge
#-------------------------------------------------------------------------
class ConnectionEdge(object):
  def __init__( self, src, dest ):
    """Construct a Connection object. TODO: describe"""
    if src.nbits != dest.nbits:
      raise ConnectionError("Connecting signals with different bitwidths!")

    self.nbits = src.nbits

    # Source Node
    if isinstance( src, ConnectionSlice ):
      self.src_node = src.parent_port
    else:
      self.src_node = src
    self.src_slice  = src._addr

    # Destination Node
    if isinstance( dest, ConnectionSlice ):
      self.dest_node = dest.parent_port
    else:
      self.dest_node = dest
    self.dest_slice = dest._addr

  def other( self, node ):
    assert self.src_node == node or self.dest_node == node
    if self.src_node == node:
      return self.dest_node
    else:
      return self.src_node

  def is_dest( self, node ):
    return self.dest_node == node

  def is_src( self, node ):
    return self.src_node == node

  def is_internal( self, node ):
    # Determine which node is the other in the connection
    other = self.other( node )

    # InPort connections to Constants are external, else internal
    if isinstance( self.src_node, Constant ):
      # TODO: HACKY WORKAROUND TO CIRCULAR DEPS, FIX
      from signals import InPort
      return not isinstance( self.dest_node, InPort )

    # Check if the connection is an internal connection for the node
    return (( self.src_node.parent == self.dest_node.parent ) or
            ( other.parent in node.parent._submodules ))

  def swap_direction( self ):
    self.src_node,  self.dest_node  = self.dest_node,  self.src_node
    self.src_slice, self.dest_slice = self.dest_slice, self.src_slice

