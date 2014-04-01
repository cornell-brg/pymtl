#=========================================================================
# metaclasses.py
#=========================================================================
# Collection of metaclasses to implement python magic.

import inspect
import collections

#-----------------------------------------------------------------------
# MetaListConstructor
#-----------------------------------------------------------------------
# Metaclass implementing syntactic sugar for creating a list of
# identical objects. Classes inheriting from this metaclass can use the
# following shorthand:
#
#   var = MyObject[ 4 ]( arg1, arg2, arg3 )
#
# The above produces the same result as the following list-comprehension:
#
#   var = [ MyModel( arg1, arg2, arg3 ) for x in range( nitems ) ]
#
# An alternative, more explicit syntax is also provided using the list() class
# method:
#
#   var = MyObject.list( 4 )( arg1, arg2, arg3 )
#
class MetaListConstructor( type ):

  #---------------------------------------------------------------------
  # __getitem__
  #---------------------------------------------------------------------
  # Class method which returns a lambda-wrapped list comprehension. When
  # called, the lambda generates a list containing n instances of type
  # cls, where n is integer passed within [] brackets, and cls is the
  # object class # the [] operator was called on. Any args received by
  # the lambda are proxied to the cls constructor.
  #
  # http://stackoverflow.com/a/12447078
  def __getitem__( cls, n ):
    return lambda *args, **kwargs : [ cls(*args, **kwargs) for x in range(n) ]

  #---------------------------------------------------------------------
  # list
  #---------------------------------------------------------------------
  # Same implementation as __getitem__, but more explicit
  def list( cls, n ):
    return lambda *args, **kwargs : [ cls(*args, **kwargs) for x in range(n) ]

#-----------------------------------------------------------------------
# MetaCollectArgs
#-----------------------------------------------------------------------
# Metaclass which collects and stores the argument names and values used
# in the construction of a class instance.
class MetaCollectArgs( MetaListConstructor ):

  #---------------------------------------------------------------------
  # __call__
  #---------------------------------------------------------------------
  # Called whenever a class instance is created, allowing us to capture
  # all the arguments and argument values passed to the class. These
  # arguments are stored as an OrderedDict in the _args field of the
  # instance so they can be used later.
  def __call__( self, *args, **kwargs ):

    # Get the constructor prototype
    argspec = inspect.getargspec( self.__init__ )

    # Create an argument dictionary
    argdict = collections.OrderedDict()

    # Collect all positional arguments (except first, which is self)
    for i, arg_value in enumerate( args ):
      key, value = argspec.args[i+1], arg_value
      argdict[ key ] = value

    # Collect all keyword arguments
    num_kwargs = len( argspec.args ) - len( args ) - 1
    if argspec.defaults and num_kwargs:
      for i, arg_name in enumerate( argspec.args[-num_kwargs:] ):
        key, value = arg_name, argspec.defaults[ i ]
        if arg_name in kwargs:
          value = kwargs[ arg_name ]
        argdict[ key ] = value

    # Create the instance
    inst = super( MetaCollectArgs, self ).__call__( *args, **kwargs )

    # Add the argdict to inst
    inst._args = argdict

    # Return the instance
    return inst

