#=========================================================================
# Port Bundle
#=========================================================================

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
      inst.__reverse__()
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

  def __reverse__( self ):

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
  a = type( 'Left'+name,  (bundle_def,), {'flip':False})
  b = type( 'Right'+name, (bundle_def,), {'flip':True} )
  return a, b


