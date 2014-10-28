#=======================================================================
# IntMulPipelined.py
#=======================================================================

from pymtl  import *
from new_pmlib  import InValRdyBundle, OutValRdyBundle
from muldiv_msg import BitStructIndex

#-----------------------------------------------------------------------
# IntMulPipelined
#-----------------------------------------------------------------------
class IntMulPipelined( Model ):

  idx = BitStructIndex()

  def __init__( s, nstages=4 ):

    s.in_  = InValRdyBundle ( s.idx.length )
    s.out  = OutValRdyBundle( 32 )

    s.nstages = nstages

  def elaborate_logic( s ):

    # Datapath

    s.mul_unit = Multiplier( 32, s.nstages )

    s.connect( s.in_.msg[s.idx.arg_A], s.mul_unit.a )
    s.connect( s.in_.msg[s.idx.arg_B], s.mul_unit.b )

    s.not_stall = Wire( 1 )
    s.valids    = Wire[ s.nstages ]( 1 )

    for i in range( s.nstages ):
      s.connect( s.not_stall, s.mul_unit.enables[i] )

    s.connect( s.mul_unit.product, s.out.msg )
    s.connect( s.valids[-1],       s.out.val )

    # Control

    s.connect( s.in_.rdy, s.not_stall  )
    s.connect( s.out.val, s.valids[-1] )

    @s.combinational
    def comb_logic():

      stall             = s.out.val and not s.out.rdy
      s.not_stall.value = not stall

    @s.posedge_clk
    def comb_logic():

      if   s.reset:     s.valids[0].next = 0
      elif s.not_stall: s.valids[0].next = s.in_.val and s.in_.rdy

      for i in range( 1, s.nstages ):
        if s.reset:       s.valids[i].next = 0
        elif s.not_stall: s.valids[i].next = s.valids[i-1]

  def line_trace( s ):
    valid = "{:0{width}b}".format( concat(*s.valids).uint(), width=s.nstages )
    stall = " " if s.not_stall else "S"
    return "{} {} {} {}".format( s.in_, stall, valid, s.out )



#-----------------------------------------------------------------------
# Multiplier
#-----------------------------------------------------------------------
class Multiplier( Model ):
  def __init__( s, nbits, nstages=1 ):
    assert nstages >= 1
    s.a       = InPort ( nbits )
    s.b       = InPort ( nbits )
    s.enables = InPort ( nstages )
    s.product = OutPort( nbits )

    s.nbits   = nbits
    s.nstages = nstages

  def elaborate_logic( s ):

    s.regs    = [ Wire( s.nbits ) for x in range( s.nstages ) ]
    s.mul_out = Wire( 2*s.nbits )

    @s.combinational
    def mult_logic():
      s.mul_out.value = s.a * s.b

    @s.posedge_clk
    def mult_logic():
      if s.reset:
        for i in range( s.nstages ):
          s.regs[i].next = 0

      else:
        if s.enables[0]:
          s.regs[0].next = s.mul_out[0:32]

        for i in range( 1, s.nstages ):
          if s.enables[i]:
            s.regs[i].next = s.regs[i-1]

    s.connect( s.product, s.regs[-1] )

