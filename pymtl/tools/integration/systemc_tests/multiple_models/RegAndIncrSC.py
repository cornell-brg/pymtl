#=======================================================================
# RegAndIncrSC.py
#=======================================================================

from pymtl import *

class RegAndIncrSC( Model ):
  
  def __init__( s ):

    s.in_ = InPort ( Bits(32) )
    s.out = OutPort( Bits(32) )
    
    s.reg  = RegSC()
    s.incr = IncrSC()
    
    s.connect( s.in_     , s.reg.in_ )
    s.connect( s.reg.out , s.incr.in_ )
    s.connect( s.incr.out, s.out )
  
  def line_trace( s ):
    return "[ " + s.reg.line_trace() + " | " + s.incr.line_trace()
  
  def destroy( s ):
    s.reg.destroy()
    s.incr.destroy()

class RegSC( SystemCModel ):
  
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


class IncrSC( SystemCModel ):
  
  sclinetrace = True
  
  def __init__( s ):

    s.in_ = InPort ( Bits(32) )
    s.out = OutPort( Bits(32) )
    
    s.set_ports({
      "in_" : s.in_,
      "out" : s.out,
    })
