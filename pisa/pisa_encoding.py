#=========================================================================
# pisa_encoding
#=========================================================================
# This module encapsulates the encoding of PISA and includes
# assembly/disassembly functions. We first define a PISA encoding table
# which includes instruction templates and opcode mask/match bits. We
# then define assembly/dissassembly functions for each field. Finally, we
# use the encoding table and assembly/disassembly field functions to
# create the assembly/disassembly instructions for single instructions
# and as well as for small programs.
#
# Author : Christopher Batten
# Date   : May 16, 2014

import struct

from pymtl         import Bits

from IsaImpl           import IsaImpl
from SparseMemoryImage import SparseMemoryImage

#=========================================================================
# Encoding Table
#=========================================================================
# There should be one row in the table for each instruction. The row
# should have three columns corresponding to: instruction template,
# opcode mask, and opcode match. The instructino template should start
# with the instruction name and a list of field tags deliminted by
# whitespace, commas, and/or parentheses. The field tags should map to
# assemble_field and disasm_field functions below. The instruction
# template is used both for assembly and disassembly. The opcode
# mask/match columns are used for decoding; effectively an encoded
# instruction is tested against each entry in the table by first applying
# the mask and then checking for a match.

pisa_encoding_table = \
[

  # Basic instructions

  [ "mfc0  rt, rc0",           0xffe007ff, 0x40000000 ],
  [ "mtc0  rt, rc0",           0xffe007ff, 0x40800000 ],
  [ "nop",                      0xffffffff, 0x00000000 ],

  # Register-register arithmetic, logical, and comparison instructions

  [ "addu  rd, rs, rt",        0xfc0007ff, 0x00000021 ],
  [ "subu  rd, rs, rt",        0xfc0007ff, 0x00000023 ],
  [ "and   rd, rs, rt",        0xfc0007ff, 0x00000024 ],
  [ "or    rd, rs, rt",        0xfc0007ff, 0x00000025 ],
  [ "xor   rd, rs, rt",        0xfc0007ff, 0x00000026 ],
  [ "nor   rd, rs, rt",        0xfc0007ff, 0x00000027 ],
  [ "slt   rd, rs, rt",        0xfc0007ff, 0x0000002a ],
  [ "sltu  rd, rs, rt",        0xfc0007ff, 0x0000002b ],

  # Register-immediate arithmetic, logical, and comparison instructions

  [ "addiu rt, rs, imm_sext",  0xfc000000, 0x24000000 ],
  [ "andi  rt, rs, imm_zext",  0xfc000000, 0x30000000 ],
  [ "ori   rt, rs, imm_zext",  0xfc000000, 0x34000000 ],
  [ "xori  rt, rs, imm_zext",  0xfc000000, 0x38000000 ],
  [ "slti  rt, rs, imm_sext",  0xfc000000, 0x28000000 ],
  [ "sltiu rt, rs, imm_sext",  0xfc000000, 0x2c000000 ],

  # Shift instructions

  [ "sll   rd, rt, shamt",     0xffe0003f, 0x00000000 ],
  [ "srl   rd, rt, shamt",     0xffe0003f, 0x00000002 ],
  [ "sra   rd, rt, shamt",     0xffe0003f, 0x00000003 ],
  [ "sllv  rd, rt, rs",        0xfc0007ff, 0x00000004 ],
  [ "srlv  rd, rt, rs",        0xfc0007ff, 0x00000006 ],
  [ "srav  rd, rt, rs",        0xfc0007ff, 0x00000007 ],

  # Other instructions

  [ "lui   rt, imm_zext",      0xffe00000, 0x3c000000 ],

  # Multiply/divide instructions

  [ "mul   rd, rs, rt",        0xfc0007ff, 0x70000002 ],
  [ "div   rd, rs, rt",        0xfc0007ff, 0x9c000005 ],
  [ "divu  rd, rs, rt",        0xfc0007ff, 0x9c000007 ],
  [ "rem   rd, rs, rt",        0xfc0007ff, 0x9c000006 ],
  [ "remu  rd, rs, rt",        0xfc0007ff, 0x9c000008 ],

  # Load instructions

  [ "lw    rt, imm_sext(rs)",  0xfc000000, 0x8c000000 ],
  [ "lh    rt, imm_sext(rs)",  0xfc000000, 0x84000000 ],
  [ "lhu   rt, imm_sext(rs)",  0xfc000000, 0x94000000 ],
  [ "lb    rt, imm_sext(rs)",  0xfc000000, 0x80000000 ],
  [ "lbu   rt, imm_sext(rs)",  0xfc000000, 0x90000000 ],

  # Store instructions

  [ "sw    rt, imm_sext(rs)",  0xfc000000, 0xac000000 ],
  [ "sh    rt, imm_sext(rs)",  0xfc000000, 0xa4000000 ],
  [ "sb    rt, imm_sext(rs)",  0xfc000000, 0xa0000000 ],

  # Unconditional jump instructions

  [ "j     jtarg",             0xfc000000, 0x08000000 ],
  [ "jal   jtarg",             0xfc000000, 0x0c000000 ],
  [ "jr    rs",                0xfc1fffff, 0x00000008 ],
  [ "jalr  rd, rs",            0xfc1f07ff, 0x00000009 ],

  # Conditional branch instructions

  [ "beq   rs, rt, imm_btarg", 0xfc000000, 0x10000000 ],
  [ "bne   rs, rt, imm_btarg", 0xfc000000, 0x14000000 ],
  [ "blez  rs, imm_btarg",     0xfc1f0000, 0x18000000 ],
  [ "bgtz  rs, imm_btarg",     0xfc1f0000, 0x1c000000 ],
  [ "bltz  rs, imm_btarg",     0xfc1f0000, 0x04000000 ],
  [ "bgez  rs, imm_btarg",     0xfc1f0000, 0x04010000 ],

  # Accelerator instructions

  [ "mtx   rt, rs, xcel_id",   0xfc00f800, 0x48000000 ],
  [ "mfx   rt, rs, xcel_id",   0xfc00f800, 0x48000800 ],

]

