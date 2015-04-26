#=========================================================================
# ParcProcCL
#=========================================================================

import collections
import copy

from pymtl           import *
from pymtl.datatypes import helpers
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from pclib.ifcs      import XcelReqMsg, XcelRespMsg
from pclib.ifcs      import MemMsg, MemReqMsg, MemRespMsg
from pisa            import PisaInst
from pclib.fl        import Queue
from pclib.cl        import InValRdyQueueAdapter, OutValRdyQueueAdapter

#-------------------------------------------------------------------------
# Syntax Helpers
#-------------------------------------------------------------------------

def sext( bits ):
  return helpers.sext( bits, 32 )

def zext( bits ):
  return helpers.zext( bits, 32 )

#-------------------------------------------------------------------------
# Writeaback
#-------------------------------------------------------------------------

class WB (object):

  NONE  = 0
  REGWR = 1
  LOAD  = 2
  STORE = 3
  MTX   = 4
  MFX   = 5

  LOAD_LW  = 0
  LOAD_LH  = 1
  LOAD_LHU = 2
  LOAD_LB  = 3
  LOAD_LBU = 4

  def __init__( s, dest=None, value=None, type_=None, load_type=0 ):
    if dest != None and type_ == None:
      s.type = WB.REGWR
    elif dest == None and value == None and type_ == None:
      s.type = WB.NONE
    else:
      s.type = type_
    s.dest  = dest
    s.value = value
    s.load_type = load_type

