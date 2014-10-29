#=========================================================================
# PisaSemantics
#=========================================================================
# This class defines the semantics for each instruction in the ISA.
#
# Author : Christopher Batten
# Date   : May 22, 2014

from pymtl            import Bits,concat
from pymtl.datatypes  import helpers
from PisaInst         import PisaInst

#-------------------------------------------------------------------------
# Syntax Helpers
#-------------------------------------------------------------------------

def sext( bits ):
  return helpers.sext( bits, 32 )

def zext( bits ):
  return helpers.zext( bits, 32 )

class PisaSemantics (object):

  #-----------------------------------------------------------------------
  # IllegalInstruction
  #-----------------------------------------------------------------------

  class IllegalInstruction (Exception):
    pass

  #-----------------------------------------------------------------------
  # RegisterFile
  #-----------------------------------------------------------------------

  class RegisterFile (object):

    def __init__( self ):
      self.regs = [ Bits(32,0) for i in xrange(32) ]

    def __getitem__( self, idx ):
      return self.regs[idx]

    def __setitem__( self, idx, value ):
      if idx != 0:
        self.regs[idx] = Bits( 32, value, trunc=True )

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, memory, mngr2proc_queue, proc2mngr_queue,
                xcel_mvmult=None ):

    self.M = memory

    self.mngr2proc_queue = mngr2proc_queue
    self.proc2mngr_queue = proc2mngr_queue

    self.xcel_mvmult = xcel_mvmult

    self.R     = PisaSemantics.RegisterFile()

    self.reset()

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset( s ):

    s.PC = Bits( 32, 0x00000400 )
    s.stats_en = False
    s.status   = 0

  #-----------------------------------------------------------------------
  # Basic Instructions
  #-----------------------------------------------------------------------

  def execute_mfc0( s, inst ):

    # CP0 register: mngr2proc
    if inst.rd == 1:
      bits = s.mngr2proc_queue.popleft()
      s.mngr2proc_str = str(bits)
      s.R[inst.rt] = bits

    # CPO register: coreid
    elif inst.rd == 17:
      s.R[inst.rt] = 0

    else:
      raise PisaSemantics.IllegalInstruction(
        "Unrecognized CPO register ({}) for mfc0 at PC={}" \
          .format(inst.rd.uint(),s.PC) )

    s.PC += 4

  def execute_mtc0( s, inst ):

    # CP0 register: status
    if inst.rd == 1:
      s.status = s.R[inst.rt]

    # CP0 register: proc2mngr
    elif inst.rd == 2:
      bits = s.R[inst.rt]
      s.proc2mngr_str = str(bits)
      s.proc2mngr_queue.append( bits )

    # CPO register: stats_en
    elif inst.rd == 10:
      s.stats_en = bool(s.R[inst.rt])

    else:
      raise PisaSemantics.IllegalInstruction(
        "Unrecognized CPO register ({}) for mtc0 at PC={}" \
          .format(inst.rd.uint(),s.PC) )

    s.PC += 4

  def execute_nop( s, inst ):
    s.PC += 4

  #-----------------------------------------------------------------------
  # Register-register arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------

  def execute_addu( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] + s.R[inst.rt]
    s.PC += 4

  def execute_subu( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] - s.R[inst.rt]
    s.PC += 4

  def execute_and( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] & s.R[inst.rt]
    s.PC += 4

  def execute_or( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] | s.R[inst.rt]
    s.PC += 4

  def execute_xor( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] ^ s.R[inst.rt]
    s.PC += 4

  def execute_nor( s, inst ):
    s.R[inst.rd] = ~( s.R[inst.rs] | s.R[inst.rt] )
    s.PC += 4

  def execute_slt( s, inst ):
    s.R[inst.rd] = s.R[inst.rs].int() < s.R[inst.rt].int()
    s.PC += 4

  def execute_sltu( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] < s.R[inst.rt]
    s.PC += 4

  #-----------------------------------------------------------------------
  # Register-immediate arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------

  def execute_addiu( s, inst ):
    s.R[inst.rt] = s.R[inst.rs] + sext(inst.imm)
    s.PC += 4

  def execute_andi( s, inst ):
    s.R[inst.rt] = s.R[inst.rs] & zext(inst.imm)
    s.PC += 4

  def execute_ori( s, inst ):
    s.R[inst.rt] = s.R[inst.rs] | zext(inst.imm)
    s.PC += 4

  def execute_xori( s, inst ):
    s.R[inst.rt] = s.R[inst.rs] ^ zext(inst.imm)
    s.PC += 4

  def execute_slti( s, inst ):
    s.R[inst.rt] = s.R[inst.rs].int() < sext(inst.imm).int()
    s.PC += 4

  def execute_sltiu( s, inst ):
    s.R[inst.rt] = s.R[inst.rs] < sext(inst.imm)
    s.PC += 4

  #-----------------------------------------------------------------------
  # Shift instructions
  #-----------------------------------------------------------------------

  def execute_sll( s, inst ):
    s.R[inst.rd] = s.R[inst.rt] << inst.shamt
    s.PC += 4

  def execute_srl( s, inst ):
    s.R[inst.rd] = s.R[inst.rt] >> inst.shamt
    s.PC += 4

  def execute_sra( s, inst ):
    s.R[inst.rd] = s.R[inst.rt].int() >> inst.shamt.uint()
    s.PC += 4

  def execute_sllv( s, inst ):
    s.R[inst.rd] = s.R[inst.rt] << s.R[inst.rs][0:5]
    s.PC += 4

  def execute_srlv( s, inst ):
    s.R[inst.rd] = s.R[inst.rt] >> s.R[inst.rs][0:5]
    s.PC += 4

  def execute_srav( s, inst ):
    s.R[inst.rd] = s.R[inst.rt].int() >> s.R[inst.rs][0:5].uint()
    s.PC += 4

  #-----------------------------------------------------------------------
  # Other instructions
  #-----------------------------------------------------------------------

  def execute_lui( s, inst ):
    s.R[inst.rt] = zext(inst.imm) << 16
    s.PC += 4

  #-----------------------------------------------------------------------
  # Multiply/divide instructions
  #-----------------------------------------------------------------------

  def execute_mul( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] * s.R[inst.rt]
    s.PC += 4

  def execute_div( s, inst ):

    # Python rounds to negative infinity even for negative values, so we
    # need to do something a little more complicated. This was inspired
    # from this post:
    #
    #  http://stackoverflow.com/questions/19919387
    #

    a = s.R[inst.rs].int()
    b = s.R[inst.rt].int()

    A = -a if (a < 0) else a
    B = -b if (b < 0) else b
    c = -(A // B) if (a < 0) ^ (b < 0) else (A // B)

    s.R[inst.rd] = c
    s.PC += 4

  def execute_divu( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] / s.R[inst.rt]
    s.PC += 4

  def execute_rem( s, inst ):

    a = s.R[inst.rs].int()
    b = s.R[inst.rt].int()

    A = -a if (a < 0) else a
    B = -b if (b < 0) else b
    c = -(A % B) if (a < 0) else (A % B)

    s.R[inst.rd] = c
    s.PC += 4

  def execute_remu( s, inst ):
    s.R[inst.rd] = s.R[inst.rs] % s.R[inst.rt]
    s.PC += 4

  #-----------------------------------------------------------------------
  # Load instructions
  #-----------------------------------------------------------------------

  def execute_lw( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.R[inst.rt] = s.M[addr:addr+4]
    s.PC += 4

  def execute_lh( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.R[inst.rt] = sext( s.M[addr:addr+2] )
    s.PC += 4

  def execute_lhu( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.R[inst.rt] = zext( s.M[addr:addr+2] )
    s.PC += 4

  def execute_lb( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.R[inst.rt] = sext( s.M[addr:addr+1] )
    s.PC += 4

  def execute_lbu( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.R[inst.rt] = zext( s.M[addr:addr+1] )
    s.PC += 4

  #-----------------------------------------------------------------------
  # Store instructions
  #-----------------------------------------------------------------------

  def execute_sw( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.M[addr:addr+4] = s.R[inst.rt]
    s.PC += 4

  def execute_sh( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.M[addr:addr+2] = s.R[inst.rt][0:16]
    s.PC += 4

  def execute_sb( s, inst ):
    addr = s.R[inst.rs] + sext(inst.imm)
    s.M[addr:addr+1] = s.R[inst.rt][0:8]
    s.PC += 4

  #-----------------------------------------------------------------------
  # Unconditional jump instructions
  #-----------------------------------------------------------------------

  def execute_j( s, inst ):
    s.PC = concat( (s.PC+4)[28:32], inst.jtarg, Bits(2,0) )

  def execute_jal( s, inst ):
    s.R[31] = s.PC + 4
    s.PC = concat( (s.PC+4)[28:32], inst.jtarg, Bits(2,0) )

  def execute_jr( s, inst ):
    s.PC = s.R[inst.rs]

  def execute_jalr( s, inst ):
    s.R[inst.rd] = s.PC + 4
    s.PC = s.R[inst.rs]

  #-----------------------------------------------------------------------
  # Conditional branch instructions
  #-----------------------------------------------------------------------

  def execute_beq( s, inst ):
    if s.R[inst.rs] == s.R[inst.rt]:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  def execute_bne( s, inst ):
    if s.R[inst.rs] != s.R[inst.rt]:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  def execute_blez( s, inst ):
    if s.R[inst.rs].int() <= 0:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  def execute_bgtz( s, inst ):
    if s.R[inst.rs].int() > 0:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  def execute_bltz( s, inst ):
    if s.R[inst.rs].int() < 0:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  def execute_bgez( s, inst ):
    if s.R[inst.rs].int() >= 0:
      s.PC = s.PC + 4 + ( sext(inst.imm) << 2 )
    else:
      s.PC += 4

  #-----------------------------------------------------------------------
  # CP2 instructions
  #-----------------------------------------------------------------------

  def execute_mtc2( s, inst ):

    if   inst.rd == 1: s.xcel_mvmult.set_size      ( s.R[inst.rt] )
    elif inst.rd == 2: s.xcel_mvmult.set_src0_addr ( s.R[inst.rt] )
    elif inst.rd == 3: s.xcel_mvmult.set_src1_addr ( s.R[inst.rt] )
    elif inst.rd == 4: s.xcel_mvmult.set_dest_addr ( s.R[inst.rt] )

    elif inst.rd == 0 and s.R[inst.rt] == 1:
      s.xcel_mvmult.go()

    s.PC += 4

  #-----------------------------------------------------------------------
  # exec
  #-----------------------------------------------------------------------

  execute_dispatch = {

    'mfc0'  : execute_mfc0,
    'mtc0'  : execute_mtc0,
    'nop'   : execute_nop,
    'addu'  : execute_addu,
    'subu'  : execute_subu,
    'and'   : execute_and,
    'or'    : execute_or,
    'xor'   : execute_xor,
    'nor'   : execute_nor,
    'slt'   : execute_slt,

    'sltu'  : execute_sltu,
    'addiu' : execute_addiu,
    'andi'  : execute_andi,
    'ori'   : execute_ori,
    'xori'  : execute_xori,
    'slti'  : execute_slti,
    'sltiu' : execute_sltiu,
    'sll'   : execute_sll,
    'srl'   : execute_srl,
    'sra'   : execute_sra,

    'sllv'  : execute_sllv,
    'srlv'  : execute_srlv,
    'srav'  : execute_srav,
    'lui'   : execute_lui,
    'mul'   : execute_mul,
    'div'   : execute_div,
    'divu'  : execute_divu,
    'rem'   : execute_rem,
    'remu'  : execute_remu,
    'lw'    : execute_lw,

    'lh'    : execute_lh,
    'lhu'   : execute_lhu,
    'lb'    : execute_lb,
    'lbu'   : execute_lbu,
    'sw'    : execute_sw,
    'sh'    : execute_sh,
    'sb'    : execute_sb,
    'j'     : execute_j,
    'jal'   : execute_jal,
    'jr'    : execute_jr,

    'jalr'  : execute_jalr,
    'beq'   : execute_beq,
    'bne'   : execute_bne,
    'blez'  : execute_blez,
    'bgtz'  : execute_bgtz,
    'bltz'  : execute_bltz,
    'bgez'  : execute_bgez,

    'mtc2'  : execute_mtc2,

  }

  def execute( self, inst ):
    self.execute_dispatch[inst.name]( self, inst )