#=========================================================================
# Field Definitions
#=========================================================================
# For each field tag used in the above instruction templates, we need to
# define: (1) a slice object specifying where the field is encoded in the
# instruction; (2) an assembly_field function that takes the instruction
# bits instruction and a string for the field as input and assembles the
# field string into the appropriate bits of the instruction; and (3) a
# disassembly_field function that takes the instruction bits as input,
# extracts the appropriate field, and converts it into a string.

#-------------------------------------------------------------------------
# Define slice for each field
#-------------------------------------------------------------------------

pisa_field_slice_rs      = slice( 21, 26 )
pisa_field_slice_rt      = slice( 16, 21 )
pisa_field_slice_rd      = slice( 11, 16 )
pisa_field_slice_imm     = slice(  0, 16 )
pisa_field_slice_shamt   = slice(  6, 11 )
pisa_field_slice_jtarg   = slice(  0, 26 )
pisa_field_slice_xcel_id = slice(  0, 11 )

pisa_field_slice_opcode = slice( 26, 32 )
pisa_field_slice_func   = slice(  0,  6 )

#-------------------------------------------------------------------------
# rs assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_rs( bits, sym, pc, field_str ):

  # Register specifiers must begin with an "r"
  assert field_str[0] == "r"

  # Register specifier must be between 0 and 31
  reg_specifier = int(field_str.lstrip("r"))
  assert 0 <= reg_specifier <= 31

  bits[ pisa_field_slice_rs ] = reg_specifier

def disassemble_field_rs( bits ):
  return "r{:0>2}".format( bits[ pisa_field_slice_rs ].uint() )

#-------------------------------------------------------------------------
# rt assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_rt( bits, sym, pc, field_str ):

  # Register specifiers must begin with an "r"
  assert field_str[0] == "r"

  # Register specifier must be between 0 and 31
  reg_specifier = int(field_str.lstrip("r"))
  assert 0 <= reg_specifier <= 31

  bits[ pisa_field_slice_rt ] = reg_specifier

