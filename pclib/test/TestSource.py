#=========================================================================
# TestSource.py
#=========================================================================

from pymtl        import *
from pclib.test   import TestRandomDelay
from pclib.ifcs import OutValRdyBundle

from TestSimpleSource import TestSimpleSource

#-------------------------------------------------------------------------
# Constructor
#-------------------------------------------------------------------------
class TestSource( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nbits, msgs, max_random_delay = 0 ):

    s.out  = OutValRdyBundle( nbits )
    s.done = OutPort        ( 1     )

    s.nbits            = nbits
    s.msgs             = msgs
    s.max_random_delay = max_random_delay

  def elaborate_logic( s ):

    # Instantiate modules

    s.src   = TestSimpleSource( s.nbits, s.msgs )
    s.delay = TestRandomDelay ( s.nbits, s.max_random_delay )

    # Connect test source -> random delay -> output ports

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.out       )

    # Connect test source done signal to output port

    s.connect( s.src.done, s.done )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    return "{}".format( s.out )

