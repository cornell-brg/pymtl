#=========================================================================
# RegIncrStructured
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

from Register import *
from Incrementer import *

class RegIncrStructured( Model ):

  def __init__( self, bits ):
    self.in_  = InPort( bits )
    self.out  = OutPort( bits )

    # Register

    self.reg = Register( bits )
    connect( self.in_,      self.reg.in_  )

    # Incrementer

    self.incr = Incrementer( bits )
    connect( self.reg.out,  self.incr.in_ )
    connect( self.incr.out, self.out      )

