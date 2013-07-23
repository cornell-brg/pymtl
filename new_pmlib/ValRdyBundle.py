#=========================================================================
# ValRdyBundle.py
#=========================================================================
# Defines a PortBundle for the ValRdy interface.

from new_pymtl import *
from valrdy    import valrdy_to_str

#-------------------------------------------------------------------------
# ValRdyBundle
#-------------------------------------------------------------------------
# Definition for the ValRdy PortBundle.
class ValRdyBundle( PortBundle ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  # Interface for the ValRdy PortBundle.
  def __init__( self, nbits ):
    self.msg = InPort ( nbits )
    self.val = InPort ( 1 )
    self.rdy = OutPort( 1 )

  #-----------------------------------------------------------------------
  # to_str
  #-----------------------------------------------------------------------
  def to_str( self, msg=None ):
    msg = self.msg if None else msg
    return valrdy_to_str( msg, self.val, self.rdy )

  #-----------------------------------------------------------------------
  # __str__
  #-----------------------------------------------------------------------
  def __str__( self ):
    return valrdy_to_str( self.msg, self.val, self.rdy )

#-------------------------------------------------------------------------
# Create InValRdyBundle and OutValRdyBundle
#-------------------------------------------------------------------------
InValRdyBundle, OutValRdyBundle = create_PortBundles( ValRdyBundle )
