#==============================================================================
# LaneManager.py
#==============================================================================

from pymtl        import *
from pclib.ifcs import InValRdyBundle

STATE_CFG  = 0
STATE_CALC = 1
STATE_DONE = 2

class LaneManager( Model ):

  def __init__( s, nlanes, addr_nbits=5, data_nbits=32 ):

    # CPU <-> LaneManager
    s.from_cpu    = InValRdyBundle( addr_nbits + data_nbits )
    s.to_cpu      = OutPort       ( 1 )

    # LaneManager -> Lanes
    s.size    = OutPort( data_nbits )
    s.r_baddr = OutPort( data_nbits )
    s.v_baddr = OutPort( data_nbits )
    s.d_baddr = OutPort( data_nbits )
    s.go      = OutPort( 1 )
    s.done    = [ InPort ( 1 ) for x in range( nlanes ) ]

    # Config fields
    s.nlanes         = nlanes
    s.addr_nbits     = addr_nbits
    s.data_nbits     = data_nbits

  def elaborate_logic( s ):

    #--------------------------------------------------------------------------
    # state_update
    #--------------------------------------------------------------------------
    s.state      = Wire( 2 )
    s.state_next = Wire( 2 )
    @s.posedge_clk
    def state_update():

      if s.reset: s.state.next = STATE_CFG
      else:       s.state.next = s.state_next

    #--------------------------------------------------------------------------
    # config_update
    #--------------------------------------------------------------------------
    s.addr = Wire( s.addr_nbits )
    s.data = Wire( s.data_nbits )

    # TODO: replace this with temporaries (issue #78 + #79)
    # TODO: make open slices translatable (issue #80)
    @s.combinational
    def temp():
      s.addr.value = s.from_cpu.msg[s.data_nbits:s.from_cpu.msg.nbits]
      s.data.value = s.from_cpu.msg[0:s.data_nbits]

    s.done_reg = Wire( s.nlanes )

    @s.posedge_clk
    def config_update():

      if s.reset:
        s.go      .next = 0
        s.size    .next = 0
        s.r_baddr .next = 0
        s.v_baddr .next = 0
        s.d_baddr .next = 0
        s.done_reg.next = 0

      elif s.from_cpu.val and s.from_cpu.rdy:
        if s.addr == 0: s.go     .next = s.data[0]
        if s.addr == 1: s.size   .next = s.data
        if s.addr == 2: s.r_baddr.next = s.data
        if s.addr == 3: s.v_baddr.next = s.data
        if s.addr == 4: s.d_baddr.next = s.data
        s.done_reg.next = 0

      elif s.state_next == STATE_CALC:

        # Check each lane for completion.
        for i in range( s.nlanes ):
          if s.done[i]: s.done_reg[i].next = 1

        # Lanes make take different amounts of time, and may transition to IDLE
        # before the LaneManager transitions to DONE. We need to set go low
        # before reaching STATE_DONE, so we do it as soon as we transition to
        # STATE_CALC; this ensures go is only high for 1 cycle.

        s.go.next = 0

    #--------------------------------------------------------------------------
    # state_transition
    #--------------------------------------------------------------------------
    @s.combinational
    def state_transition():

      # Status

      do_config     = s.from_cpu.val and s.from_cpu.rdy
      start_compute = s.addr == 0 and s.data == 1
      is_done       = reduce_and( s.done_reg )

      # State update

      s.state_next.value = s.state

      if   s.state == STATE_CFG and do_config and start_compute:
        s.state_next.value = STATE_CALC

      elif s.state == STATE_CALC and is_done:
        s.state_next.value = STATE_DONE

      elif s.state == STATE_DONE:
        s.state_next.value = STATE_CFG

      # Output rdy and to_cpu

      s.from_cpu.rdy.value = s.state == STATE_CFG
      s.to_cpu      .value = s.state == STATE_DONE

  def line_trace( s ):
    return '{cfg_msg} {state:4} {go:2} {done_reg} {done:4}'.format(
              cfg_msg  = s.from_cpu,
              state    = ['CFG','CALC','DONE'][s.state],
              go       = 'go'   if s.go     else '',
              done     = 'done' if s.to_cpu else '',
              done_reg = '{:0{width}b}'.format(
                            concat( *s.done ).uint(),
                            width = len( s.done )
                          )
           )

