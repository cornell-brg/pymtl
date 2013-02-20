#=========================================================================
# BitStruct
#=========================================================================

from model import *

#-------------------------------------------------------------------------
# Field
#-------------------------------------------------------------------------

class Field( object ):
  # http://stackoverflow.com/a/2014002
  ids = 0

  def __init__( self, width ):
    self.width  = width
    self.id     = Field.ids
    Field.ids  += 1

#-------------------------------------------------------------------------
# BitStruct
#-------------------------------------------------------------------------

class MetaBitStruct( type ):

  def __call__( self, *args, **kwargs ):
    inst = super(MetaBitStruct, self).__call__(*args, **kwargs)
    # HACKY: change class to be unique, this is necessary so that
    # each instance of the message has its properties set
    # http://stackoverflow.com/a/1633363
    inst.__class__ = type( inst.__class__.__name__, ( inst.__class__, object ), {} )
    # Get all the members of type Field, sort them by order of declaration
    fields = [(name, obj) for name, obj in
              inst.__dict__.items() if isinstance(obj, Field)]
    fields.sort( lambda (n1, o1), (n2, o2) : cmp(o2.id, o1.id) )
    # transform attributes containing Field objects into properties so that
    # when accessed they return slices of the underlying value
    nbits = 0
    for name, f in fields:
      width = f.width
      # Create a getter to assign to the property
      def create_getter( nbits, width ):
        addr = slice( nbits, nbits + width )
        return lambda self : self._signal.__getitem__( addr )
      # Create a setter to assign to the property
      # TODO: not needed when returning ConnectionSlice and accessing .value
      #def create_setter( nbits, width ):
      #  addr = slice( nbits, nbits + width )
      #  return lambda self, value: self._signal.__setitem__( addr, value )
      # Create the property
      setattr( inst.__class__, name,
               property( create_getter( nbits, width ) )
             )
      nbits += width
    # Set total width
    setattr( inst, 'width', nbits )
    return inst

class BitStruct( object ):
  __metaclass__ = MetaBitStruct


#-------------------------------------------------------------------------
# Inst Example
#-------------------------------------------------------------------------

#class ParcInst( BitStruct ):
#
#  op    = slice( 26, )
#  rs    = slice( 21, 26 )
#  rt    = slice( 16, 21 )
#  rd    = slice( 11, 16 )
#  shamt = slice(  6, 11 )
#  func  = slice(  0,  6 )
#  imm   = slice(  0, 16 )
#  tgt   = slice(  0, 26 )
#  #-----------------------------------------------------------------------
#  # Constructor
#  #-----------------------------------------------------------------------
#  def __init__( self, msg ):
#
#    self.op    = slice( 26, 32 )
#    self.rs    = slice( 21, 26 )
#    self.rt    = slice( 16, 21 )
#    self.rd    = slice( 11, 16 )
#    self.shamt = slice(  6, 11 )
#    self.func  = slice(  0,  6 )
#    self.imm   = slice(  0, 16 )
#    self.tgt   = slice(  0, 26 )
