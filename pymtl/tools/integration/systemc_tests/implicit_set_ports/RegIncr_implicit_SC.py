#=======================================================================
# RegIncr_implicit_SC.py
#=======================================================================

from pymtl import *

class RegIncr_implicit_SC( SystemCModel ):
  
  def __init__( s ):

    s.in_ = InPort ( Bits(32) )
    s.out = OutPort( Bits(32) )
  
  # When the port names in SystemC module matches the defined ports 
  # above, plus "clk" and "reset", we don't need to set_ports.
