#=========================================================================
# RegIncrStruct
#=========================================================================

from pymtl import *

from Register    import Register
from Incrementer import Incrementer

# from pmlib import arith
# from pmlib import regs

class RegIncrStruct( Model ):

  def __init__( self ):
    self.in_  = InPort( 16 )
    self.out  = OutPort( 16 )

    # Register

    self.reg = Register( 16 )
    # self.reg = regs.Reg( 16 )
    connect( self.in_, self.reg.in_ )

    # Incrementer

    self.incr = Incrementer( 16 )
    # self.incr = arith.Inc( 16 )
    connect( self.reg.out,  self.incr.in_ )
    connect( self.incr.out, self.out      )

