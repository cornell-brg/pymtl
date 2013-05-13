#=========================================================================
# TestSource
#=========================================================================
# This class will output messages on a val/rdy interface from a
# predefined list. Includes support for random delays.
#

from new_pymtl import *
import valrdy

from TestSimpleSource import TestSimpleSource
from TestRandomDelay  import TestRandomDelay

class TestSource (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, msgs, max_random_delay = 0 ):

    self.out_msg = OutPort ( nbits )
    self.out_val = OutPort ( 1     )
    self.out_rdy = InPort  ( 1     )
    self.done    = OutPort ( 1     )

    self.src   = TestSimpleSource( nbits, msgs )
    self.delay = TestRandomDelay( nbits, max_random_delay )

  def elaborate_logic( self ):

    # Connect test source to random delay

    self.connect( self.src.out_msg, self.delay.in_msg )
    self.connect( self.src.out_val, self.delay.in_val )
    self.connect( self.src.out_rdy, self.delay.in_rdy )

    # Connect random delay to output ports

    self.connect( self.delay.out_msg, self.out_msg )
    self.connect( self.delay.out_val, self.out_val )
    self.connect( self.delay.out_rdy, self.out_rdy )

    # Connect test source done signal to output port

    self.connect( self.src.done, self.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    out_str = \
      valrdy.valrdy_to_str( self.out_msg.value,
        self.out_val.value, self.out_rdy.value )

    return "{}".format( out_str )

