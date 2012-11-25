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




#-------------------------------------------------------------------------
# Temporary Example 1
#-------------------------------------------------------------------------

#x = ValRdyBundle( 4, 'in' )
#print x.msg
#y = ValRdyBundle( 4, 'out' )
#print y.msg
#
#connect( x, y )
#print x.msg.connections
#print x.val.connections
#print x.rdy.connections
#print y.msg.connections
#print y.val.connections
#print y.rdy.connections
#
#x = ValRdyBundle( 4 )
#print x.msg
#y = ValRdyBundle( 4 ).reverse()
#print y.msg
#
#connect( x, y )
#print x.msg.connections
#print x.val.connections
#print x.rdy.connections
#print y.msg.connections
#print y.val.connections
#print y.rdy.connections
