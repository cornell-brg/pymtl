#=========================================================================
# Lab 2 - ParcProc5stBypassDecodeCtrl
#=========================================================================

from pymtl import *

from ParcISA        import *
from DecodeInstType import DecodeInstType

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

# Control Signal Bus Width

CS_WIDTH = 46

# Control Signal Bus Definition

# For use with cs function
#RS_EN        = slice(  0, 1  ) # 1
#RS_RADDR     = slice(  1, 6  ) # 5
#RT_EN        = slice(  6, 7  ) # 1
#RT_RADDR     = slice(  7, 12 ) # 5
#RF_WEN       = slice( 12, 13 ) # 1
#RF_WADDR     = slice( 13, 18 ) # 5
#OP0_MUX_SEL  = slice( 18, 20 ) # 2
#OP1_MUX_SEL  = slice( 20, 22 ) # 2
#ALU_FN       = slice( 22, 26 ) # 4
#MD_EN        = slice( 26, 27 ) # 1
#MD_FN        = slice( 27, 30 ) # 3
#EX_MUX_SEL   = slice( 30, 31 ) # 1
#MEM_REQ_EN   = slice( 31, 32 ) # 1
#MEM_REQ_TYPE = slice( 33, 34 ) # 1
#MEM_REQ_LEN  = slice( 34, 36 ) # 2
#MEM_RESP_SEL = slice( 36, 39 ) # 3
#WB_MUX_SEL   = slice( 39, 40 ) # 1
#CPR_WEN      = slice( 40, 41 ) # 1
#CPR_WADDR    = slice( 41, 46 ) # 5
#CP2_WEN      = slice( 46, 47 ) # 1

# Concat definition
#RS_EN        = slice( 45, 46 )  # 1
#RS_RADDR     = slice( 40, 45 )  # 5
#RT_EN        = slice( 39, 40 )  # 1
#RT_RADDR     = slice( 34, 39 )  # 5
#RF_WEN       = slice( 33, 34 )  # 1
#RF_WADDR     = slice( 28, 33 )  # 5
#OP0_MUX_SEL  = slice( 26, 28 )  # 2
#OP1_MUX_SEL  = slice( 24, 26 )  # 2
#ALU_FN       = slice( 20, 24 )  # 4
#MD_EN        = slice( 19, 20 )  # 1
#MD_FN        = slice( 16, 19 )  # 3
#EX_MUX_SEL   = slice( 15, 16 )  # 1
#MEM_REQ_EN   = slice( 14, 15 )  # 1
#MEM_REQ_TYPE = slice( 13, 14 )  # 1
#MEM_REQ_LEN  = slice( 11, 13 )  # 2
#MEM_RESP_SEL = slice(  8, 11 )  # 3
#WB_MUX_SEL   = slice(  7,  8 )  # 1
#CPR_WEN      = slice(  6,  7 )  # 1
#CPR_WADDR    = slice(  1,  6 )  # 5
#CP2_WEN      = slice(  0,  1 )  # 1

# Control Signal Value Encoding

x        = Bits( 1, 0 )
x2       = Bits( 2, 0 )
x3       = Bits( 3, 0 )
x4       = Bits( 4, 0 )
x5       = Bits( 5, 0 )

y        = Bits( 1, 1 )

alu_add  = Bits( 4,  0 )
alu_sub  = Bits( 4,  1 )
alu_or   = Bits( 4,  2 )
alu_sll  = Bits( 4,  3 )
alu_slt  = Bits( 4,  4 )
alu_sltu = Bits( 4,  5 )
alu_and  = Bits( 4,  6 )
alu_xor  = Bits( 4,  7 )
alu_nor  = Bits( 4,  8 )
alu_srl  = Bits( 4,  9 )
alu_sra  = Bits( 4, 10 )

md_div   = Bits( 3, 0 )
md_rem   = Bits( 3, 1 )
md_mul   = Bits( 3, 2 )
md_divu  = Bits( 3, 3 )
md_remu  = Bits( 3, 4 )

alu      =  Bits( 1, 0 )
md       =  Bits( 1, 1 )

