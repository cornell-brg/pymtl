#==============================================================================
# DummyCOP.py
#==============================================================================

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle, mem_msgs

STATE_CFG  = 0
STATE_CALC = 1
STATE_DONE = 2

class DummyCOPCL( Model ):

  def __init__( s ):
    s.from_cpu = InValRdyBundle( 5 + 32 )
    s.to_cpu   = OutPort( 1 )
    s.result   = OutPort( 32 )

  def elaborate_logic( s ):

    s.regs  = [Bits(32,0)]*4
    s.state = STATE_CFG

    @s.tick
    def seq_logic():

      addr = s.from_cpu.msg[32:37]
      data = s.from_cpu.msg[ 0:32]

      # State transitions

      if   s.state == STATE_CFG:
        if s.from_cpu.val and s.from_cpu.rdy:
          s.regs[ addr ] = data
        s.state = STATE_CALC if s.regs[0] == 1 else STATE_CFG

      elif s.state == STATE_CALC:
        s.regs[3] = s.regs[1] + s.regs[2]
        s.state = STATE_DONE

      elif s.state == STATE_DONE:
        s.regs[0] = 0
        s.state = STATE_CFG

      # Output Signals

      s.from_cpu.rdy.value = s.state == STATE_CFG
      s.to_cpu      .value = s.state == STATE_DONE
      s.result      .value = s.regs[3]

  def line_trace( s ):
    return '{} ( {}+{}={} ) {}'\
        .format( s.from_cpu, s.regs[1], s.regs[2], s.regs[3], s.to_cpu )

