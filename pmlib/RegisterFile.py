#=========================================================================
# Register File
#=========================================================================

from pymtl import *

import math

class RegisterFile( Model ):

  @capture_args
  def __init__( self, nbits = 32, nregs = 32, rd_ports = 1 ):

    self.rd_ports = rd_ports
    self.nregs    = nregs
    addr_bits     = int( math.ceil( math.log( nregs, 2 ) ) )

    self.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    self.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]
    self.wr_addr  = InPort( addr_bits )
    self.wr_data  = InPort( nbits )
    self.wr_en    = InPort( 1 )

    self.regs     = [ Wire( nbits ) for x in xrange( nregs ) ]

  @combinational
  def comb_logic( self ):
    for i in xrange( self.rd_ports ):
      # TODO: complains if no uint, list indices must be integers.
      #       How do we make this translatable?
      raddr = self.rd_addr[i].value.uint
      assert raddr < self.nregs
      self.rd_data[i].value = self.regs[ raddr ].value

  @posedge_clk
  def seq_logic( self ):
    if self.wr_en.value:
      waddr = self.wr_addr.value.uint
      assert waddr < self.nregs
      # TODO: will this translate and synthesize to what we want?
      #       Or does the read need to have this check?
      self.regs[ waddr ].next = self.wr_data.value

  def line_trace( self ):
    return [x.value.uint for x in self.regs]