def disassemble_field_rt( bits ):
  return "r{:0>2}".format( bits[ pisa_field_slice_rt ].uint() )

#-------------------------------------------------------------------------
# rd assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_rd( bits, sym, pc, field_str ):

  # Register specifiers must begin with an "r"
  assert field_str[0] == "r"

  # Register specifier must be between 0 and 31
  reg_specifier = int(field_str.lstrip("r"))
  assert 0 <= reg_specifier <= 31

  bits[ pisa_field_slice_rd ] = reg_specifier

def disassemble_field_rd( bits ):
  return "r{:0>2}".format( bits[ pisa_field_slice_rd ].uint() )

#-------------------------------------------------------------------------
# rc0 assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_rc0( bits, sym, pc, field_str ):

  # Only allowed register specifiers are mngr2proc and proc2mngr
  assert (field_str == "mngr2proc") or (field_str == "proc2mngr")

  reg_specifier = None
  if field_str == "mngr2proc":
    reg_specifier = 1
  elif field_str == "proc2mngr":
    reg_specifier = 2

  bits[ pisa_field_slice_rd ] = reg_specifier

def disassemble_field_rc0( bits ):
  return "r{:0>2}".format( bits[ pisa_field_slice_rd ].uint() )

#-------------------------------------------------------------------------
# rc2 assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_rc2( bits, sym, pc, field_str ):

  # Register specifiers must begin with an "r"
  assert field_str[0] == "r"

  # Register specifier must be between 0 and 4
  reg_specifier = int(field_str.lstrip("r"))
  assert 0 <= reg_specifier <= 5

  bits[ pisa_field_slice_rd ] = reg_specifier

def disassemble_field_rc2( bits ):
  return "r{:0>2}".format( bits[ pisa_field_slice_rd ].uint() )

#-------------------------------------------------------------------------
# imm_zext assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_imm_zext( bits, sym, pc, field_str ):

  # Check to see if the immediate field derives from a label
  if field_str[0] == "%":
    label_addr = Bits( 32, sym[ field_str[4:-1] ] )

    if field_str.startswith( "%hi[" ):
      imm = label_addr[16:32]
    elif field_str.startswith( "%lo[" ):
      imm = label_addr[0:16]
    else:
      assert False

  else:
    imm = int(field_str,0)

  assert imm < (1 << 16)
  bits[ pisa_field_slice_imm ] = imm

def disassemble_field_imm_zext( bits ):
  return "{:0>4x}".format( bits[ pisa_field_slice_imm ].uint() )

#-------------------------------------------------------------------------
# imm_sext assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_imm_sext( bits, sym, pc, field_str ):
  imm = int(field_str,0)
  if imm > 0:
    assert imm < (1 << 16)
  else:
    assert -imm < (1 << 15)
  bits[ pisa_field_slice_imm ] = imm

def disassemble_field_imm_sext( bits ):
  return "{:0>4x}".format( bits[ pisa_field_slice_imm ].uint() )

#-------------------------------------------------------------------------
# shamt assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_shamt( bits, sym, pc, field_str ):
  shamt = int(field_str,0)
  assert 0 <= shamt <= 31
  bits[ pisa_field_slice_shamt ] = shamt

def disassemble_field_shamt( bits ):
  return "{:0>2x}".format( bits[ pisa_field_slice_shamt ].uint() )

#-------------------------------------------------------------------------
# jtarg assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_jtarg( bits, sym, pc, field_str ):

  if sym.has_key( field_str ):
    jtarg_byte_addr = sym[field_str]
  else:
    jtarg_byte_addr = int(field_str,0)

  bits[ pisa_field_slice_jtarg ] = jtarg_byte_addr >> 2

def disassemble_field_jtarg( bits ):
  return "{:0>7x}".format( bits[ pisa_field_slice_jtarg ].uint() )

#-------------------------------------------------------------------------
# imm_btarg assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_imm_btarg( bits, sym, pc, field_str ):

  if sym.has_key( field_str ):
    btarg_byte_addr = sym[field_str]
  else:
    btarg_byte_addr = int(field_str,0)

  bits[ pisa_field_slice_imm ] = (btarg_byte_addr - pc - 4) >> 2

