#=======================================================================
# RegIncrSC.py
#=======================================================================

from pymtl import *

class RegIncrSC( SystemCModel ):
  
  sclinetrace = True
  
  def __init__( s ):

    s.in_ = InPort ( Bits(32) )
    s.out = OutPort( Bits(32) )
    
    s.set_ports({
      "clk" : s.clk,
      "rst" : s.reset,
      "in_" : s.in_,
      "out" : s.out,
    })

