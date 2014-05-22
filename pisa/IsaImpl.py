#=========================================================================
# IsaImpl
#=========================================================================
# This is an implementation class for simplifying the construction of
# instruction classes used in PyMTL modeling. Eventually, we might be
# able to refactor even more boilerplate into this class.
#
# This class is meant to be instantiated and used from within a concrete
# instruction class. In addition to the instruction class, we also need
# to define an encoding table and functions for assembling and
# disassembling instruction fields. See PisaInst for an example of how to
# use this class.
#
# Author : Christopher Batten
# Date   : May 16, 2014

from new_pymtl import Bits
from string import translate,maketrans

class IsaImpl (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, nbits, inst_encoding_table, inst_fields ):

    self.nbits                   = 32
    self.inst_encoding_table     = inst_encoding_table
    self.asm_field_funcs_dict    = {}
    self.disasm_field_funcs_dict = {}
    self.opcode_match_dict       = {}

    for row in inst_encoding_table:

      # Extract the columns from the row

      inst_tmpl    = row[0]
      opcode_mask  = row[1]
      opcode_match = row[2]

      # Extract instruction name from string template

      (inst_name,sep,inst_tmpl) = inst_tmpl.partition(' ')

      # Add opcode match to the a dictionary using the instruction
      # name as the key

      self.opcode_match_dict[ inst_name ] = opcode_match

      # Split the remainder of the template into field strings. First we
      # translate non-whitespace deliminters into whitespace so that we
      # can use split.

      translation_table = maketrans(",()","   ")
      inst_field_tags = translate(inst_tmpl,translation_table).split()

      # Create the list of asm field functions

      asm_field_funcs = []
      for asm_field_tag in inst_field_tags:
        asm_field_funcs.append( inst_fields[asm_field_tag][0] )

      # Add the list of asm field functions to the encoding

      self.asm_field_funcs_dict[ inst_name ] = asm_field_funcs

      # Create the list of disasm field functions

      disasm_field_funcs = {}
      for asm_field_tag in inst_field_tags:
        disasm_field_funcs[ asm_field_tag ] = inst_fields[asm_field_tag][1]

      # Add the list of disasm field functions to the encoding

      self.disasm_field_funcs_dict[ inst_name ] = disasm_field_funcs

  #-----------------------------------------------------------------------
  # decode_tmpl
  #-----------------------------------------------------------------------
  # For now this is O(n) where n is the number of instructions in the
  # encoding table. Obviously, this is pretty slow. I am sure we can do
  # better by creating some kind of tree-based data structure.

  def decode_tmpl( self, inst_bits ):

    for row in self.inst_encoding_table:

      # Extract the columns from the row

      inst_tmpl    = row[0]
      opcode_mask  = row[1]
      opcode_match = row[2]

      # If match, then return instruction name

      if (inst_bits & opcode_mask) == opcode_match:
        return inst_tmpl

    # Illegal instruction

    raise AssertionError( "Illegal instruction {}!".format( inst_bits ) )


  #-----------------------------------------------------------------------
  # decode_name
  #-----------------------------------------------------------------------

  def decode_inst_name( self, inst_bits ):

    # Decode template

    inst_tmpl = self.decode_tmpl( inst_bits )

    # Extract instruction name

    return inst_tmpl.partition(' ')[0]

  #-----------------------------------------------------------------------
  # assemble_inst
  #-----------------------------------------------------------------------

  def assemble_inst( self, sym, pc, inst_str ):

    # Extract instruction name from asm string

    (inst_name,sep,inst_str) = inst_str.partition(' ')

    # Use the instruction name to get the opcode match which we can
    # the use to initialize the instruction bits

    inst_bits = Bits( self.nbits, self.opcode_match_dict[ inst_name ] )

    # Split the remainder of the asm string into field strings. First
    # we translate non-whitespace deliminters into whitespace so that
    # we can use split.

    translation_table = maketrans(",()","   ")
    asm_field_strs = translate(inst_str,translation_table).split()

    # Retrieve the list of asm field functions for this instruction

    asm_field_funcs = self.asm_field_funcs_dict[ inst_name ]

    # Apply these asm field functions to the asm field strings

    for asm_field_str, asm_field_func in zip( asm_field_strs, asm_field_funcs ):
      asm_field_func( inst_bits, sym, pc, asm_field_str )

    # Return the assembled instruction

    return inst_bits

  #-----------------------------------------------------------------------
  # disassemble_inst
  #-----------------------------------------------------------------------

  def disassemble_inst( self, inst_bits ):

    # Decode the instruction to find instruction template

    inst_tmpl = self.decode_tmpl( inst_bits )

    # Extract instruction name from asm template

    inst_name = inst_tmpl.partition(' ')[0]

    # Retrieve the list of disasm field functions for this instruction

    disasm_field_funcs = self.disasm_field_funcs_dict[ inst_name ]

    # Apply these asm field functions to create the disasm string

    inst_str = inst_tmpl
    for inst_field_tag,disasm_field_func in disasm_field_funcs.iteritems():
      field_str = disasm_field_func( inst_bits )
      inst_str = inst_str.replace( inst_field_tag, field_str )

    # Return the disassembled instruction

    return inst_str

