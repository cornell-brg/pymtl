#=======================================================================
# signal_lists.py
#=======================================================================
"""Collection of special list classes used internally by PyMTL tools.

These list classes provide additonal information to PyMTL tools
inspecting PyMTL models. They additionally enable monkey-patching, which
is not allowed on the Python built-in list.
"""

#-----------------------------------------------------------------------
# PortList
#-----------------------------------------------------------------------
class PortList( list ):
  """A list containing PyMTL InPort or OutPort Signals."""

  def get_ports( self ):
    """Getter provides same interface as Model."""
    return self

  def __hash__( self ):
    """Allow PortLists to be hashable."""
    return hash( tuple(self) )

#-----------------------------------------------------------------------
# WireList
#-----------------------------------------------------------------------
class WireList( list ):
  """A list containing PyMTL Wire Signals."""

  def get_wires( self ):
    """Getter provides same interface as Model."""
    return self

  def __hash__( self ):
    """Allow PortLists to be hashable."""
    return hash( tuple(self) )
