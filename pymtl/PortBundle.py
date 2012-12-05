#=========================================================================
# Port Bundle
#=========================================================================

# TODO: circular import with model/PortBundle... how to fix this?
import model

class PortBundle( object ):

  #-----------------------------------------------------------------------
  # Port
  #-----------------------------------------------------------------------

  def __init__( self ):
    pass

  #-----------------------------------------------------------------------
  # Reverse Bundle Direction
  #-----------------------------------------------------------------------

  def reverse( self ):

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

