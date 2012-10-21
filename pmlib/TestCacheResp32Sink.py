#=========================================================================
# TestCacheResp32Sink
#=========================================================================
# Custom Test Sink for the Caches with 32-bit data responses

from   pymtl import *
import pmlib

import pmlib.valrdy          as     valrdy
from   pmlib.TestRandomDelay import TestRandomDelay


class TestCacheResp32Sink (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, memresp_params, msgs, max_random_delay = 0 ):

    self.mem_params = memresp_params

    self.in_msg = InPort  ( memresp_params.nbits )
    self.in_val = InPort  ( 1     )
    self.in_rdy = OutPort ( 1     )
    self.done   = OutPort ( 1     )

    self.delay  = TestRandomDelay( memresp_params.nbits, max_random_delay )

    # Connect the input ports to the delay

    connect( self.in_msg, self.delay.in_msg )
    connect( self.in_val, self.delay.in_val )
    connect( self.in_rdy, self.delay.in_rdy )

    self.msgs = msgs
    self.idx  = 0

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # Local Constants

    RD = 0
    WR = 1

    # Handle reset

    if self.reset.value:
      self.delay.out_rdy.next = False
      self.done.next          = False
      return

    # At the end of the cycle, we AND together the val/rdy bits to
    # determine if the input message transaction occured

    in_go = self.delay.out_val.value and self.delay.out_rdy.value

    # If the input transaction occured, verify that it is what we
    # expected. then increment the index.

    if in_go:

      # Handle Read Responses

      if self.delay.out_msg[ self.mem_params.type_slice ].value == RD:

        # Reading Word

        if self.delay.out_msg[ self.mem_params.len_slice ].value == 0:
          assert self.delay.out_msg.value == self.msgs[self.idx]

        # Reading Subwords

        else:
          MASK      = Bits( 32 )

          shamt     = \
            self.delay.out_msg[ self.mem_params.len_slice ].value.uint * 8

          MASK.uint = ( 1 << shamt ) - 1

          sub_word  = slice( self.mem_params.data_slice.start,
            self.delay.out_msg[ self.mem_params.len_slice ].value.uint * 8 )

          assert ( ( self.delay.out_msg[ self.mem_params.data_slice ].value & MASK )
            == ( self.msgs[self.idx][ self.mem_params.data_slice ] & MASK ) )

      # Handle Write Responses

      elif self.delay.out_msg[ self.mem_params.len_slice ].value == WR:
        pass

      self.idx = self.idx + 1

    # Set the ready and done signals.

    if ( self.idx < len(self.msgs) ):
      self.delay.out_rdy.next = True
      self.done.next          = False
    else:
      self.delay.out_rdy.next = False
      self.done.next          = True

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      valrdy.valrdy_to_str( self.in_msg.value,
        self.in_val.value, self.in_rdy.value )

    return "{} ({:2})" \
      .format( in_str, self.idx )


