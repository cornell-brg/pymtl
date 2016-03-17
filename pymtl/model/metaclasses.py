#=========================================================================
# metaclasses.py
#=========================================================================
"""Collection of metaclasses to implement python magic."""

import inspect
import collections

#-----------------------------------------------------------------------
# MetaListConstructor
#-----------------------------------------------------------------------
class MetaListConstructor( type ):
  """Metaclass implementing syntactic sugar for creating a list of
  identical objects.

  Classes inheriting from this metaclass can use the following
  shorthand:

  >>> var = MyObject[ 4 ]( arg1, arg2, arg3 )

  The above produces the same result as the following list
  comprehension:

  >>> var = [ MyModel( arg1, arg2, arg3 ) for x in range( nitems ) ]

  An alternative, more explicit syntax is also provided using the list()
  class method:

  >>> var = MyObject.list( 4 )( arg1, arg2, arg3 )
  """

  #---------------------------------------------------------------------
  # __getitem__
  #---------------------------------------------------------------------
  def __getitem__( cls, n ):
    """Class method which returns a lambda-wrapped list comprehension.

    When called, the lambda generates a list containing n instances of
    type cls, where n is integer passed within [] brackets, and cls is
    the object class # the [] operator was called on. Any args received
    by the lambda are proxied to the cls constructor.

    http://stackoverflow.com/a/12447078
    """

    return lambda *args, **kwargs : [ cls(*args, **kwargs) for x in range(n) ]

  #---------------------------------------------------------------------
  # list
  #---------------------------------------------------------------------
  def list( cls, n ):
    """Class method which returns a lambda-wrapped list comprehension.

    Same implementation as __getitem__, but more explicit syntax.
    """

    return lambda *args, **kwargs : [ cls(*args, **kwargs) for x in range(n) ]

#-----------------------------------------------------------------------
# MetaCollectArgs
#-----------------------------------------------------------------------
class MetaCollectArgs( MetaListConstructor ):
  """Metaclass which collects and stores the argument names and values
  used in the construction of a class instance.

  This metaclass subclasses MetaListConstructor so we can chain together
  Metaclass functionality.
  """

  #---------------------------------------------------------------------
  # __call__
  #---------------------------------------------------------------------
  def __call__( self, *args, **kwargs ):
    """Called whenever a class instance is created, allowing us to
    capture all the arguments and argument values passed to the class.
    These arguments are stored as an OrderedDict in the _args field of
    the instance so they can be used later.
    """

    # Get the constructor prototype

    argspec = inspect.getargspec( self.__init__ )

    # Create an argument dictionary

    argdict = collections.OrderedDict()

    # Collect all positional arguments (except first, which is self)

    for i, arg_value in enumerate( args ):
      key, value = argspec.args[i+1], arg_value
      argdict[ key ] = value

    # Collect all keyword arguments

    for key, value in kwargs.items():
      argdict[ key ] = value

    # Handle default arguments. Iterate backwards through default values,
    # matching the default value to the corresponding argument name, then
    # add the corresponding argument as long as we did not already add it
    # above.

    if argspec.defaults:
      for i, default_value in enumerate( reversed(argspec.defaults) ):
        arg_name = argspec.args[ len(argspec.args) - i - 1 ]
        if arg_name not in argdict:
          argdict[ arg_name ] = default_value

    # Create the instance

    inst = super( MetaCollectArgs, self ).__call__( *args, **kwargs )

    # Add the argdict to inst

    inst._args = argdict

    # Return the instance

    return inst

