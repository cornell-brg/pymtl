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

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    if isinstance( msg_type, int ):
      self.nbits         = msg_type
    else:
      self.nbits         = msg_type.nbits
    self._addr           = None
    self.name            = "NO NAME: not elaborated yet!"
    self.parent          = None
    self.connections     = []
    self.int_connections = []
    self.ext_connections = []

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------
  # Bitfield access ([]). Returns a Slice object.
  def __getitem__( self, addr ):
    return ConnectionSlice( self, addr )

  #-----------------------------------------------------------------------
  # connect
  #-----------------------------------------------------------------------
  # Creates a connection with a Port or Slice.
  def connect( self, target ):
    connection_edge     = ConnectionEdge( self, target )
    self.connections   += [ connection_edge ]
    target.connections += [ connection_edge ]

  #-----------------------------------------------------------------------
  # width
  #-----------------------------------------------------------------------
  # TEMPORARY: for backwards compatibility
  @property
  def width( self ):
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

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( InPort, self ).__init__( msg_type )

#-------------------------------------------------------------------------
# OutPort
#-------------------------------------------------------------------------
# User visible implementation of an output port.
class OutPort( Port ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( OutPort, self ).__init__( msg_type )

#-------------------------------------------------------------------------
# Wire
#-------------------------------------------------------------------------
# User visible implementation of a wire.
class Wire( Port ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( Wire, self ).__init__( nbits )
