#=======================================================================
# signals.py
#=======================================================================
# Collection of classes for defining interfaces and connectivity in
# hardware models.

from metaclasses import MetaListConstructor
from Bits        import Bits

#-----------------------------------------------------------------------
# Signal
#-----------------------------------------------------------------------
# Base class implementing any Signal (port, wire, constant) that can
# carry a SignalValue.
class Signal( object ):

  __metaclass__ = MetaListConstructor

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):

    is_int             = isinstance( msg_type, int )
    self.msg_type      = msg_type if not is_int else Bits( msg_type )
    self.nbits         = self.msg_type.nbits
    self.slice         = slice( None )

    self.name          = "NO NAME: not elaborated yet!"
    self.parent        = None
    self.connections   = []

    self._addr         = None
    self._signal       = self
    self._signalvalue  = None

  #---------------------------------------------------------------------
  # __getattr__
  #---------------------------------------------------------------------
  def __getattr__( self, name ):
    if name in self.msg_type.bitfields:
      return self[ self.msg_type.bitfields[ name ] ]
    raise AttributeError( "'{}' object has no attribute '{}'"
                          .format( self.__class__.__name__, name ) )

  #---------------------------------------------------------------------
  # __getitem__
  #---------------------------------------------------------------------
  # Bitfield access ([]). Returns a SignalSlice object.
  def __getitem__( self, addr ):
    return _SignalSlice( self, addr )

  #---------------------------------------------------------------------
  # fullname
  #---------------------------------------------------------------------
  # Return name of Signal with format 'parent_model_name.signal_name'.
  @property
  def fullname( self ):
    parent_name = self.parent.name if self.parent else '?'
    return "{}.{}".format( parent_name, self.name )

  #---------------------------------------------------------------------
  # Protected attributes
  #---------------------------------------------------------------------
  # Prevent reading/writing the following attributes to prevent
  # confusion between Signal objects and SignalValue objects.
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

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  #def line_trace( self ):
  #  return self._msg.line_trace()

#-----------------------------------------------------------------------
# InPort
#-----------------------------------------------------------------------
# User visible implementation of an input port.
class InPort( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( InPort, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# OutPort
#-----------------------------------------------------------------------
# User visible implementation of an output port.
class OutPort( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( OutPort, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# Wire
#-----------------------------------------------------------------------
# User visible implementation of a wire.
class Wire( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  msg_type: msg type on the port.
  def __init__( self, msg_type ):
    super( Wire, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# Constant
#-----------------------------------------------------------------------
# Hidden class implementing a constant value Signal.
class Constant( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  nbits: bitwidth of the constant.
  #  value: integer value of the constant.
  def __init__( self, nbits, value ):
    super( Constant, self ).__init__( nbits )

    # Special case the name and _signalvalue attributes
    self.name         = "{}'d{}".format( nbits, value )
    self._signalvalue = value
    # TODO: no parent, causes AttributeError when debugging, fix?
    #self.parent      = DummyParent

  #---------------------------------------------------------------------
  # fullname
  #---------------------------------------------------------------------
  # Constants don't have a parent (should they?) so the fullname is
  # simply simply a string describing the bitwidth + value of the
  # constant.
  @property
  def fullname( self ):
    return self.name

  #---------------------------------------------------------------------
  # __eq__
  #---------------------------------------------------------------------
  # TODO: temporary?
  def __eq__( self, other ):
    return self._signalvalue == other._signalvalue

#-----------------------------------------------------------------------
# _SignalSlice
#-----------------------------------------------------------------------
# Hidden class representing a subslice of a Signal. _SignalSlices are
# temporary objects constructed when structurally connecting Signals.
class _SignalSlice( object ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, signal, addr ):

    # Handle slices of the form x[ idx ] and x[ start : stop ]
    is_slice   = isinstance( addr, slice )
    self.nbits = (addr.stop - addr.start) if is_slice else 1
    self.slice = addr

    # Steps are not supported!
    if is_slice: assert not addr.step

    # _signal points to the Signal object we are slicing
    self._addr   = addr
    self._signal = signal

  #---------------------------------------------------------------------
  # connections
  #---------------------------------------------------------------------
  # Make .connections reference our parent Signal's connections.
  # Necessary? If so, do the same for _signalvalue?
  @property
  def connections( self ):
    return self._signal.connections
  @connections.setter
  def connections( self, value ):
    self._signal.connections = value