def disassemble_field_imm_btarg( bits ):
  return "{:0>4x}".format( bits[ pisa_field_slice_imm ].uint() )

#-------------------------------------------------------------------------
# xcel id assembly/disassembly functions
#-------------------------------------------------------------------------

def assemble_field_xcel_id( bits, sym, pc, field_str ):
  xcel_id = int(field_str,0)
  assert 0 <= xcel_id <= 2**10
  bits[ pisa_field_slice_xcel_id ] = xcel_id

def disassemble_field_xcel_id( bits ):
  return "{:0>3x}".format( bits[ pisa_field_slice_xcel_id ].uint() )

#-------------------------------------------------------------------------
# Field Dictionary
#-------------------------------------------------------------------------
# Create a dictionary so we can lookup an assemble field function
# based on the field tag. I imagine we can eventually use some kind of
# Python magic to eliminate this boiler plate code.

pisa_fields = \
{
  "rs"        : [ assemble_field_rs,        disassemble_field_rs        ],
  "rt"        : [ assemble_field_rt,        disassemble_field_rt        ],
  "rd"        : [ assemble_field_rd,        disassemble_field_rd        ],
  "rc0"       : [ assemble_field_rc0,       disassemble_field_rc0       ],
  "rc2"       : [ assemble_field_rc2,       disassemble_field_rc2       ],
  "imm_zext"  : [ assemble_field_imm_zext,  disassemble_field_imm_zext  ],
  "imm_sext"  : [ assemble_field_imm_sext,  disassemble_field_imm_sext  ],
  "shamt"     : [ assemble_field_shamt,     disassemble_field_shamt     ],
  "jtarg"     : [ assemble_field_jtarg,     disassemble_field_jtarg     ],
  "imm_btarg" : [ assemble_field_imm_btarg, disassemble_field_imm_btarg ],
  "xcel_id"   : [ assemble_field_xcel_id,   disassemble_field_xcel_id   ],
}

#=========================================================================
# IsaImpl
#=========================================================================
# We use the encoding table and assembly/disassembly field functions to
# instantiate an IsaImpl objection which we can then use in our
# assembly/disassembly functions.

pisa_isa_impl = IsaImpl( 32, pisa_encoding_table, pisa_fields )

#=========================================================================
# Assemble
#=========================================================================

def assemble_inst( sym, pc, inst_str ):
  return pisa_isa_impl.assemble_inst( sym, pc, inst_str )

