#=========================================================================
# ValueNode
#=========================================================================
# Base class for value types, provides hooks used by SimulationTool.
# Any value that can be passed as a parameter to a Signal object
# (InPort, OutPort, Wire), needs to subclass ValueNode.
class ValueNode( object ):

  #-----------------------------------------------------------------------
  # Write v property
  #-----------------------------------------------------------------------
  @property
  def v( self ):
    return self

  @v.setter
  def v( self, value ):
    self.notify_sim()
    self.write( value )

  #-----------------------------------------------------------------------
  # TEMPORARY: Backwards compatibility
  #-----------------------------------------------------------------------
  @property
  def value( self ):
    return self

  #-----------------------------------------------------------------------
  # TEMPORARY: Backwards compatibility
  #-----------------------------------------------------------------------
  @value.setter
  def value( self, value ):
    self.notify_sim()
    self.write( value )

  #-----------------------------------------------------------------------
  # Write (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def write( self, value ):
    raise NotImplementedError( "Subclasses of ValueNode must "
                               "implement the write() method!" )

  #-----------------------------------------------------------------------
  # Notify Sim Hook (Abstract)
  #-----------------------------------------------------------------------
  # Another abstract method used as a hook by simulators tools.
  # Not meant to be implemented by subclasses.
  # NOTE: This approach uses closures, other methods can be found in:
  #       http://brg.csl.cornell.edu/wiki/lockhart-2013-03-18
  #       Is this the fastest approach?
  def notify_sim( self ):
    pass

