#=========================================================================
# ValRdyBundle.py
#=========================================================================
# Defines a PortBundle for the ValRdy interface.

from pymtl import *
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
    self.req  = msgtype.req
    self.resp = msgtype.resp

    self.req_msg = InPort ( msgtype.req )
    self.req_val = InPort ( 1 )
    self.req_rdy = OutPort( 1 )

    self.resp_msg = InPort ( msgtype.resp )
    self.resp_val = InPort ( 1 )
    self.resp_rdy = OutPort( 1 )

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
