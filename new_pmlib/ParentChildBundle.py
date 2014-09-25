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
class ParentChildBundle( PortBundle ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  # Interface for the ValRdy PortBundle.
  def __init__( self, msgtype ):
    self.p2c_msg = InPort ( msgtype.req )
    self.p2c_val = InPort ( 1 )
    self.p2c_rdy = OutPort( 1 )

    self.c2p_msg = InPort ( msgtype.resp )
    self.c2p_val = InPort ( 1 )
    self.c2p_rdy = OutPort( 1 )

  #-----------------------------------------------------------------------
  # to_str
  #-----------------------------------------------------------------------
  def to_str( self, msg=None ):
    return "TODO"

  #-----------------------------------------------------------------------
  # __str__
  #-----------------------------------------------------------------------
  def __str__( self ):
    return "TODO"

#-------------------------------------------------------------------------
# Create InValRdyBundle and OutValRdyBundle
#-------------------------------------------------------------------------
ParentReqRespBundle, ChildReqRespBundle = create_PortBundles( ParentChildBundle )
