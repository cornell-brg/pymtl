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
        return lambda self : self.value.__getitem__( addr )
      # Create a setter to assign to the property
      def create_setter( nbits, width ):
        addr = slice( nbits, nbits + width )
        return lambda self, value: self.value.__setitem__( addr, value )
      # Create the property
      setattr( inst.__class__, name, property( create_getter( nbits, width ),
                                               create_setter( nbits, width ) ))
      nbits += width
    # Set total width
    setattr( inst, 'width', nbits )
    setattr( inst, 'value', Bits( 64, 0x0f0f0f0f0f ) )
    return inst

class BitStruct( object ):
  __metaclass__ = MetaBitStruct


#-------------------------------------------------------------------------
# Memory Example
#-------------------------------------------------------------------------

class mem_type( object ):
  rd = 0
  wr = 1

class mem_len( object ):
  byte  = 1
  half  = 2
  word  = 0

class MemMsg( BitStruct ):

  def __init__( self, addr_nbits, data_nbits ):

    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    len = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    self.type = Field( 1 )
    self.len  = Field( len )
    self.addr = Field( addr_nbits )
    self.data = Field( data_nbits )

x = MemMsg( 16, 16 )
print 'type',  x.type
print 'len',   x.len
print 'addr',  x.addr
print 'data',  x.data
print 'width', x.width

x.type = mem_type.rd
print x.type

# Field( width )
# Field( start, width )
# Field( start, stop )  # Excl, like python range

# USAGE
# def __init__( self ):
#   my_msg = MemMsg.MemMsg( 16, 32 )
#   self.in_ = InPort ( my_msg )
#   self.out = OutPort( my_msg )
#
#   connect( self.in_.addr, some_other_thing )
#
# @combinational
# def logic( self ):
#   self.out.data.value = self.in_.data.value

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

