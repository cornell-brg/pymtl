#=========================================================================
# ValRdy PortBundle
#=========================================================================
# Defines a port bundle for the ValRdy interface.

from pymtl import *

#-------------------------------------------------------------------------
# ValRdy PortBundle Template
#-------------------------------------------------------------------------

class ValRdyBundle( PortBundle ):

  #-----------------------------------------------------------------------
  # PortBundle interface
  #-----------------------------------------------------------------------

  def __init__( self, nbits ):
    self.msg = InPort ( nbits )
    self.val = InPort ( 1 )
    self.rdy = OutPort( 1 )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( self ):
    return valrdy_to_str( self.msg.value, self.val.value, self.rdy.value)

#-------------------------------------------------------------------------
# Create InValRdyBundle and OutValRdyBundle
#-------------------------------------------------------------------------

InValRdyBundle, OutValRdyBundle = create_PortBundles( ValRdyBundle )

#-------------------------------------------------------------------------
# Utility linetracing function
#-------------------------------------------------------------------------

def valrdy_to_str( msg, val, rdy ):

  str = "{}".format( msg )
  num_chars = len(str)

  if val and not rdy:
    str = "#".ljust(num_chars)
  elif not val and rdy:
    str = " ".ljust(num_chars)
  elif not val and not rdy:
    str = ".".ljust(num_chars)

  return str

