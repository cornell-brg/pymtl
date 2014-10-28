#=========================================================================
# PisaInst
#=========================================================================
# This is a concrete instruction class for PISA with methods for
# accessing the various instruction fields.
#
# Author : Christopher Batten
# Date   : May 22, 2014

import pisa_encoding

from pymtl import Bits

class PisaInst (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, inst_bits ):
    self.bits = Bits( 32, inst_bits )

  #-----------------------------------------------------------------------
  # Get instruction name
  #-----------------------------------------------------------------------

  @property
  def name( self ):
    return pisa_encoding.decode_inst_name( self.bits )

  #-----------------------------------------------------------------------
  # Get fields
  #-----------------------------------------------------------------------

  @property
  def rs( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_rs ]

  @property
  def rt( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_rt ]

  @property
  def rd( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_rd ]

  @property
  def imm( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_imm ]

  @property
  def shamt( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_shamt ]

  @property
  def jtarg( self ):
    return self.bits[ pisa_encoding.pisa_field_slice_jtarg ]

  #-----------------------------------------------------------------------
  # to string
  #-----------------------------------------------------------------------

  def __str__( self ):
    return pisa_encoding.disassemble_inst( self.bits )

