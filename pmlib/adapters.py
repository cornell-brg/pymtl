#=========================================================================
# Microprotocol Adapters
#=========================================================================

from pymtl import *
import pmlib

from NormalQueue import NormalQueue
from queues      import SingleElementNormalQueue

from math import ceil, log

# TODO: different get_nbits for indexs vs counts?
def get_nbits( value ):
  return int( ceil( log( value+1, 2 ) ) )

#=========================================================================
# ValRdyToValCredit
#=========================================================================

class ValRdyToValCredit( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  @capture_args
  def __init__( self, msg_sz, max_credits ):

    self.max_credits  = max_credits
    max_credits_nbits = get_nbits( max_credits )

    self.from_msg     = InPort  ( msg_sz )
    self.from_val     = InPort  ( 1 )
    self.from_rdy     = OutPort ( 1 )

    self.to_msg    = OutPort ( msg_sz )
    self.to_val    = OutPort ( 1 )
    self.to_credit = InPort  ( 1 )

    self.credits    = Wire( max_credits_nbits )

  #-----------------------------------------------------------------------
  # Credit Counter Logic
  #-----------------------------------------------------------------------

  @posedge_clk
  def counter( self ):

    if self.reset.value:
      self.credits.next = self.max_credits
    elif self.to_credit.value and not self.to_val.value:
      # Assert if above counter bounds
      assert self.credits.value < self.max_credits
      self.credits.next = self.credits.value + 1
    elif self.to_val.value and not self.to_credit.value:
      # Assert if below counter bounds
      assert self.credits.value > 0
      self.credits.next = self.credits.value - 1
    else:
      self.credits.next = self.credits.value

  #-----------------------------------------------------------------------
  # Output Signals
  #-----------------------------------------------------------------------

  @combinational
  def comb_logic( self ):

    self.to_msg.value   = self.from_msg.value
    self.from_rdy.value = ( self.credits.value > 0 )
    self.to_val.value   = self.from_val.value and self.from_rdy.value

  #-----------------------------------------------------------------------
  # LineTracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( self.from_msg.value,
        self.from_val.value, self.from_rdy.value )

    out_str = \
      pmlib.valrdy.valrdy_to_str( self.to_msg.value,
        self.to_val.value, 1 )

    credit  = self.credits.value

    return "{} () {} - [{}]"\
      .format( in_str, out_str, credit )


#=========================================================================
# ValCreditToValRdy
#=========================================================================

class ValCreditToValRdy( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  @capture_args
  def __init__( self, msg_sz, max_credits ):

    self.entries    = max_credits

    self.from_msg     = InPort  ( msg_sz )
    self.from_val     = InPort  ( 1 )
    self.from_credit  = OutPort ( 1 )

    self.to_msg       = OutPort ( msg_sz )
    self.to_val       = OutPort ( 1 )
    self.to_rdy       = InPort  ( 1 )

    # TODO: make a bypass queue!
    if self.entries == 1:
      self.queue        = SingleElementNormalQueue( msg_sz )
    else:
      self.queue        = NormalQueue( self.entries, msg_sz )

    connect( self.queue.enq_bits, self.from_msg )
    connect( self.queue.enq_val,  self.from_val )

    connect( self.queue.deq_bits, self.to_msg   )
    connect( self.queue.deq_val,  self.to_val   )
    connect( self.queue.deq_rdy,  self.to_rdy   )

  #-----------------------------------------------------------------------
  # Output Signals
  #-----------------------------------------------------------------------

  @combinational
  def comb_logic( self ):

    self.from_credit.value = self.to_val.value and self.to_rdy.value

  #-----------------------------------------------------------------------
  # LineTracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( self.from_msg.value,
        self.from_val.value, 1 )

    full = self.queue.ctrl.full.value

    out_str = \
      pmlib.valrdy.valrdy_to_str( self.to_msg.value,
        self.to_val.value, self.to_rdy.value )

    return "{} - [{}] () {}"\
      .format( in_str, full, out_str )