class ParcProcCL (Model):

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

  def __init__( s, reset_vector=0, test_en=True ):

    s.reset_vector = reset_vector
    s.test_en      = test_en

    # Proc/Mngr Interface

    s.mngr2proc  = InValRdyBundle( 32 )
    s.proc2mngr  = OutValRdyBundle( 32 )

    # Instruction Memory Request/Response Interface

    s.imemreq    = OutValRdyBundle ( MemReqMsg(32,32) )
    s.imemresp   = InValRdyBundle  ( MemRespMsg(32)   )

    # Data Memory Request/Response Interface

    s.dmemreq    = OutValRdyBundle ( MemReqMsg(32,32) )
    s.dmemresp   = InValRdyBundle  ( MemRespMsg(32)   )

    # Accelerator Interface

    s.xcelreq    = OutValRdyBundle( XcelReqMsg() )
    s.xcelresp   = InValRdyBundle( XcelRespMsg() )

    # Extra Interface

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Queue Adapters

    s.mngr2proc_q     = InValRdyQueueAdapter  ( s.mngr2proc )
    s.proc2mngr_q     = OutValRdyQueueAdapter ( s.proc2mngr )

    s.imemreq_q       = OutValRdyQueueAdapter ( s.imemreq   )
    s.imemresp_q      = InValRdyQueueAdapter  ( s.imemresp  )

    s.dmemreq_q       = OutValRdyQueueAdapter ( s.dmemreq   )
    s.dmemresp_q      = InValRdyQueueAdapter  ( s.dmemresp  )

    s.xcelreq_q       = OutValRdyQueueAdapter ( s.xcelreq   )
    s.xcelresp_q      = InValRdyQueueAdapter  ( s.xcelresp  )

    # Helpers to make memory read/write requests

    mem_ifc_types = MemMsg(32,32)
    s.mk_rd = mem_ifc_types.req.mk_rd
    s.mk_wr = mem_ifc_types.req.mk_wr

    # Pipeline queues

    s.pc_queue_FX     = Queue(4)
    s.inst_queue_XW   = Queue(4)
    s.wb_queue_XW     = Queue(4)

    s.R = ParcProcCL.RegisterFile()

    s.stall_X = False
    s.stall_W = False

    s.stall_type_X = " "
    s.stall_type_W = " "

    s.WB_NONE  = 0
    s.WB_REGWR = 1

    s.ifetch_wait = 0

    # Reset

    s.reset_proc()

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset_proc( s ):

    # Copies of pc and inst

    s.PC   = Bits( 32, 0x00000400 )
    s.inst = Bits( 32, 0x00000000 )
    s.stall_X = False
    s.stall_W = False

    # Stats

    s.num_total_inst = 0
    s.num_inst       = 0

  #-----------------------------------------------------------------------
  # Bypass logic
  #-----------------------------------------------------------------------

  def bypass1( s, reg ):

    src = s.R[reg]

    for entry in s.wb_queue_XW.queue:
      if entry.dest == reg:
        if entry.type == WB.REGWR:
          src = entry.value
        elif entry.type in [ WB.LOAD, WB.MFX ]:
          s.stall_X = True
          s.stall_type_X = "b"

    return src

  def bypass2( s, reg0, reg1 ):
    src0 = s.R[reg0]
    src1 = s.R[reg1]

    for entry in s.wb_queue_XW.queue:

      if entry.dest == reg0:
        if entry.type == WB.REGWR:
          src0 = entry.value
        elif entry.type in [ WB.LOAD, WB.MFX ]:
          s.stall_X = True
          s.stall_type_X = "b"

      if entry.dest == reg1:
        if entry.type == WB.REGWR:
          src1 = entry.value
        elif entry.type in [ WB.LOAD, WB.MFX ]:
          s.stall_X = True
          s.stall_type_X = "b"

    return ( src0, src1 )

  #-----------------------------------------------------------------------
  # update_pc
  #-----------------------------------------------------------------------

  def update_pc( s, pc ):

    # Determine how many ifetches are inflight

    s.ifetch_wait = \
        len(s.pc_queue_FX) \
      - len(s.imemresp_q) \
      - len(s.imemreq_q)

    # Clear the front end queues

    s.imemreq_q.clear()
    s.imemresp_q.clear()
    s.pc_queue_FX.clear()

    # Update the PC

    s.PC = pc

  #-----------------------------------------------------------------------
  # Basic Instructions
  #-----------------------------------------------------------------------

  def execute_mfc0( s, inst ):

    # CP0 register: mngr2proc
    if inst.rd == 1:
      if not s.mngr2proc_q.empty():
        s.wb_queue_XW.enq( WB( inst.rt, s.mngr2proc_q.deq() ) )
      else:
        s.stall_X = True
        s.stall_type_X = "M"

    # CPO register: coreid
    elif inst.rd == 17:
      s.R[inst.rt] = 0

    else:
      raise ParcProcCL.IllegalInstruction(
        "Unrecognized CPO register ({}) for mfc0 at PC={}" \
          .format(inst.rd.uint(),s.PC) )

  def execute_mtc0( s, inst ):

    # CP0 register: status
    if inst.rd == 1:
      s.status.next = s.R[inst.rt]

    # CP0 register: proc2mngr
    elif inst.rd == 2:
      if not s.proc2mngr_q.full():
        RT = s.bypass1( inst.rt )
        if not s.stall_X:
          s.wb_queue_XW.enq( WB() )
          s.proc2mngr_q.enq( RT )
      else:
        s.stall_X = True
        s.stall_type_X = "M"

    # CPO register: stats_en
    elif inst.rd == 10:
      s.stats_en.next = s.R[inst.rt][0]

    else:
      raise ParcProcCL.IllegalInstruction(
        "Unrecognized CPO register ({}) for mtc0 at PC={}" \
          .format(inst.rd.uint(),s.PC) )

  def execute_nop( s, inst ):
    s.wb_queue_XW.enq( WB() )

  #-----------------------------------------------------------------------
  # Register-register arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------

  def execute_addu( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS + RT ) )

  def execute_subu( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS - RT ) )

  def execute_and( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS & RT ) )

  def execute_or( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS | RT ) )

  def execute_xor( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS ^ RT ) )

  def execute_nor( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, ~( RS | RT ) ) )

  def execute_slt( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS.int() < RT.int() ) )

  def execute_sltu( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS < RT ) )

  #-----------------------------------------------------------------------
  # Register-immediate arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------

  def execute_addiu( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS + sext(inst.imm) ) )

  def execute_andi( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS & zext(inst.imm) ) )

  def execute_ori( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS | zext(inst.imm) ) )

  def execute_xori( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS ^ zext(inst.imm) ) )

  def execute_slti( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS.int() < sext(inst.imm).int() ) )

  def execute_sltiu( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rt, RS < sext(inst.imm) ) )

  #-----------------------------------------------------------------------
  # Shift instructions
  #-----------------------------------------------------------------------

  def execute_sll( s, inst ):
    RT = s.bypass1( inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT << inst.shamt ) )

  def execute_srl( s, inst ):
    RT = s.bypass1( inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT >> inst.shamt ) )

  def execute_sra( s, inst ):
    RT = s.bypass1( inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT.int() >> inst.shamt.uint() ) )

  def execute_sllv( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT << RS[0:5] ) )

  def execute_srlv( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT >> RS[0:5] ) )

  def execute_srav( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RT.int() >> RS[0:5].uint() ) )

  #-----------------------------------------------------------------------
  # Other instructions
  #-----------------------------------------------------------------------

  def execute_lui( s, inst ):
    s.wb_queue_XW.enq( WB( inst.rt, zext(inst.imm) << 16 ) )

  #-----------------------------------------------------------------------
  # Multiply/divide instructions
  #-----------------------------------------------------------------------

  def execute_mul( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS * RT ) )

  def execute_div( s, inst ):

    # Python rounds to negative infinity even for negative values, so we
    # need to do something a little more complicated. This was inspired
    # from this post:
    #
    #  http://stackoverflow.com/questions/19919387
    #

    RS,RT = s.bypass2( inst.rs, inst.rt )

    if not s.stall_X:

      a = s.R[inst.rs].int()
      b = s.R[inst.rt].int()

      A = -a if (a < 0) else a
      B = -b if (b < 0) else b
      c = -(A // B) if (a < 0) ^ (b < 0) else (A // B)

      s.wb_queue_XW.enq( WB( inst.rd, c ) )

  def execute_divu( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS / RT ) )

  def execute_rem( s, inst ):

    RS,RT = s.bypass2( inst.rs, inst.rt )

    if not s.stall_X:

      a = RS.int()
      b = RT.int()

      A = -a if (a < 0) else a
      B = -b if (b < 0) else b
      c = -(A % B) if (a < 0) else (A % B)

      s.wb_queue_XW.enq( WB( inst.rd, c ) )

  def execute_remu( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, RS % RT ) )

  #-----------------------------------------------------------------------
  # Load instructions
  #-----------------------------------------------------------------------

  def execute_lw( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_rd( addr, 0 ) )
        s.wb_queue_XW.enq( WB( inst.rt, type_=WB.LOAD, load_type=WB.LOAD_LW ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_lh( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_rd( addr, 2 ) )
        s.wb_queue_XW.enq( WB( inst.rt, type_=WB.LOAD, load_type=WB.LOAD_LH ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_lhu( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_rd( addr, 2 ) )
        s.wb_queue_XW.enq( WB( inst.rt, type_=WB.LOAD, load_type=WB.LOAD_LHU ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_lb( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_rd( addr, 1 ) )
        s.wb_queue_XW.enq( WB( inst.rt, type_=WB.LOAD, load_type=WB.LOAD_LB ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_lbu( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_rd( addr, 1 ) )
        s.wb_queue_XW.enq( WB( inst.rt, type_=WB.LOAD, load_type=WB.LOAD_LBU ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  #-----------------------------------------------------------------------
  # Store instructions
  #-----------------------------------------------------------------------

  def execute_sw( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_wr( addr, 0, RT ) )
        s.wb_queue_XW.enq( WB( type_=WB.STORE ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_sh( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_wr( addr, 2, RT ) )
        s.wb_queue_XW.enq( WB( type_=WB.STORE ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  def execute_sb( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      if not s.dmemreq_q.full():
        addr = RS + sext(inst.imm)
        s.dmemreq_q.enq( s.mk_wr( addr, 1, RT ) )
        s.wb_queue_XW.enq( WB( type_=WB.STORE ) )
      else:
        s.stall_X = True
        s.stall_type_X = "m"

  #-----------------------------------------------------------------------
  # Unconditional jump instructions
  #-----------------------------------------------------------------------

  def execute_j( s, inst ):
    pc = s.pc_queue_FX.front()
    s.wb_queue_XW.enq( WB() )
    s.update_pc( concat( (pc+4)[28:32], inst.jtarg, Bits(2,0) ) )

  def execute_jal( s, inst ):
    pc = s.pc_queue_FX.front()
    s.wb_queue_XW.enq( WB( 31, pc + 4 ) )
    s.update_pc( concat( (pc+4)[28:32], inst.jtarg, Bits(2,0) ) )

  def execute_jr( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      s.update_pc( RS )

  def execute_jalr( s, inst ):
    pc = s.pc_queue_FX.front()
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB( inst.rd, pc + 4 ) )
      s.update_pc( RS )

  #-----------------------------------------------------------------------
  # Conditional branch instructions
  #-----------------------------------------------------------------------

  def execute_beq( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS == RT:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  def execute_bne( s, inst ):
    RS,RT = s.bypass2( inst.rs, inst.rt )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS != RT:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  def execute_blez( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS.int() <= 0:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  def execute_bgtz( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS.int() > 0:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  def execute_bltz( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS.int() < 0:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  def execute_bgez( s, inst ):
    RS = s.bypass1( inst.rs )
    if not s.stall_X:
      s.wb_queue_XW.enq( WB() )
      pc = s.pc_queue_FX.front()
      if RS.int() >= 0:
        s.update_pc( pc + 4 + ( sext(inst.imm) << 2 ) )

  #-----------------------------------------------------------------------
  # Accelerator instructions
  #-----------------------------------------------------------------------

  def execute_mtx( s, inst ):
    RT = s.bypass1( inst.rt )
    if not s.stall_X:
      if not s.xcelreq_q.full():
        s.xcelreq_q.enq( XcelReqMsg().mk_wr( inst.rs, RT ) )
        s.wb_queue_XW.enq( WB( 0, type_=WB.MTX ) )
      else:
        s.stall_X = True
        s.stall_type_X = "x"

  def execute_mfx( s, inst ):
    if not s.xcelreq_q.full():
      s.xcelreq_q.enq( XcelReqMsg().mk_rd( inst.rs ) )
      s.wb_queue_XW.enq( WB( inst.rt, type_=WB.MFX ) )
    else:
      s.stall_X = True
      s.stall_type_X = "x"

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

    'mtx'   : execute_mtx,
    'mfx'   : execute_mfx,

  }

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    # Currently we can never really stall the response port

    s.connect( s.imemresp.rdy, 1 )

    @s.tick
    def logic():

      s.mngr2proc_q.xtick()
      s.proc2mngr_q.xtick()
      s.xcelreq_q.xtick()
      s.xcelresp_q.xtick()
      s.imemreq_q.xtick()
      s.imemresp_q.xtick()
      s.dmemreq_q.xtick()
      s.dmemresp_q.xtick()

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # W: Writeback Pipeline Stage
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_W = " "*5
      if not s.inst_queue_XW.empty() and not s.wb_queue_XW.empty():

        inst = s.inst_queue_XW.front()
        wb   = s.wb_queue_XW.front()

        s.stall_W = False
        s.trace_W = str(inst.name).ljust(5)
        if wb.type == WB.REGWR:
          s.R[ wb.dest ] = wb.value

        elif wb.type == WB.LOAD:
          if not s.dmemresp_q.empty():

            if wb.load_type == WB.LOAD_LW:
              s.R[wb.dest] = s.dmemresp_q.deq()

            elif wb.load_type == WB.LOAD_LH:
              s.R[wb.dest] = sext( s.dmemresp_q.deq()[0:16] )

            elif wb.load_type == WB.LOAD_LHU:
              s.R[wb.dest] = zext( s.dmemresp_q.deq()[0:16] )

            elif wb.load_type == WB.LOAD_LB:
              s.R[wb.dest] = sext( s.dmemresp_q.deq()[0:8] )

            elif wb.load_type == WB.LOAD_LBU:
              s.R[wb.dest] = zext( s.dmemresp_q.deq()[0:8] )

            else:
              raise AssertionError()

          else:
            s.stall_W = True
            s.trace_W = "#m".ljust(5)

        elif wb.type == WB.STORE:
          if not s.dmemresp_q.empty():
            s.dmemresp_q.deq()
          else:
            s.stall_W = True
            s.trace_W = "#m".ljust(5)

        elif wb.type == WB.MTX:
          if not s.xcelresp_q.empty():
            s.xcelresp_q.deq()
          else:
            s.stall_W = True
            s.trace_W = "#x".ljust(5)

        elif wb.type == WB.MFX:
          if not s.xcelresp_q.empty():
            s.R[wb.dest] = s.xcelresp_q.deq()
          else:
            s.stall_W = True
            s.trace_W = "#x".ljust(5)

        if not s.stall_W:
          s.inst_queue_XW.deq()
          s.wb_queue_XW.deq()

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # X: Execute Pipeline Stage
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_X = " "*29

      if s.ifetch_wait > 0:

        s.trace_X = "~w{}".format(s.ifetch_wait).ljust(29)
        if not s.imemresp_q.empty():
          inst = PisaInst(s.imemresp_q.first())
          s.ifetch_wait -= 1
          s.trace_X = "~w{}".format(s.ifetch_wait).ljust(29)
          s.imemresp_q.deq()

      elif     not s.pc_queue_FX.empty() \
           and not s.imemresp_q.empty() \
           and not s.inst_queue_XW.full() \
           and not s.wb_queue_XW.full():

        s.stall_X = False
        inst = PisaInst(s.imemresp_q.first())
        s.execute_dispatch[inst.name]( s, inst )

        if not s.stall_X:
          if not s.pc_queue_FX.empty():
            s.pc_queue_FX.deq()
            s.imemresp_q.deq()
          s.inst_queue_XW.enq( inst )
          s.trace_X = str(inst).ljust(29)
        else:
          s.trace_X = ( "#" + s.stall_type_X ).ljust(29)

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # F: Fetch Pipeline Stage
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_F = "  ".ljust(8)

      if s.imemreq_q.full() and s.pc_queue_FX.full():
        s.trace_F = "#X".ljust(8)
      elif s.imemreq_q.full():
        s.trace_F = "#m".ljust(8)
      elif s.pc_queue_FX.full():
        s.trace_F = "#x".ljust(8)
      else:

        s.imemreq_q.enq( s.mk_rd( s.PC, 0 ) )
        s.pc_queue_FX.enq( s.PC )
        s.PC      += 4
        s.trace_F = str(s.PC)

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace_F + "|" + s.trace_X + "|" + s.trace_W

