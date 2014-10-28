#=========================================================================
# ParcV1 ALU
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# Function Constants
#-------------------------------------------------------------------------

ADD  =  0
SUB  =  1
OR   =  2
SLL  =  3
SLT  =  4
SLTU =  5
AND  =  6
XOR  =  7
NOR  =  8
SRL  =  9
SRA  = 10

#-------------------------------------------------------------------------
# ALU
#-------------------------------------------------------------------------
class ALU( Model ):

  #-----------------------------------------------------------------------
  # Port Interface
  #-----------------------------------------------------------------------
  def __init__( s, nbits ):

    s.in0 = InPort(  nbits )
    s.in1 = InPort(  nbits )
    s.sel = InPort(      4 )
    s.out = OutPort( nbits )

    s.nbits = nbits

  #-----------------------------------------------------------------------
  # Combinational Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.ones  = Wire( s.nbits )
    s.mask  = Wire( s.nbits )
    s.sign  = Wire( 1 )
    s.diff  = Wire( s.nbits )

    @s.combinational
    def comb_logic():

      if   s.sel == ADD: s.out.value = s.in0 + s.in1
      elif s.sel == SUB: s.out.value = s.in0 - s.in1
      elif s.sel == OR:  s.out.value = s.in0 | s.in1
      elif s.sel == SLL: s.out.value = s.in1 << s.in0[0:5]
      elif s.sel == AND: s.out.value = s.in0 & s.in1
      elif s.sel == XOR: s.out.value = s.in0 ^ s.in1
      elif s.sel == NOR: s.out.value = ~( s.in0 | s.in1 )
      elif s.sel == SRL: s.out.value = s.in1 >> s.in0[0:5]

      elif s.sel == SRA:
        # TODO: this is not scalable by nbits!!!
        s.mask.value  = Bits( 32, 0xffffffff ) << (32 - s.in0[0:5])
        if s.in1[31]:
          if s.in0[0:5] == 0: s.out.value = s.in1
          else:               s.out.value =(s.in1 >> s.in0[0:5]) | s.mask
        else:                 s.out.value = s.in1 >> s.in0[0:5]

      elif s.sel.value == SLT:
        s.sign.value = s.in0[31] ^ s.in1[31]
        s.diff.value = s.in0 - s.in1
        if    s.sign &  s.in0 [31]: s.out.value = 1
        elif  s.sign & ~s.in0 [31]: s.out.value = 0
        elif ~s.sign & ~s.diff[31]: s.out.value = 0
        elif ~s.sign &  s.diff[31]: s.out.value = 1

      elif s.sel == SLTU:
        s.sign.value = s.in0[31] ^ s.in1[31]
        s.diff.value = s.in0 - s.in1
        if    s.sign &  s.in0 [31]: s.out.value = 0
        elif  s.sign & ~s.in0 [31]: s.out.value = 1
        elif ~s.sign & ~s.diff[31]: s.out.value = 0
        elif ~s.sign &  s.diff[31]: s.out.value = 1

      else:
        raise Exception("Unimplemented ALU operation!")

  def line_trace( s ):
    return "{} ({}) {} = {}".format(s.in0, s.sel, s.in1, s.out)
