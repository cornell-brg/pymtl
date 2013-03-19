# TODO: use abc module to create "update()" abstract method?

class ValueNode( object ):

  @property
  def v( self ):
    return self

  @v.setter
  def v( self, value ):
    self.write( value )

  def write( self, value ):
    raise NotImplementedError( "Subclasses of ValueNode must "
                               "implement the write() method!" )