rd0_rf   =  Bits( 2, 0 )
rd0_16   =  Bits( 2, 1 )
rd0_0    =  Bits( 2, 2 )
rd0_sh   =  Bits( 2, 3 )

rd1_rf   =  Bits( 2, 0 )
rd1_zext =  Bits( 2, 1 )
rd1_sext =  Bits( 2, 2 )
rd1_pc4  =  Bits( 2, 3 )

mem_en   =  Bits( 1, 1 )

mem_lw   =  Bits( 1, 0 )
mem_sw   =  Bits( 1, 1 )

byte_    =  Bits( 2, 1 )
hword    =  Bits( 2, 2 )
word     =  Bits( 2, 0 )

sbyte    =  Bits( 3, 1 )
shword   =  Bits( 3, 2 )
ubyte    =  Bits( 3, 3 )
uhword   =  Bits( 3, 4 )

wr_alu   =  Bits( 1, 0 )
wr_mem   =  Bits( 1, 1 )

ra       =  Bits( 5, 31 )

#-------------------------------------------------------------------------
# Control Signal Helper Function
#-------------------------------------------------------------------------

def c( rs_en, rs_addr, rt_en, rt_addr, rf_wen, rf_addr,
       op0_mux_sel, op1_mux_sel, alu_fn, md_en, md_fn,
       ex_mux_sel, mem_req_en, mem_req_type, mem_req_len,
       mem_resp_sel, wb_mux_sel, cpr_wen, cpr_waddr ):

  cs               = Bits( CS_WIDTH )
  cs[RS_EN]        = rs_en
  cs[RS_RADDR]     = rs_addr
  cs[RT_EN]        = rt_en
  cs[RT_RADDR]     = rt_addr
  cs[RF_WEN]       = rf_wen
  cs[RF_WADDR]     = rf_addr
  cs[OP0_MUX_SEL]  = op0_mux_sel
  cs[OP1_MUX_SEL]  = op1_mux_sel
  cs[ALU_FN]       = alu_fn
  cs[MD_EN]        = md_en
  cs[MD_FN]        = md_fn
  cs[EX_MUX_SEL]   = ex_mux_sel
  cs[MEM_REQ_EN]   = mem_req_en
  cs[MEM_REQ_TYPE] = mem_req_type
  cs[MEM_REQ_LEN]  = mem_req_len
  cs[MEM_RESP_SEL] = mem_resp_sel
  cs[WB_MUX_SEL]   = wb_mux_sel
  cs[CPR_WEN]      = cpr_wen
  cs[CPR_WADDR]    = cpr_waddr

  return cs

#-------------------------------------------------------------------------
# Control Signal Decoder
#-------------------------------------------------------------------------

