#=======================================================================
# ConnectionEdge.py
#=======================================================================
# Classes used to construct the structural connection graph of a Model.

from helpers import get_nbits
from signals import InPort, Constant

#-----------------------------------------------------------------------
# ConnectError
#-----------------------------------------------------------------------
# Exception raised for invalid connection parameters.
class ConnectError(Exception):
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
        raise ConnectError("Constant is too big for target Signal!")
      else:
        src = Constant( dest.nbits, src )

    elif isinstance( dest, int ):
      if get_nbits( dest ) > src.nbits:
        raise ConnectError("Constant is too big for target Signal!")
      else:
        dest = Constant( src.nbits, dest )

    elif src.nbits != dest.nbits:
      raise ConnectError("Connecting signals with different bitwidths!")

    # Set the nbits attribute of the connection
    self.nbits = src.nbits

    # Set source and destination nodes and ranges
    self.src_node   = src._signal
    self.src_slice  = src._addr
    self.dest_node  = dest._signal
    self.dest_slice = dest._addr

    # Add ourselves to the src_node and dest_node connectivity lists
    # TODO: is this the right way to do this?
    src.connections  += [ self ]
    dest.connections += [ self ]

  #---------------------------------------------------------------------
  # other
  #---------------------------------------------------------------------
  # If given the src_node, return the dest_node.
  # If given the dest_node, return the src_node.
  # Assert if the provided node is neither the src_node or dest_node.
  def other( self, node ):
    assert self.src_node == node or self.dest_node == node
    if self.src_node == node:
      return self.dest_node
    else:
      return self.src_node

  #---------------------------------------------------------------------
  # is_dest
  #---------------------------------------------------------------------
  def is_dest( self, node ):
    return self.dest_node == node

  #---------------------------------------------------------------------
  # is_src
  #---------------------------------------------------------------------
  def is_src( self, node ):
    return self.src_node == node

  #---------------------------------------------------------------------
  # is_internal
  #---------------------------------------------------------------------
  # Return true if this connection belongs to the same parent module as
  # the provided node.
  def is_internal( self, node ):
    # Determine which node is the other in the connection
    other = self.other( node )

    # InPort connections to Constants are external, else internal
    if isinstance( self.src_node, Constant ):
      return not isinstance( self.dest_node, InPort )

    # Check if the connection is an internal connection for the node
    return (( self.src_node.parent == self.dest_node.parent ) or
            ( other.parent in node.parent._submodules ))

  #---------------------------------------------------------------------
  # swap_direction
  #---------------------------------------------------------------------
  # Swap the direction of the connection, the source becomes the
  # destination and vice versa.
  def swap_direction( self ):
    self.src_node,  self.dest_node  = self.dest_node,  self.src_node
    self.src_slice, self.dest_slice = self.dest_slice, self.src_slice

  #---------------------------------------------------------------------
  # __repr__
  #---------------------------------------------------------------------
  # Pretty printing of connections for debugging.
  def __repr__( self ):
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

