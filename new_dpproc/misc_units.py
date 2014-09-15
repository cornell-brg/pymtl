#=======================================================================
# misc_units.py
#=======================================================================
# Collection of Miscellaneous Processor Logic Units

from new_pymtl import *

#=======================================================================
# BranchTarget
#=======================================================================
class BranchTarget(Model):

  def __init__( s, nbits ):
    s.nbits = nbits
    s.pc_4  = InPort  (  nbits )
    s.imm   = InPort  (  16    )
    s.out   = OutPort ( nbits  )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.pc_4 + ( sext( s.imm, s.nbits ) << 2 )

#=======================================================================
# JumpTarget
#=======================================================================
class JumpTarget(Model):

  def __init__( s, nbits ):
    s.nbits = nbits
    s.pc_4  = InPort  ( nbits )
    s.tgt   = InPort  ( 26    )
    s.out   = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = concat( s.pc_4[28:32], s.tgt, Bits(2, 0) )
      #s.out.value = (s.pc_4[28:32] << 28) + (s.tgt << 2)
