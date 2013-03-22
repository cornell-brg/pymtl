#=========================================================================
# Signals
#=========================================================================

from connection_graph import ConnectionSlice, ConnectionEdge

#-------------------------------------------------------------------------
# Port Base Class
#-------------------------------------------------------------------------
# Hidden base class implementing a module port.
#
class Port( object ):

  def __init__( self, msg_type ):
    """Constructor for a Port object.

    Parameters
    ----------
    msg_type: msg type on the port.
    """
    # TODO: replace width with nbits!!!
    if isinstance( msg_type, int ):
      self.nbits  = msg_type
    else:
      self.nbits  = msg_type.nbits
    self._addr  = None
    self.name   = "NO NAME: not elaborated yet!"
    self.parent = None
    # Connections used by Simulation Tool
    self.connections     = []
    # Connections used by VerilogTranslationTool
    # TODO: merge these different types of connections?
    self.inst_connection = None
    # Connections defined inside a module implementation
    self.int_connections = []
    # Connections defined when instantiating a model
    self.ext_connections = []
    # Needed by VerilogTranslationTool
    self.is_reg = False

  def __getitem__( self, addr ):
    """Bitfield access ([]). Returns a Slice object."""
    return ConnectionSlice( self, addr )

  def connect( self, target ):
    """Creates a connection with a Port or Slice."""
    # Port-to-Port connections, used for translation
    connection_edge     = ConnectionEdge( self, target )
    self.connections   += [ connection_edge ]
    target.connections += [ connection_edge ]

  # TODO: temporary hack for VCD
  @property
  def _code( self ):
    """Access the parent of this port."""
    return self.node._code
  @_code.setter
  def _code( self, code ):
    self.node._code = code

  @property
  def width( self ):
    """Temporary"""
    return self.nbits

  #-----------------------------------------------------------------------
  # Unaccessible attributes
  #-----------------------------------------------------------------------
  # Prevent reading/writing the following attributes to prevent
  # confusion between Ports (Signals? Channels?) and Values
  @property
  def v( self ):
    raise AttributeError( "ports/wires have no .v attribute!" )
  @v.setter
  def v( self, value ):
    raise AttributeError( "ports/wires have no .v attribute!" )
  @property
  def value( self ):
    raise AttributeError( "ports/wires have no .value attribute!" )
  @value.setter
  def value( self, value ):
    raise AttributeError( "ports/wires have no .value attribute!" )
  @property
  def n( self ):
    raise AttributeError( "ports/wires have no .n attribute!" )
  @n.setter
  def n( self, value ):
    raise AttributeError( "ports/wires have no .n attribute!" )
  @property
  def next( self ):
    raise AttributeError( "ports/wires have no .next attribute!" )
  @next.setter
  def next( self, value ):
    raise AttributeError( "ports/wires have no .next attribute!" )

  #def line_trace( self ):
  #  return self._msg.line_trace()

#-------------------------------------------------------------------------
# InPort
#-------------------------------------------------------------------------
# User visible implementation of an input port.
class InPort( Port ):

  def __init__( self, nbits ):
    """Constructor for an InPort object.

    Parameters
    ----------
    nbits: bitwidth of the port.
    """
    super( InPort, self ).__init__( nbits )

#-------------------------------------------------------------------------
# OutPort
#-------------------------------------------------------------------------
# User visible implementation of an output port.
class OutPort( Port ):

  def __init__( self, nbits ):
    """Constructor for an OutPort object.

    Parameters
    ----------
    nbits: bitwidth of the port.
    """
    super( OutPort, self ).__init__( nbits )

#-------------------------------------------------------------------------
# Wire
#-------------------------------------------------------------------------
# User visible implementation of a wire.
class Wire( Port ):

  def __init__( self, nbits ):
    """Constructor for an Wire object.

    Parameters
    ----------
    nbits: bitwidth of the wire.
    """
    super( Wire, self ).__init__( nbits )

#-------------------------------------------------------------------------
# ImplicitWire
#-------------------------------------------------------------------------
# TODO: remove?

#class ImplicitWire(object):
#
#  """Hidden class to represent wires implicitly generated from connections."""
#
#  def __init__(self, name, width):
#    """Constructor for a ImplicitWire object.
#
#    Parameters
#    ----------
#    name: name of the wire.
#    width: bitwidth of the wire.
#    """
#    self.name   = name
#    self.width  = width
#    self.type   = "wire"
#    self.is_reg = False
#
#  def verilog_name(self):
#    return self.name