def assemble( asm_code ):

  # If asm_code is a single string, then put it in a list to simplify the
  # rest of the logic.

  asm_code_list = asm_code
  if isinstance( asm_code, str ):
    asm_code_list = [ asm_code ]

  # Create a single list of lines

  asm_list = []
  for asm_seq in asm_code_list:
    asm_list.extend( asm_seq.splitlines() )

  # First pass to create symbol table. This is obviously very simplistic.
  # We can maybe make it more robust in the future.

  addr = 0x00000400
  sym  = {}
  for line in asm_list:
    line = line.partition('#')[0]
    line = line.strip()

    if line == "":
      continue

    if line.startswith(".offset"):
      (cmd,sep,addr_str) = line.partition(' ')
      addr = int(addr_str,0)

    elif line.startswith(".data"):
      pass

    else:
      (label,sep,rest) = line.partition(':')
      if sep != "":
        sym[label.strip()] = addr
      else:
        addr += 4

  # Second pass to assemble text section

  asm_list_idx    = 0
  addr            = 0x00000400
  text_bytes      = bytearray()
  mngr2proc_bytes = bytearray()
  proc2mngr_bytes = bytearray()

  for line in asm_list:
    asm_list_idx += 1
    line = line.partition('#')[0]
    line = line.strip()

    if line == "":
      continue

    if line.startswith(".offset"):
      (cmd,sep,addr_str) = line.partition(' ')
      addr = int(addr_str,0)

    elif line.startswith(".data"):
      break

    else:
      if ':' not in line:
        inst_str = line

        # First see if we have either a < or a >

        if '<' in line:
          (temp,sep,value) = line.partition('<')
          bits = Bits( 32, int(value,0) )
          mngr2proc_bytes.extend(struct.pack("<I",bits))
          inst_str = temp

        elif '>' in line:
          (temp,sep,value) = line.partition('>')
          bits = Bits( 32, int(value,0) )
          proc2mngr_bytes.extend(struct.pack("<I",bits))
          inst_str = temp

        bits = assemble_inst( sym, addr, inst_str )
        text_bytes.extend(struct.pack("<I",bits.uint()))
        addr += 4

  # Assemble data section

  data_bytes = bytearray()
  for line in asm_list[asm_list_idx:]:
    line = line.partition('#')[0]
    line = line.strip()

    if line == "":
      continue

    if line.startswith(".offset"):
      (cmd,sep,addr_str) = line.partition(' ')
      addr = int(addr_str,0)

    elif line.startswith(".word"):
      (cmd,sep,value) = line.partition(' ')
      data_bytes.extend(struct.pack("<I",int(value,0)))
      addr += 4

    elif line.startswith(".hword"):
      (cmd,sep,value) = line.partition(' ')
      data_bytes.extend(struct.pack("<H",int(value,0)))
      addr += 2

    elif line.startswith(".byte"):
      (cmd,sep,value) = line.partition(' ')
      data_bytes.extend(struct.pack("<B",int(value,0)))
      addr += 1

  # Construct the corresponding section objects

  text_section = \
    SparseMemoryImage.Section( ".text", 0x0400, text_bytes )

  data_section = SparseMemoryImage.Section( ".data", 0x2000, data_bytes )

  mngr2proc_section = \
    SparseMemoryImage.Section( ".mngr2proc", 0x3000, mngr2proc_bytes )

  proc2mngr_section = \
    SparseMemoryImage.Section( ".proc2mngr", 0x4000, proc2mngr_bytes )

  # Build a sparse memory image

  mem_image = SparseMemoryImage()
  mem_image.add_section( text_section )

  if len(data_section.data) > 0:
    mem_image.add_section( data_section )

  if len(mngr2proc_section.data) > 0:
    mem_image.add_section( mngr2proc_section )

  if len(proc2mngr_section.data) > 0:
    mem_image.add_section( proc2mngr_section )

  return mem_image

#=========================================================================
# Disassemble
#=========================================================================

def disassemble_inst( inst_bits ):
  return pisa_isa_impl.disassemble_inst( inst_bits )

