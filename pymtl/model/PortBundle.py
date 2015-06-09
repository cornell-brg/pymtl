#=======================================================================
# PortBundle
#=======================================================================
# This module defines a base class and utility function for creating
# user defined port bundles.  A user first defines a template class
# which # subclasses PortBundle, and then passes this template class
# into the # create_PortBundles() utility function.
# create_PortBundles() will return two new classes that implement the
# two halves (Left and Right) of the bundle interface.
#
#   def MyBundle( PortBundle ):
#     def __init__( dtype ):
#       self.data = InPort ( dtype )
#       self.rdy  = OutPort( 1 )
#
#   InMyBundle, OutMyBundle = create_PortBundles( MyBundle )
#
# Some metaclass magic is used to make this work. create_PortBundles
# uses the built-in type() method provided by the Python language
# to create the Left/Right bundle subclasses, additionally adding a
# "flip" class attribute, which is False for left and True for right.
#
# The Left/Right classes are subclasses of the user defined port bundle,
# which in turn should subclass PortBundle, whose __metaclass__ is set
# to be MetaPortBundle. Whenever an instance of the left or right
# port bundle object is created, not only is the __init__ function of
# the PortBundle called (creating the Ports of the bundle), but also
# the __call__ function of MetaPortBundle.  __call__ inspects the
# "flip" class attribute, and then sets the direction of the bundles
# ports based on the value of "flip".

from metaclasses import MetaListConstructor
from signals     import InPort, OutPort

#-----------------------------------------------------------------------
# MetaPortBundle
#-----------------------------------------------------------------------
# Metaclass that customizes PortBundle subclass creation
class MetaPortBundle( MetaListConstructor ):

  def __call__( self, *args, **kwargs ):

    # Create the instance
    inst = super( MetaPortBundle, self ).__call__( *args, **kwargs )

    # Set direction of ports
    if self.flip: inst._reverse()

    # Collect all the ports into a list
    ports = []
    for port_name, port in inst.__dict__.items():
      port.name = port_name
      ports.append( port )
    inst._ports = sorted( ports, key=lambda x: x.name )

    # Return the instance
    return inst

#-----------------------------------------------------------------------
# PortBundle
#-----------------------------------------------------------------------
# Base class for user defined port bundles.  These port bundles should
# create a definition class which subclasses PortBundle, and then pass
# the defination class into create_PortBundles to create the input and
# output versions of the bundle.
class PortBundle( object ):
  __metaclass__ = MetaPortBundle

  #---------------------------------------------------------------------
  # _reverse
  #---------------------------------------------------------------------
  # Reverse Bundle Direction
  def _reverse( self ):

    for var_name, var_obj in self.__dict__.items():

      if   isinstance( var_obj, InPort ):
        self.__dict__[var_name] = OutPort ( var_obj.dtype )
      elif isinstance( var_obj, OutPort ):
        self.__dict__[var_name] = InPort  ( var_obj.dtype )

    return self

  #---------------------------------------------------------------------
  # get_ports
  #---------------------------------------------------------------------
  # Get list of ports in PortBundle.
  def get_ports( self ):
    return self._ports

#-----------------------------------------------------------------------
# create_PortBundles
#-----------------------------------------------------------------------
# Utility function that takes a user defined PortBundle class and
# generates the Left and Right (flipped and unflipped) versions of the
# class.

def create_PortBundles( bundle_def ):
  name = bundle_def.__name__
  a = type( '_Left'+name,  (bundle_def,), {'flip':False})
  b = type( '_Right'+name, (bundle_def,), {'flip':True} )
  return a, b