class ParcProc5stBypassDecodeCtrl( Model ):

  def __init__( s ):

    # Interface Ports

    s.inst_bits  = InPort  ( 32 )

    s.cs         = OutPort ( 46 )
    s.inst       = OutPort ( 8  )

  # Static Elaboration
  def elaborate_logic( s ):

    s.inst_type = DecodeInstType()

    s.connect( s.inst_type.in_, s.inst_bits )
    s.connect( s.inst_type.out, s.inst      )

    s.rs_field = Wire( 5 )
    s.rt_field = Wire( 5 )
    s.rd_field = Wire( 5 )

    s.connect( s.rs_field, s.inst_bits[ RS ] )
    s.connect( s.rt_field, s.inst_bits[ RT ] )
    s.connect( s.rd_field, s.inst_bits[ RD ] )

    @s.combinational
    def comb_logic():

      # helper signals

      # TODO: get this inference working! (or replace with bitstruct...)
      #rs   = s.inst_bits[ RS ]
      #rt   = s.inst_bits[ RT ]
      #rd   = s.inst_bits[ RD ]
      rs = s.rs_field
      rt = s.rt_field
      rd = s.rd_field

                                     #  rs rs   rt rt   rf  rf   op0_mux op1_mux   alu       md  md       ex_mux memreq  memreq  memreq memresp wb_mux  cpr cpr   cp2
                                     #  en addr en addr wen addr sel     sel       fn        en  fn       sel    en      type    len    sel     sel     en  waddr en
      if   s.inst == NOP  :cx = concat( x, x5,  x, x5,  x,  x5,  x2,     x2,       x4,       x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == ADDIU:cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == ORI  :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_zext, alu_or,   x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == LUI  :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_16, rd1_zext, alu_sll,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == ADDU :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_add,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == MTC0 :cx = concat( x, x5,  y, rt,  x,  x5,  rd0_0,  rd1_rf,   alu_add,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, y,  rd,   x  )
      elif s.inst == LW   :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_lw, word,  x3,     wr_mem, x,  x5,   x  )
      elif s.inst == SW   :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_sw, word,  x3,     x,      x,  x5,   x  )
      elif s.inst == BNE  :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_xor,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == JAL  :cx = concat( x, x5,  x, x5,  y,  ra,  rd0_0,  rd1_pc4,  alu_add,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == JR   :cx = concat( y, rs,  x, x5,  x,  x5,  x2,     x2,       x4,       x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == ANDI :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_zext, alu_and,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == XORI :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_zext, alu_xor,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLTI :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_slt,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLTIU:cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_sltu, x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLL  :cx = concat( x, x5,  y, rt,  y,  rd,  rd0_sh, rd1_rf,   alu_sll,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SRL  :cx = concat( x, x5,  y, rt,  y,  rd,  rd0_sh, rd1_rf,   alu_srl,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SRA  :cx = concat( x, x5,  y, rt,  y,  rd,  rd0_sh, rd1_rf,   alu_sra,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLLV :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_sll,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SRLV :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_srl,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SRAV :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_sra,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SUBU :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_sub,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == AND  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_and,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == OR   :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_or,   x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == XOR  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_xor,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == NOR  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_nor,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLT  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_slt,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == SLTU :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   alu_sltu, x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == MUL  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   x4,       y,  md_mul,  md,    x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == DIV  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   x4,       y,  md_div,  md,    x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == DIVU :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   x4,       y,  md_divu, md,    x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == REM  :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   x4,       y,  md_rem,  md,    x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == REMU :cx = concat( y, rs,  y, rt,  y,  rd,  rd0_rf, rd1_rf,   x4,       y,  md_remu, md,    x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == LB   :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_lw, byte_, sbyte,  wr_mem, x,  x5,   x  )
      elif s.inst == LBU  :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_lw, byte_, ubyte,  wr_mem, x,  x5,   x  )
      elif s.inst == LH   :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_lw, hword, shword, wr_mem, x,  x5,   x  )
      elif s.inst == LHU  :cx = concat( y, rs,  x, x5,  y,  rt,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_lw, hword, uhword, wr_mem, x,  x5,   x  )
      elif s.inst == SB   :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_sw, byte_, x3,     x,      x,  x5,   x  )
      elif s.inst == SH   :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_sext, alu_add,  x,  x3,      alu,   mem_en, mem_sw, hword, x3,     x,      x,  x5,   x  )
      elif s.inst == J    :cx = concat( x, x5,  x, x5,  x,  x5,  x2,     x2,       x4,       x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == JALR :cx = concat( y, rs,  x, x5,  y,  rd,  rd0_0,  rd1_pc4,  alu_add,  x,  x3,      alu,   x,      x,      x2,    x3,     wr_alu, x,  x5,   x  )
      elif s.inst == BEQ  :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_xor,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == BLEZ :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_sub,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == BGTZ :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_sub,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == BLTZ :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_sub,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == BGEZ :cx = concat( y, rs,  y, rt,  x,  x5,  rd0_rf, rd1_rf,   alu_sub,  x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )
      elif s.inst == MTC2 :cx = concat( x, x5,  y, rt,  x,  x5,  x2,     rd1_rf,   x4,       x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  rd,   y  )
      elif s.inst == MFC2 :cx = concat( x, x5,  x, x5,  y,  rd,  x2,     x2,       x4,       x,  x3,      x,     x,      x,      x2,    x3,     x,      x,  x5,   x  )

      # Unsupported Inst Type
      else:
        assert False

      s.cs.value = cx
