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
# _magic_methods
#-------------------------------------------------------------------------
_magic_methods = [
      '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
      '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
      '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
      '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
      '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
      '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
      '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
      '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
      '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
      '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
      '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
      '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
      '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
      '__truediv__', '__xor__', 'next',
  ]


#-------------------------------------------------------------------------
# SignalValueWrapper
#-------------------------------------------------------------------------
# Wrapper to turn arbitrary objects into SignalValues.
class SignalValueWrapper( SignalValue ):
  nbits = None
  def write_value( self, value ):
    try:                   self._data = value._data
    except AttributeError: self._data = value
  def write_next( self, value ):
    try:                   self._next._data = value._data
    except AttributeError: self._next._data = value

#-------------------------------------------------------------------------
# _make_func
#-------------------------------------------------------------------------
def _make_func( attr):
  def func( obj, *args, **kwargs ):
    return getattr( obj._data, attr )( *args, **kwargs )
  return func

#-------------------------------------------------------------------------
# CreateWrappedClass
#-------------------------------------------------------------------------
def CreateWrappedClass( cls ):

  classdict = {}
  for attr, kind, c, o in inspect.classify_class_attrs( cls ):
    if kind == 'method' and (
       not attr.startswith('__') or attr in _magic_methods ):

         classdict[ attr ] = _make_func( attr )

  x = type( 'Wrapped_'+cls.__name__, (SignalValueWrapper,), classdict )
  x._data = cls()
  return x

