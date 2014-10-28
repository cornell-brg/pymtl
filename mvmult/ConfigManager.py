#==============================================================================
# ConfigManager
#==============================================================================

from pymtl import *
from new_pmlib import InValRdyBundle, Decoder

STATE_IDLE = 0
STATE_CFG  = 1
STATE_CALC = 2

y = Bits( 1, 1 )
n = Bits( 1, 0 )

class ConfigManager( Model ):
  def __init__( s, addr_nbits, data_nbits, decoder_in_sz, decoder_out_sz ):

    # Input from Proc2ASLA
    s.proc2asla     = InValRdyBundle( addr_nbits + data_nbits )

    # ConfigManager <- ASLA Kernel
    s.is_asla_done  = InPort ( 1 )

    # ConfigManager -> ASLA Kernel
    s.cfg_data      = OutPort( data_nbits )
    s.asla_go       = OutPort( 1 )

    # Write enables for operator cfg registers
    s.cfg_reg_wen   = OutPort( decoder_out_sz )

    # Config fields
    s.addr_nbits     = addr_nbits
    s.data_nbits     = data_nbits
    s.decoder_in_sz  = addr_nbits
    s.decoder_out_sz = data_nbits

  def elaborate_logic( s ):

    s.state      = Wire( 2 )
    s.state_next = Wire( 2 )

    #--------------------------------------------------------------------------
    # state_update
    #--------------------------------------------------------------------------
    @s.posedge_clk
    def state_update():
      if s.reset: s.state.next = STATE_IDLE
      else:       s.state.next = s.state_next

    #--------------------------------------------------------------------------
    # state_transition
    #--------------------------------------------------------------------------

    s.cfg_addr = Wire( s.addr_nbits )

    @s.combinational
    def state_transition():

      s.cfg_addr      = s.proc2asla.msg[s.data_nbits:s.data_nbits+s.addr_nbits]

      is_asla_cfg_go  = s.proc2asla.val and s.proc2asla.rdy
      is_asla_calc_go = is_asla_cfg_go  and (s.cfg_addr == 0)

      s.state_next.value = s.state

      if   s.state == STATE_IDLE and     is_asla_calc_go:
        s.state_next.value = STATE_CALC
      elif s.state == STATE_IDLE and     is_asla_cfg_go:
        s.state_next.value = STATE_CFG

      elif s.state == STATE_CFG  and     is_asla_calc_go:
        s.state_next.value = STATE_CALC
      elif s.state == STATE_CFG  and     is_asla_cfg_go:
        s.state_next.value = STATE_CFG
      elif s.state == STATE_CFG  and not is_asla_cfg_go:
        s.state_next.value = STATE_IDLE

      elif s.state == STATE_CALC:
        if   s.is_asla_done and is_asla_calc_go and s.proc2asla.val:
          s.state_next.value = STATE_CALC
        elif s.is_asla_done and not s.proc2asla.val:
          s.state_next.value = STATE_IDLE
        elif s.is_asla_done and     s.proc2asla.val:
          s.state_next.value = STATE_CFG

    #--------------------------------------------------------------------------
    # decoder
    #--------------------------------------------------------------------------

    s.decoder = Decoder( s.decoder_in_sz, s.decoder_out_sz )
    s.connect( s.decoder.in_, s.proc2asla.msg[s.data_nbits:
                                              s.data_nbits+s.addr_nbits] )

    #--------------------------------------------------------------------------
    # output_signals
    #--------------------------------------------------------------------------

    s.connect( s.cfg_data, s.proc2asla.msg[0:s.data_nbits] )

    # TODO: make temporary
    s.cs = Wire( 3 )

    @s.combinational
    def output_signals():

      if   s.state == STATE_IDLE: s.cs.value = concat( y, y, n )
      elif s.state == STATE_CFG:  s.cs.value = concat( y, y, n )
      elif s.state == STATE_CALC: s.cs.value = concat( n, n, y )

      s.proc2asla.rdy.value = s.cs[2]
      decoder_en            = s.cs[1] and s.proc2asla.val
      s.asla_go.value       = s.cs[0]

      s.cfg_data.value    = s.proc2asla.msg[0:s.data_nbits]
      s.cfg_reg_wen.value = s.decoder.out if decoder_en == 1 else 0

  def line_trace( s ):
    return 'p2asla: {} done: {} () data: {} go: {} wen: {} state: {}'.format(
        s.proc2asla, s.is_asla_done, s.cfg_data, s.asla_go, s.cfg_reg_wen, s.state )

