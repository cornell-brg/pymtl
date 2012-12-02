#=========================================================================
# Register File
#=========================================================================

from pymtl import *

import math

class RegisterFile( Model ):

  def __init__( self, nbits = 32):

    addr_bits     = 3

    self.rd_addr  = InPort( addr_bits )
    self.rd_data  = OutPort( nbits )
    self.wr_addr  = InPort( addr_bits )
    self.wr_data  = InPort( nbits )
    self.wr_en    = InPort( 1 )

    self.regs0    = Wire( nbits )
    self.regs1    = Wire( nbits )
    self.regs2    = Wire( nbits )
    self.regs3    = Wire( nbits )
    self.regs4    = Wire( nbits )
    self.regs5    = Wire( nbits )
    self.regs6    = Wire( nbits )
    self.regs7    = Wire( nbits )

  @combinational
  def comb_logic( self ):
    if   self.rd_addr.value == 0:
      self.rd_data.value = self.regs0.value
    elif self.rd_addr.value == 1:
      self.rd_data.value = self.regs1.value
    elif self.rd_addr.value == 2:
      self.rd_data.value = self.regs2.value
    elif self.rd_addr.value == 3:
      self.rd_data.value = self.regs3.value
    elif self.rd_addr.value == 4:
      self.rd_data.value = self.regs4.value
    elif self.rd_addr.value == 5:
      self.rd_data.value = self.regs5.value
    elif self.rd_addr.value == 6:
      self.rd_data.value = self.regs6.value
    elif self.rd_addr.value == 7:
      self.rd_data.value = self.regs7.value

  @posedge_clk
  def seq_logic( self ):
    if self.wr_en.value:
      if   self.wr_addr.value == 0:
        self.regs0.next = self.wr_data.value
      elif self.wr_addr.value == 1:
        self.regs1.next = self.wr_data.value
      elif self.wr_addr.value == 2:
        self.regs2.next = self.wr_data.value
      elif self.wr_addr.value == 3:
        self.regs3.next = self.wr_data.value
      elif self.wr_addr.value == 4:
        self.regs4.next = self.wr_data.value
      elif self.wr_addr.value == 5:
        self.regs5.next = self.wr_data.value
      elif self.wr_addr.value == 6:
        self.regs6.next = self.wr_data.value
      elif self.wr_addr.value == 7:
        self.regs7.next = self.wr_data.value

  def line_trace( self ):
    return [self.regs0.value.uint,
            self.regs1.value.uint,
            self.regs2.value.uint,
            self.regs3.value.uint,
            self.regs4.value.uint,
            self.regs5.value.uint,
            self.regs6.value.uint,
            self.regs7.value.uint]

