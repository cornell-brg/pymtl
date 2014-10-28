#=======================================================================
# signal_lists.py
#=======================================================================

class PortList( list ):
  def get_ports( self ):
    return self
  def __hash__( self ):
    return hash( tuple(self) )

class WireList( list ):
  def get_wires( self ):
    return self
  def __hash__( self ):
    return hash( tuple(self) )
