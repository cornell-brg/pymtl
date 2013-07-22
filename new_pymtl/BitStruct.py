#=========================================================================
# BitStruct
#=========================================================================

#from signals import Signal, InPort, OutPort, Wire, Constant
from Bits import Bits

#-------------------------------------------------------------------------
# BitField
#-------------------------------------------------------------------------
class BitField( object ):
  # http://stackoverflow.com/a/2014002
  ids = 0

  def __init__( self, nbits ):
    self.nbits    = nbits
    self.id       = BitField.ids
    BitField.ids += 1

#-------------------------------------------------------------------------
# MetaBitStruct
#-------------------------------------------------------------------------
class MetaBitStruct( type ):

  #-----------------------------------------------------------------------
  # __call__
  #-----------------------------------------------------------------------
  def __call__( self, *args, **kwargs ):

    # Create a class instance using the default definition of __call__
    inst = super( MetaBitStruct, self ).__call__( *args, **kwargs )

    # Properties are per class, not per instance, so we need to create
    # a one-of-a-kind class type (not instance!) and assign it to this
    # BitStruct instance. This is necessary so that each instance of the
    # message has its properties set.  HACKY!!!
    # http://stackoverflow.com/a/1633363
    inst.__class__ = type( inst.__class__.__name__, ( inst.__class__, Bits ), {} )

    # Get all the members of type BitField, sort them by order of declaration
    # TODO: sort objects in dictionary..
    fields = [(name, obj) for name, obj in
              inst.__dict__.items() if isinstance( obj, BitField )]
    fields.sort( lambda (n1, o1), (n2, o2) : cmp(o2.id, o1.id) )

    # Get the total size of the BitStruct
    nbits = sum( [ f.nbits for name, f in fields ] )

    start_pos = 0
    inst._bitfields = {}

    # Transform attributes containing BitField objects into properties so that
    # when accessed they return slices of the underlying value
    for name, f in fields:

      # Calculate address range, update start_pos
      end_pos   = start_pos + f.nbits
      addr      = slice( start_pos, end_pos )
      start_pos = end_pos

      # Add slice to bitfields
      inst._bitfields[ name ] = addr

      # Create a getter to assign to the property
      def create_getter( addr ):
        return lambda self : self.__getitem__( addr )

      # Create a setter to assign to the property
      # TODO: not needed when returning ConnectionSlice and accessing .value
      def create_setter( addr ):
        return lambda self, value: self.__setitem__( addr, value )

      # Apply the property
      setattr( inst.__class__, name,
               property( create_getter( addr ),
                         create_setter( addr )
                       )
             )

    # Call the parent constructor (Bits)
    super( BitStruct, inst ).__init__( nbits )

    # Return the instance
    return inst

#-------------------------------------------------------------------------
# BitStruct
#-------------------------------------------------------------------------
class BitStruct( Bits ):
  __metaclass__ = MetaBitStruct

  @property
  def bitfields( self ):
    return self._bitfields