def decode_inst_name( inst ):

  # Originally I was just using this:
  #
  #  return pisa_isa_impl.decode_inst_name( inst_bits )
  #
  # which basically just does a linear search in the encoding table to
  # find a match. Eventually, I think we should figure out a way to
  # automatically turn the encoding table into some kind of fast
  # tree-bsaed search, but for now we just explicitly create a big case
  # statement to do the instruction name decode.

  # Short names

  op   = pisa_field_slice_opcode
  func = pisa_field_slice_func
  rt   = pisa_field_slice_rt
  rs   = pisa_field_slice_rs
  rd   = pisa_field_slice_rd

  inst_name = ""

  if     inst       == 0:        inst_name = "nop"    #  2,
  elif   inst[op]   == 0b001001: inst_name = "addiu"  # 11,
  elif   inst[op]   == 0b001101: inst_name = "ori"    # 13,
  elif   inst[op]   == 0b001111: inst_name = "lui"    # 23,
  elif   inst[op]   == 0b100011: inst_name = "lw"     # 29,
  elif   inst[op]   == 0b101011: inst_name = "sw"     # 34,
  elif   inst[op]   == 0b000011: inst_name = "jal"    # 38,
  elif   inst[op]   == 0b000101: inst_name = "bne"    # 42,
  elif   inst[op]   == 0b010000:                      #
    if   inst[rs]   == 0b00100:  inst_name = "mtc0"   #  1,
    elif inst[rs]   == 0b00000:  inst_name = "mfc0"   #  0,
  elif   inst[op]   == 0b010010:                      #
    if   inst[rd]   == 0b00000:  inst_name = "mtx"    # 47,
    if   inst[rd]   == 0b00001:  inst_name = "mfx"    # 48,
  elif   inst[op]   == 0b000000:                      #
    if   inst[func] == 0b100001: inst_name = "addu"   #  3,
    elif inst[func] == 0b001000: inst_name = "jr"     # 39,
    elif inst[func] == 0b000000: inst_name = "sll"    # 17,
    elif inst[func] == 0b000010: inst_name = "srl"    # 18,
    elif inst[func] == 0b000011: inst_name = "sra"    # 19,
    elif inst[func] == 0b000100: inst_name = "sllv"   # 20,
    elif inst[func] == 0b000110: inst_name = "srlv"   # 21,
    elif inst[func] == 0b000111: inst_name = "srav"   # 22,
    elif inst[func] == 0b100011: inst_name = "subu"   #  4,
    elif inst[func] == 0b100100: inst_name = "and"    #  5,
    elif inst[func] == 0b100101: inst_name = "or"     #  6,
    elif inst[func] == 0b100110: inst_name = "xor"    #  7,
    elif inst[func] == 0b100111: inst_name = "nor"    #  8,
    elif inst[func] == 0b101010: inst_name = "slt"    #  9,
    elif inst[func] == 0b101011: inst_name = "sltu"   # 10,
    elif inst[func] == 0b001001: inst_name = "jalr"   # 40,
  elif   inst[op]   == 0b001100: inst_name = "andi"   # 12,
  elif   inst[op]   == 0b001110: inst_name = "xori"   # 14,
  elif   inst[op]   == 0b001010: inst_name = "slti"   # 15,
  elif   inst[op]   == 0b001011: inst_name = "sltiu"  # 16,
  elif   inst[op]   == 0b011100: inst_name = "mul"    # 24,
  elif   inst[op]   == 0b100111:                      #
    if   inst[func] == 0b000101: inst_name = "div"    # 25,
    elif inst[func] == 0b000111: inst_name = "divu"   # 26,
    elif inst[func] == 0b000110: inst_name = "rem"    # 27,
    elif inst[func] == 0b001000: inst_name = "remu"   # 28,
  elif   inst[op]   == 0b100001: inst_name = "lh"     # 30,
  elif   inst[op]   == 0b100101: inst_name = "lhu"    # 31,
  elif   inst[op]   == 0b100000: inst_name = "lb"     # 32,
  elif   inst[op]   == 0b100100: inst_name = "lbu"    # 33,
  elif   inst[op]   == 0b101001: inst_name = "sh"     # 35,
  elif   inst[op]   == 0b101000: inst_name = "sb"     # 36,
  elif   inst[op]   == 0b000010: inst_name = "j"      # 37,
  elif   inst[op]   == 0b000011: inst_name = "jal"    # 38,
  elif   inst[op]   == 0b000100: inst_name = "beq"    # 41,
  elif   inst[op]   == 0b000110: inst_name = "blez"   # 43,
  elif   inst[op]   == 0b000111: inst_name = "bgtz"   # 44,
  elif   inst[op]   == 0b000001:                      #
    if   inst[rt]   == 0b00000:  inst_name = "bltz"   # 45,
    elif inst[rt]   == 0b00001:  inst_name = "bgez"   # 46,

  if inst_name == "":
    raise AssertionError( "Illegal instruction {}!".format(inst) )

  return inst_name

def disassemble( mem_image ):

  # Get the text section to disassemble

  text_section = mem_image.get_section( ".text" )

  # Iterate through the text section four bytes at a time

  addr = text_section.addr
  asm_code = ""
  for i in xrange(0,len(text_section.data),4):

    print hex(addr+i)

    bits = struct.unpack_from("<I",buffer(text_section.data,i,4))[0]
    inst_str= disassemble_inst( Bits(32,bits) )
    disasm_line = " {:0>8x}  {:0>8x}  {}\n".format( addr+i, bits, inst_str )
    asm_code += disasm_line

  return asm_code

