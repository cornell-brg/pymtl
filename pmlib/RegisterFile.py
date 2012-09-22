#=========================================================================
# Register File
#=========================================================================
# This is a parameterized Register File model with the number of registers,
# bitwidth of registers and read-write ports as parameters. The
# implementation assumes that we can never have conflicts in the read/
# write addresses across all the ports. In other words, we do not handle
# the case when all ports read or write to the same register currently.
# TODO: Needs translation support for port lists and for loop constructs in
# combinational and posedge blocks.

from pymtl import *

import math

class RegisterFile( Model ):

  def __init__( self, nbits = 32, nregs = 32, rd_ports = 1, wr_ports = 1 ):

    self.rd_ports = rd_ports
    self.wr_ports = wr_ports
    self.nregs    = nregs
    addr_bits     = int( math.ceil( math.log( nbits, 2 ) ) )

    self.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    self.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]
    self.wr_addr  = [ InPort( addr_bits ) for x in xrange(wr_ports) ]
    self.wr_data  = [ InPort( nbits )     for x in xrange(wr_ports) ]
    self.wr_en    = [ InPort( 1 )         for x in xrange(wr_ports) ]

    self.regs     = [ Wire( nbits ) for x in xrange( nregs ) ]

  @combinational
  def comb_logic( self ):
    for i in xrange( self.rd_ports ):
      # TODO: complains if no uint, list indices must be integers.
      #       How do we make this translatable?
      addr = self.rd_addr[i].value.uint
      assert addr < self.nregs
      self.rd_data[i].value = self.regs[ addr ].value

  @posedge_clk
  def seq_logic( self ):
    for i in xrange( self.wr_ports ):
      if self.wr_en[i].value:
        addr = self.wr_addr[i].value.uint
        assert addr < self.nregs
        # TODO: will this translate and synthesize to what we want?
        #       Or does the read need to have this check?
        if addr != 0:
          self.regs[ addr ].next = self.wr_data[i].value

  def line_trace( self ):
    return [x.value.uint for x in self.regs]

