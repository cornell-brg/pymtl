#=========================================================================
# TestCacheResp32Sink
#=========================================================================
# Custom Test Sink for the Caches with 32-bit data responses

from   pymtl import *
from   new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle
import new_pmlib

import new_pmlib.valrdy          as     valrdy
from   new_pmlib.TestRandomDelay import TestRandomDelay


class TestCacheResp32Sink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memresp_params, msgs, max_random_delay = 0 ):

    s.mem_params = memresp_params

    #s.in_msg = InPort  ( memresp_params.nbits )
    #s.in_val = InPort  ( 1     )
    #s.in_rdy = OutPort ( 1     )

    s.in_    = InValRdyBundle( memresp_params.nbits )
    s.done   = OutPort ( 1     )

    s.delay  = TestRandomDelay( memresp_params.nbits, max_random_delay )

    s.msgs = msgs
    s.idx  = 0

  def elaborate_logic( s ):

    # Connect the input ports to the delay

    s.connect( s.in_, s.delay.in_ )
    #s.connect( s.in_msg, s.delay.in_msg )
    #s.connect( s.in_val, s.delay.in_val )
    #s.connect( s.in_rdy, s.delay.in_rdy )


    #-----------------------------------------------------------------------
    # Tick
    #-----------------------------------------------------------------------

    @s.posedge_clk
    def tick():

      # Local Constants

      RD = 0
      WR = 1

      # Handle reset

      if s.reset.value:
        s.delay.out.rdy.next = False
        s.done.next          = False
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input message transaction occured

      in_go = s.delay.out.val.value and s.delay.out.rdy.value

      # If the input transaction occured, verify that it is what we
      # expected. then increment the index.

      if in_go:

        # Handle Read Responses

        if s.delay.out.msg[ s.mem_params.type_slice ].value == RD:

          # Reading Word

          if s.delay.out.msg[ s.mem_params.len_slice ].value == 0:
            assert s.delay.out.msg.value == s.msgs[s.idx]

          # Reading Subwords

          else:
            MASK      = Bits( 32 )

            shamt     = \
              s.delay.out.msg[ s.mem_params.len_slice ].value.uint() * 8

            MASK.value = ( 1 << shamt ) - 1

            
            assert ( ( s.delay.out.msg[ s.mem_params.data_slice ].value & MASK )
              == ( s.msgs[s.idx][ s.mem_params.data_slice ] & MASK ) )

        # Handle Write Responses

        elif s.delay.out.msg[ s.mem_params.type_slice ].value == WR:
          pass

        s.idx = s.idx + 1

      # Set the ready and done signals.

      if ( s.idx < len(s.msgs) ):
        s.delay.out.rdy.next = True
        s.done.next          = False
      else:
        s.delay.out.rdy.next = False
        s.done.next          = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.in_.msg.value,
        s.in_.val.value, s.in_.rdy.value )

    return "{} ({:2})" \
      .format( in_str, s.idx )


