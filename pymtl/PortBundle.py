#=========================================================================
# PortBundle
#=========================================================================
# This module defines a base class and utility function for creating user
# defined port bundles.  A user first defines a template class which
# subclasses PortBundle, and then passes this template class into the
# create_PortBundles() utility function.  create_PortBundles()
# will return two new classes that implement the two halves (Left and
# Right) of the bundle interface.
#
#   def MyBundle( PortBundle ):
#     def __init__( nbits ):
#       self.data = InPort ( nbits )
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


# TODO: circular import with model/PortBundle... how to fix this?
import model

#-------------------------------------------------------------------------
# MetaPortBundle
#-------------------------------------------------------------------------
# Metaclass that customizes PortBundle subclass creation

class MetaPortBundle( type ):

  def __call__( self, *args, **kwargs ):

    inst = super(MetaPortBundle, self).__call__(*args, **kwargs)
    if self.flip:
      inst._reverse()
    return inst

#-------------------------------------------------------------------------
# PortBundle
#-------------------------------------------------------------------------
# Base class for user defined port bundles.  These port bundles should
# create a definition class which subclasses PortBundle, and then pass
# the defination class into create_PortBundles to create the input and
# output versions of the bundle.

class PortBundle( object ):
  __metaclass__ = MetaPortBundle

  #-----------------------------------------------------------------------
  # Reverse Bundle Direction
  #-----------------------------------------------------------------------

  def _reverse( self ):

    for var_name, var_obj in self.__dict__.items():

      if   isinstance( var_obj, model.InPort ):
        self.__dict__[var_name] = model.OutPort ( var_obj.width )
      elif isinstance( var_obj, model.OutPort ):
        self.__dict__[var_name] = model.InPort  ( var_obj.width )

    return self

  #-----------------------------------------------------------------------
  # Connect Bundles
  #-----------------------------------------------------------------------

  def connect( self, target ):

    assert isinstance( target, PortBundle )

    for var_name, var_obj in self.__dict__.items():
      target_obj = target.__dict__[ var_name ]
      var_obj.connect( target_obj )


#-------------------------------------------------------------------------
# create_PortBundles
#-------------------------------------------------------------------------
# Utility function that takes a user defined PortBundle class and
# generates the Left and Right (flipped and unflipped) versions of the
# class.

def create_PortBundles( bundle_def ):
  name = bundle_def.__name__
  a = type( '_Left'+name,  (bundle_def,), {'flip':False})
  b = type( '_Right'+name, (bundle_def,), {'flip':True} )
  return a, b


