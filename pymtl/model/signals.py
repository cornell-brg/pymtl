#=======================================================================
# signals.py
#=======================================================================
"""Collection of classes for defining interfaces and connectivity in
hardware models."""

from metaclasses      import MetaListConstructor
from ..datatypes.Bits import Bits

#-----------------------------------------------------------------------
# Signal
#-----------------------------------------------------------------------
class Signal( object ):
  """Base class implementing any Signal (port, wire, constant) that can
  carry a SignalValue."""

  __metaclass__ = MetaListConstructor

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, msg_type ):
    """Construct a new Signal for carrying data of type msg_type.

    Note that msg_type should be a subclass of SignalValue, like Bits:

    >>> Signal( Bits( 5 ) )

    If the msg_type parameter provided is an integer value instead of a
    SignalValue, the msg_type will instead b set to be Bits( msg_type ).

    >>> Signal( 5 )  # Equivalent to Signal( Bits( 5 ) )
    """

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
    """Proxy attribute accesses to the underlying msg_type so we can refer
    to fields when the msg_type is a BitStruct."""

    if name in self.msg_type.bitfields:
      return self[ self.msg_type.bitfields[ name ] ]
    raise AttributeError( "'{}' object has no attribute '{}'"
                          .format( self.__class__.__name__, name ) )

  #---------------------------------------------------------------------
  # __getitem__
  #---------------------------------------------------------------------
  def __getitem__( self, addr ):
    """Bitfield access ([]) returns a _SignalSlice object."""

    return _SignalSlice( self, addr )

  #---------------------------------------------------------------------
  # fullname
  #---------------------------------------------------------------------
  @property
  def fullname( self ):
    """Return Signal name formatted as "parent_model_name.signal_name".
    """

    parent_name = self.parent.name if self.parent else '?'
    return "{}.{}".format( parent_name, self.name )

  #---------------------------------------------------------------------
  # Protected attributes
  #---------------------------------------------------------------------
  # Prevent reading/writing the following attributes to prevent
  # confusion between Signal objects and SignalValue objects.
  @property
  def v( self ):
    """Invalid attribute, accessing raises an AttributeError!"""
    raise AttributeError( "ports/wires have no .v attribute!" )
  @v.setter
  def v( self, value ):
    raise AttributeError( "ports/wires have no .v attribute!" )
  @property
  def value( self ):
    """Invalid attribute, accessing raises an AttributeError!"""
    raise AttributeError( "ports/wires have no .value attribute!" )
  @value.setter
  def value( self, value ):
    raise AttributeError( "ports/wires have no .value attribute!" )
  @property
  def n( self ):
    """Invalid attribute, accessing raises an AttributeError!"""
    raise AttributeError( "ports/wires have no .n attribute!" )
  @n.setter
  def n( self, value ):
    raise AttributeError( "ports/wires have no .n attribute!" )
  @property
  def next( self ):
    """Invalid attribute, accessing raises an AttributeError!"""
    raise AttributeError( "ports/wires have no .next attribute!" )
  @next.setter
  def next( self, value ):
    raise AttributeError( "ports/wires have no .next attribute!" )


#-----------------------------------------------------------------------
# InPort
#-----------------------------------------------------------------------
class InPort( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, msg_type ):
    """Construct a new InPort for carrying data of type msg_type.

    Note that msg_type should be a subclass of SignalValue, like Bits:

    >>> InPort( Bits( 5 ) )

    If the msg_type parameter provided is an integer value instead of a
    SignalValue, the msg_type will instead b set to be Bits( msg_type ).

    >>> InPort( 5 )  # Equivalent to InPort( Bits( 5 ) )
    """
    super( InPort, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# OutPort
#-----------------------------------------------------------------------
class OutPort( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, msg_type ):
    """Construct a new OutPort for carrying data of type msg_type.

    Note that msg_type should be a subclass of SignalValue, like Bits:

    >>> OutPort( Bits( 5 ) )

    If the msg_type parameter provided is an integer value instead of a
    SignalValue, the msg_type will instead b set to be Bits( msg_type ).

    >>> OutPort( 5 )  # Equivalent to OutPort( Bits( 5 ) )
    """
    super( OutPort, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# Wire
#-----------------------------------------------------------------------
# User visible implementation of a wire.
class Wire( Signal ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, msg_type ):
    """Construct a new Wire for carrying data of type msg_type.

    Note that msg_type should be a subclass of SignalValue, like Bits:

    >>> Wire( Bits( 5 ) )

    If the msg_type parameter provided is an integer value instead of a
    SignalValue, the msg_type will instead b set to be Bits( msg_type ).

    >>> Wire( 5 )  # Equivalent to Wire( Bits( 5 ) )
    """
    super( Wire, self ).__init__( msg_type )

#-----------------------------------------------------------------------
# Constant
#-----------------------------------------------------------------------
class Constant( Signal ):
  """Hidden class implementing a constant valued Signal."""

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  #  nbits: bitwidth of the constant.
  #  value: integer value of the constant.
  def __init__( self, nbits, value ):
    """Construct a contant valued Signal with the specified value and
    bitwidth provided in nbits.
    """
    super( Constant, self ).__init__( nbits )

    # Special case the name and _signalvalue attributes
    self.name         = "{}'d{}".format( nbits, value )
    self._signalvalue = value
    # TODO: no parent, causes AttributeError when debugging, fix?
    #self.parent      = DummyParent

  #---------------------------------------------------------------------
  # fullname
  #---------------------------------------------------------------------
  @property
  def fullname( self ):
    """Constants don't have a parent (should they?) so the fullname is
    simply simply a string describing the bitwidth + value of the
    constant."""
    return self.name

  #---------------------------------------------------------------------
  # __eq__
  #---------------------------------------------------------------------
  # TODO: temporary?
  def __eq__( self, other ):
    """Not sure why this equality check is needed..."""
    return self._signalvalue == other._signalvalue

#-----------------------------------------------------------------------
# _SignalSlice
#-----------------------------------------------------------------------
class _SignalSlice( object ):
  """Hidden class representing a subslice of a Signal.

  _SignalSlices are temporary objects constructed when structurally
  connecting Signals.
  """

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( self, signal, addr ):
    """Create a _SignalSlice from Signal = signal and bits = addr."""

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
  # Necessary? If so, do the same for _signalvalue?
  @property
  def connections( self ):
    """Proxy .connections to our parent Signal's connections."""
    return self._signal.connections
  @connections.setter
  def connections( self, value ):
    self._signal.connections = value

  #---------------------------------------------------------------------
  # __getitem__
  #---------------------------------------------------------------------
  def __getitem__( self, addr ):
    """Enable subslicing of a SignalSlice. Does this work?"""

    #TODO THIS ONLY WORKS FOR SLICE + INT
    return self._signal[self._addr.start+addr]


