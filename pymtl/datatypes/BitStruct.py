#=======================================================================
# BitStruct.py
#=======================================================================

from __future__ import print_function

from Bits import Bits

#=======================================================================
# MetaBitStruct
#=======================================================================
class MetaBitStruct( type ):

  #---------------------------------------------------------------------
  # __new__
  #---------------------------------------------------------------------
  #def __new__( meta, classname, supers, classdict ):
  #  #print( "- Meta NEW", classname )  # DEBUG
  #  return type.__new__( meta, classname, supers, classdict )

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  # Use __init__ instead of __new__ because we are saving the classdict
  # for later use during __call__.  Class attributes and instance
  # methods don't show up in the classdict during __new__!
  def __init__( meta, classname, supers, classdict ):
    #print( "- Meta INIT", classname )  # DEBUG

    # Save the classdict of the BitStructDefinition class (aka. the
    # users # definition for a BitStruct). We'll need this to add the
    # class constants to the new BitStruct class we create later.
    #
    # TODO: should we leave __module__?
    meta._classdict = {key: val for key, val in classdict.items()
                       if not key.startswith('_')}
    return type.__init__( meta, classname, supers, classdict )

  #---------------------------------------------------------------------
  # __call__
  #---------------------------------------------------------------------
  # Takes an instantiation of type BitStructDefinition, and generates a
  # new subclass BitStruct. Returns an instance of the newly created
  # BitStruct class.
  #
  # This approach is necessary because Python properties (our bitfields)
  # are per class, not per instance. This requires creating a new class
  # class type (not instance!) and dynamically adding propreties to it.
  # This is necessary so that each instance of the message has its
  # properties set.  More details can be found here:
  #
  #   http://stackoverflow.com/a/1633363
  #
  def __call__( self, *args, **kwargs ):
    #print( "- Meta CALL", args )   # DEBUG

    # Instantiate the user-created BitStructDefinition class
    def_inst = super( MetaBitStruct, self ).__call__( *args, **kwargs )

    # Get all the members of type BitField from the BitStructDefinition
    # instance. Sort them by order of declaration (stored by the
    # BitField objects). TODO: sort objects in dictionary..
    fields = [(name, obj) for name, obj in
              def_inst.__dict__.items() if isinstance( obj, BitField )]
    fields.sort( lambda (n1, o1), (n2, o2) : cmp(o2.id, o1.id) )

    # Get the total size of the BitStruct
    nbits = sum( [ f.nbits for name, f in fields ] )

    # Create the new BitStruct class, then instantiate it
    name_prfx       = def_inst.__class__.__name__
    name_sufx       = '_'.join(str(x) for x in args)
    class_name      = "{}_{}".format( name_prfx, name_sufx )
    bitstruct_class = type( class_name, ( BitStruct, ), self._classdict )

    # Keep track of bit positions for each bitfield
    start_pos = 0
    bitstruct_class._bitfields = {}

    # Transform attributes containing BitField objects into properties,
    # when accessed they return slices of the underlying value
    for attr_name, bitfield in fields:

      # Calculate address range, update start_pos
      end_pos   = start_pos + bitfield.nbits
      addr      = slice( start_pos, end_pos )
      start_pos = end_pos

      # Add slice to bitfields
      bitstruct_class._bitfields[ attr_name ] = addr

      # Create a getter to assign to the property
      def create_getter( addr ):
        return lambda self : self.__getitem__( addr )

      # Create a setter to assign to the property
      # TODO: not needed when returning ConnectionSlice and accessing .value
      def create_setter( addr ):
        return lambda self, value: self.__setitem__( addr, value )

      # Add the property to the class
      setattr( bitstruct_class, attr_name,
               property( create_getter( addr ),
                         create_setter( addr )
                       )
             )

    if '__str__' in def_inst.__class__.__dict__:
      bitstruct_class.__str__ = def_inst.__class__.__dict__['__str__']

    # Return an instance of the new BitStruct class
    bitstruct_inst = bitstruct_class( nbits )

    # TODO: hack for verilog translation!
    bitstruct_inst._module    = def_inst.__class__.__module__
    bitstruct_inst._classname = def_inst.__class__.__name__
    bitstruct_inst._instantiate = '{class_name}{args}'.format(
        class_name = def_inst.__class__.__name__,
        args       = args,
    )
    assert not kwargs

    return bitstruct_inst

#=======================================================================
# BitStructDefinition
#=======================================================================
# Users wishing to define a new BitStruct type should create a new class
# which subclasses BitStructDefinition, then define fields using the
# BitField type (below). The parameterizable BitStructDefinition defined
# by the user is then used to create new classes of type BitStruct.
#
class BitStructDefinition( object ):
  __metaclass__ = MetaBitStruct

#=======================================================================
# BitField
#=======================================================================
# Defines a bit field when creating a BitStructDefinition.
#
class BitField( object ):
  # http://stackoverflow.com/a/2014002
  ids = 0

  def __init__( self, nbits ):
    self.nbits    = nbits
    self.id       = BitField.ids
    BitField.ids += 1

#=======================================================================
# BitStruct
#=======================================================================
# Superclass of BitStruct classes/objects generated by calling classes
# of type BitStructDefinition.
#
class BitStruct( Bits ):

  #---------------------------------------------------------------------
  # bitfields
  #---------------------------------------------------------------------
  # Allow interrogation of all bitfields in a BitStruct.
  #
  @property
  def bitfields( self ):
    return self._bitfields

  #---------------------------------------------------------------------
  # __call__
  #---------------------------------------------------------------------
  # Allows BitStruct objects to act as both instances and types.  Calling
  # a BitStruct instance generates a new instance of that object. This
  # allows the following syntax
  #
  #   # MyBitStruct acting as a type
  #   dtype     = MyBitStruct( 32, 32 )
  #   msg_inst1 = dtype()
  #
  #   # MyBitStruct acting as an instance
  #   msg_inst2 = MyBitStruct( 32, 32 )
  #   msg_inst.fieldA = 12
  #   msg_inst.fieldB = 32
  #
  def __call__( self ):
    #print( "-CALL", type( self ) )
    return type( self )( self.nbits )

  #---------------------------------------------------------------------
  # __hash__
  #---------------------------------------------------------------------
  def __hash__( self ):
    return hash( (self.__class__.__name__, self._uint) )
