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
class MetaListConstructor( type ):

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------
  # Class method which returns a lambda-wrapped list comprehension. When
  # called, the lambda generates a list containing n instances of type
  # cls, where n is integer passed within [] brackets, and cls is the
  # object class the [] operator was called on. Any args received by the
  # lambda are proxied to the cls constructor.
  def __getitem__( cls, n ):
    return lambda *args : [ cls( *args ) for x in range( n ) ]

