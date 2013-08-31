#=========================================================================
# metaclasses.py
#=========================================================================
# Collection of metaclasses to implement python magic.
#

#=========================================================================
# __metaclass__
#=========================================================================
# Metaclass implementing syntactic sugar for creating a list of identical
# objects. Classes inheriting from this metaclass can use the following
# shorthand:
#
#   var = MyObject[ 4 ]( arg1, arg2, arg3 )
#
# The above produces the same result as the following list-comprehension:
#
#   var = [ MyModel( arg1, arg2, arg3 ) for x in range( nitems ) ]
#
# An alternative, more explicit syntax is also provided using the list()
# class method:
#
#   var = MyObject.list( 4 )( arg1, arg2, arg3 )
#
class MetaListConstructor( type ):

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------
  # Class method which returns a lambda-wrapped list comprehension. When
  # called, the lambda generates a list containing n instances of type
  # cls, where n is integer passed within [] brackets, and cls is the
  # object class the [] operator was called on. Any args received by the
  # lambda are proxied to the cls constructor.
  #
  # http://stackoverflow.com/a/12447078
  def __getitem__( cls, n ):
    return lambda *args, **kwargs : [ cls( *args, **kwargs ) for x in range( n ) ]

  #-----------------------------------------------------------------------
  # list
  #-----------------------------------------------------------------------
  # Same implementation as __getitem__, but a much more explicit
  def list( cls, n ):
    return lambda *args, **kwargs : [ cls( *args, **kwargs ) for x in range( n ) ]

