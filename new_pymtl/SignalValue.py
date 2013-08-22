#=========================================================================
# SignalValue.py
#=========================================================================
# Module containing the SignalValue class.

import inspect

#-------------------------------------------------------------------------
# SignalValue
#-------------------------------------------------------------------------
# Base class for value types, provides hooks used by SimulationTool.
# Any value that can be passed as a parameter to a Signal object
# (InPort, OutPort, Wire), needs to subclass SignalValue.
class SignalValue( object ):

  constant    = False
  _callbacks  = []
  _slices     = []

  #-----------------------------------------------------------------------
  # Write v property
  #-----------------------------------------------------------------------
  @property
  def v( self ):
    return self
  @property
  def value( self ):
    return self

  @v.setter
  def v( self, value ):
    if value != self:
      self.write_value( value )
      self.notify_sim_comb_update()
      for func in self._slices: func()
  @value.setter
  def value( self, value ):
    if value != self:
      self.write_value( value )
      self.notify_sim_comb_update()
      for func in self._slices: func()

  #-----------------------------------------------------------------------
  # Write n property
  #-----------------------------------------------------------------------
  @property
  def n( self ):
    return self._next
  @property
  def next( self ):
    return self._next

  @n.setter
  def n( self, value ):
    # TODO: add optimization?
    #if value != self._next:
    self.write_next( value )
    self.notify_sim_seq_update()
  @next.setter
  def next( self, value ):
    # TODO: add optimization?
    #if value != self._next:
    self.write_next( value )
    self.notify_sim_seq_update()

  #-----------------------------------------------------------------------
  # flop
  #-----------------------------------------------------------------------
  # Update the value to match the _next (flop the register).
  def flop( self ):
    self.v = self._next

  #-----------------------------------------------------------------------
  # write_value (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def write_value( self, value ):
    raise NotImplementedError( "Subclasses of SignalValue must "
                               "implement the write_value() method!" )

  #-----------------------------------------------------------------------
  # write_next (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def write_next( self, value ):
    raise NotImplementedError( "Subclasses of SignalValue must "
                               "implement the write_next() method!" )

  #-----------------------------------------------------------------------
  # uint (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def uint( self, value ):
    raise NotImplementedError( "Subclasses of SignalValue must "
                               "implement the uint() method!" )

  #-----------------------------------------------------------------------
  # int (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def int( self, value ):
    raise NotImplementedError( "Subclasses of SignalValue must "
                               "implement the int() method!" )

  #-----------------------------------------------------------------------
  # is_constant
  #-----------------------------------------------------------------------
  # Returns true if this SignalValue contains a constant value which
  # should never be written.
  def is_constant( self ):
    return self.constant

  #-----------------------------------------------------------------------
  # notify_sim_comb_update
  #-----------------------------------------------------------------------
  # Notify simulator of combinational update.
  # Another abstract method used as a hook by simulator tools.
  # Not meant to be implemented by subclasses.
  # NOTE: This approach uses closures, other methods can be found in:
  #       http://brg.csl.cornell.edu/wiki/lockhart-2013-03-18
  #       Is this the fastest approach?
  def notify_sim_comb_update( self ):
    pass

  #-----------------------------------------------------------------------
  # notify_sim_seq_update
  #-----------------------------------------------------------------------
  # Notify simulator of sequential update.
  # Another abstract method used as a hook by simulator tools.
  # Not meant to be implemented by subclasses.
  # NOTE: This approach uses closures, other methods can be found in:
  #       http://brg.csl.cornell.edu/wiki/lockhart-2013-03-18
  #       Is this the fastest approach?
  def notify_sim_seq_update( self ):
    pass

  #-----------------------------------------------------------------------
  # register_callback
  #-----------------------------------------------------------------------
  def register_callback( self, func_ptr ):
    if not self._callbacks:
      self._callbacks = []
    self._callbacks.append( func_ptr )

  #-----------------------------------------------------------------------
  # register_slice
  #-----------------------------------------------------------------------
  def register_slice( self, func_ptr ):
    if not self._slices:
      self._slices = []
    self._slices.append( func_ptr )

  #-----------------------------------------------------------------------
  # bitfields
  #-----------------------------------------------------------------------
  @property
  def bitfields( self ):
    return {}


#-------------------------------------------------------------------------
# SignalValueWrapper
#-------------------------------------------------------------------------
# Wrapper to turn arbitrary objects into SignalValues.
# Proxying magic borrowed from: http://stackoverflow.com/a/9059858
class SignalValueWrapper( SignalValue ):

  __wraps__  = None
  __ignore__ = "class mro new init setattr getattr getattribute nbits"

  nbits      = None

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( self ):
    if self.__wraps__ is None:
      raise TypeError("base class Wrapper may not be instantiated")
    self._data = self.__wraps__()

  #-----------------------------------------------------------------------
  # write_value
  #-----------------------------------------------------------------------
  # Provide implementation for required SignalValue abstract method.
  def write_value( self, value ):
    try:                   self._data = value._data
    except AttributeError: self._data = value

  #-----------------------------------------------------------------------
  # write_next
  #-----------------------------------------------------------------------
  # Provide implementation for required SignalValue abstract method.
  def write_next( self, value ):
    try:                   self._next._data = value._data
    except AttributeError: self._next._data = value

  #-----------------------------------------------------------------------
  # __getattr__
  #-----------------------------------------------------------------------
  # Proxy attribute access to the wrapped data.
  def __getattr__( self, name ):
    return getattr( self._data, name )

  #-----------------------------------------------------------------------
  # __metaclass__
  #-----------------------------------------------------------------------
  # Add metaclass magic to automatically create proxies for double-
  # underscore attribute access.
  class __metaclass__( type ):

    # Constructor for __metaclass__.
    def __init__( cls, name, bases, dct ):

      # Utility function to create proxying logic.
      def make_proxy( name ):
        def proxy( self, *args ):
          return getattr( self._data, name )
        return proxy

      # Create the warpper class.
      type.__init__( cls, name, bases, dct )

      # For each double-underscore attribute not in the __ignore__ list,
      # create a proxy attribute.
      if cls.__wraps__:
        ignore = set( "__%s__" % n for n in cls.__ignore__.split() )
        for name in dir( cls.__wraps__ ):
          if name.startswith("__"):
            if name not in ignore and name not in dct:
              attr = getattr( cls.__wraps__, name )
              setattr( cls, name, property( make_proxy( name ) ) )


#-------------------------------------------------------------------------
# CreateWrappedClass
#-------------------------------------------------------------------------
# Takes a class and returns a wrapped version of the class that can
# behave as a SignalValue (can be passed on Ports and Wires).
def CreateWrappedClass( cls ):

  class Wrapper( SignalValueWrapper ):
    __wraps__ = cls

  return Wrapper
