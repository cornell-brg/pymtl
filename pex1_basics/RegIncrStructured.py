import sys
sys.path.append('..')
from pymtl import *

from Register import *
from Incrementer import *

class RegIncrStructured( Model ):

  def __init__( self, bits ):
    self.in_  = InPort( bits )
    self.out  = OutPort( bits )
    self.reg  = Incrementer( bits )
    self.incr = Register( bits )

    connect( self.in_      , self.reg.in_  )
    connect( self.reg.out  , self.incr.in_ )
    connect( self.incr.out , self.out      )
