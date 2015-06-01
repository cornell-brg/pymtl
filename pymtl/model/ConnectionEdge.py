#=======================================================================
# ConnectionEdge.py
#=======================================================================
'Classes used to describe the structural connection graph of a Model.'

from ..datatypes.helpers import get_nbits
from signals             import InPort, OutPort, Wire, Constant

#-----------------------------------------------------------------------
# PyMTLConnectError
#-----------------------------------------------------------------------
class PyMTLConnectError(Exception):
  'Exception raised for invalid connection parameters.'
  pass

#-----------------------------------------------------------------------
# ConnectionEdge
#-----------------------------------------------------------------------
# Class representing a structural connection between Signal objects.
class ConnectionEdge(object):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, src, dest ):

    # Validate inputs, raise exceptions if necessary
    if   isinstance( src, int ):
      if get_nbits( src ) > dest.nbits:
        raise PyMTLConnectError(
          "Constant {} is too big for target Signal of width nbits={}"
          .format( src, dest.nbits ))
      else:
        src = Constant( dest.nbits, src )

    elif isinstance( dest, int ):
      if get_nbits( dest ) > src.nbits:
        raise PyMTLConnectError(
          "Constant {} is too big for target Signal of width nbits={}"
          .format( dest, src.nbits ))
      else:
        dest = Constant( src.nbits, dest )

    elif src.nbits != dest.nbits:
      raise PyMTLConnectError(
          "Connecting signals with different bitwidths, nbits={} != nbits={}"
          .format( src.nbits, dest.nbits ))

    # Set the nbits attribute of the connection
    self.nbits = src.nbits

    # Set source and destination nodes and ranges
    self.src_node   = src ._signal
    self.src_slice  = src ._addr
    self.dest_node  = dest._signal
    self.dest_slice = dest._addr

    # Add ourselves to the src_node and dest_node connectivity lists
    # TODO: is this the right way to do this?
    src .connections += [ self ]
    dest.connections += [ self ]

  #---------------------------------------------------------------------
  # is_dest
  #---------------------------------------------------------------------
  def is_dest( self, node ):
    '''Return True if dest_node == node.'''
    return self.dest_node == node

  #---------------------------------------------------------------------
  # is_src
  #---------------------------------------------------------------------
  def is_src( self, node ):
    'Return True if src_node == node.'
    return self.src_node == node

  #---------------------------------------------------------------------
  # swap_direction
  #---------------------------------------------------------------------
  def swap_direction( self ):
    '''Swap the direction of the connection.

    The source becomes the destination and vice versa.
    '''

    self.src_node,  self.dest_node  = self.dest_node,  self.src_node
    self.src_slice, self.dest_slice = self.dest_slice, self.src_slice

  #---------------------------------------------------------------------
  # set_edge_direction
  #---------------------------------------------------------------------
  def set_edge_direction( self ):
    '''Determine directionality of edge and swap src/dest if necessary.

    Note that this method should only be called after static elaboration
    when .parent attributes of nodes are initialized!
    '''

    a = self.src_node
    b = self.dest_node

    # Constants should always be the source node
    if isinstance( a, Constant ): return
    if isinstance( b, Constant ): self.swap_direction()

    # Model connecting own InPort to own OutPort
    elif ( a.parent == b.parent and
           isinstance( a, OutPort ) and isinstance( b, InPort  )):
      self.swap_direction()

    # Model InPort connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort  ) and isinstance( b, InPort  )):
      self.swap_direction()

    # Model OutPort connected to OutPort of a submodule
    elif ( b.parent in a.parent._submodules and
           isinstance( a, OutPort ) and isinstance( b, OutPort )):
      self.swap_direction()

    # Model OutPort connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort ) and isinstance( b, OutPort )):
      self.swap_direction()

    # Wire connected to InPort
    elif ( a.parent == b.parent and
           isinstance( a, Wire ) and isinstance( b, InPort )):
      self.swap_direction()

    # Wire connected to OutPort
    elif ( a.parent == b.parent and
           isinstance( a, OutPort ) and isinstance( b, Wire )):
      self.swap_direction()

    # Wire connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort  ) and isinstance( b, Wire )):
      self.swap_direction()

    # Wire connected to OutPort of a submodule
    elif ( b.parent in a.parent._submodules and
           isinstance( a, Wire ) and isinstance( b, OutPort )):
      self.swap_direction()

    # Chaining submodules together (OutPort of one to InPort of another)
    elif ( a.parent != b.parent and a.parent.parent == b.parent.parent and
           isinstance( a, InPort  ) and isinstance( b, OutPort )):
      self.swap_direction()

  #---------------------------------------------------------------------
  # other
  #---------------------------------------------------------------------
  def other( self, node ):
    '''Given one vertex of this ConnectionEdge, return the other vertex.

    If given the src_node, return the dest_node.
    If given the dest_node, return the src_node.
    Assert if the provided node is neither the src_node or dest_node.
    '''

    assert self.src_node == node or self.dest_node == node
    if self.src_node == node:
      return self.dest_node
    else:
      return self.src_node

  #---------------------------------------------------------------------
  # is_internal
  #---------------------------------------------------------------------
  def is_internal( self, node ):
    '''DEPRECATED. Return true if connection's parent == node's parent.

    Note that this method should only be called after static elaboration
    when .parent attributes of nodes are initialized!
    '''

    # Determine which node is the other in the connection
    other = self.other( node )

    # InPort connections to Constants are external, else internal
    if isinstance( self.src_node, Constant ):
      return not isinstance( self.dest_node, InPort )

    # Check if the connection is an internal connection for the node
    return (( self.src_node.parent == self.dest_node.parent ) or
            ( other.parent in node.parent._submodules ))

  #---------------------------------------------------------------------
  # __repr__
  #---------------------------------------------------------------------
  def __repr__( self ):
    'Pretty printing of connections for debugging.'

    if   isinstance( self.src_slice, int ):
      sa = '[{}]'.format( self.src_slice )
    elif isinstance( self.src_slice, slice ):
      sa = '[{}:{}]'.format( self.src_slice.start, self.src_slice.stop )
    else:
      sa = ''
    if   isinstance( self.dest_slice, int ):
      da = '[{}]'.format( self.dest_slice )
    elif isinstance( self.dest_slice, slice ):
      da = '[{}:{}]'.format( self.dest_slice.start, self.dest_slice.stop )
    else:
      da = ''
    return "{}{} => {}{}".format( self.src_node.fullname,  sa,
                                    self.dest_node.fullname, da )

