#=========================================================================
# signals.py
#=========================================================================
# Collection of classes for defining interfaces and connectivity in PyMTL
# hardware models.

#-------------------------------------------------------------------------
# Signal
#-------------------------------------------------------------------------
# Hidden base class implementing any Signal (port, wire, or constant) that
# can carry a value.
class Signal( object ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    if isinstance( msg_type, int ):
      self.nbits          = msg_type
    else:
      self.nbits          = msg_type.nbits
    self._addr            = None
    self.name             = "NO NAME: not elaborated yet!"
    self.parent           = None
    self.connections      = []
    self._int_connections = []
    self._ext_connections = []
    self._signalvalue     = None

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------
  # Bitfield access ([]). Returns a Slice object.
  def __getitem__( self, addr ):
    # TODO: temporary hack
    from connection_graph import ConnectionSlice
    return ConnectionSlice( self, addr )

  #-----------------------------------------------------------------------
  # width
  #-----------------------------------------------------------------------
  # TEMPORARY: for backwards compatibility
  @property
  def width( self ):
    return self.nbits

  @property
  def fullname( self ):
    return "{}.{}".format( self.parent.name, self.name )

  #-----------------------------------------------------------------------
  # Unaccessible attributes
  #-----------------------------------------------------------------------
  # Prevent reading/writing the following attributes to prevent
  # confusion between Signals (Channels?) and Values
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
class InPort( Signal ):

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
class OutPort( Signal ):

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
class Wire( Signal ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( Wire, self ).__init__( msg_type )

#-------------------------------------------------------------------------
# Constant
#-------------------------------------------------------------------------
# Hidden class implementing a Constant value.
class Constant( Signal ):

  def __init__( self, nbits, value ):
    super( Constant, self ).__init__( nbits )
    self._signalvalue = value
    self.name = "{}'d{}".format( nbits, value )

  @property
  def fullname( self ):
    # Constants don't have a parent (should they?) so the fullname
    # is simply the name
    return self.name

  # TODO: temporary?
  def __eq__( self, other ):
    return self._signalvalue == other._signalvalue

