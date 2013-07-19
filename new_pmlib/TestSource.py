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

class TestSource( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs, max_random_delay = 0 ):

    s.out_msg = OutPort ( nbits )
    s.out_val = OutPort ( 1     )
    s.out_rdy = InPort  ( 1     )
    s.done    = OutPort ( 1     )

    s.src   = TestSimpleSource( nbits, msgs )
    s.delay = TestRandomDelay( nbits, max_random_delay )

  def elaborate_logic( s ):

    # Connect test source to random delay

    s.connect( s.src.out_msg, s.delay.in_msg )
    s.connect( s.src.out_val, s.delay.in_val )
    s.connect( s.src.out_rdy, s.delay.in_rdy )

    # Connect random delay to output ports

    s.connect( s.delay.out_msg, s.out_msg )
    s.connect( s.delay.out_val, s.out_val )
    s.connect( s.delay.out_rdy, s.out_rdy )

    # Connect test source done signal to output port

    s.connect( s.src.done, s.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    out_str = valrdy.valrdy_to_str( s.out_msg, s.out_val, s.out_rdy )

    return "{}".format( out_str )

