#=========================================================================
# Register File
#=========================================================================

from new_pymtl import *

import math

class RegisterFile( Model ):

  @capture_args
  def __init__( s, nbits = 32, nregs = 32, rd_ports = 1 ):

    s.nbits = nbits
    s.rd_ports = rd_ports
    s.nregs    = nregs
    addr_bits     = int( math.ceil( math.log( nregs, 2 ) ) )

    s.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    s.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]
    s.wr_addr  = InPort( addr_bits )
    s.wr_data  = InPort( nbits )
    s.wr_en    = InPort( 1 )

  def elaborate_logic( s ):

    s.regs     = [ Wire( s.nbits ) for x in xrange( s.nregs ) ]

    @s.combinational
    def comb_logic():
      for i in xrange( s.rd_ports ):
        # TODO: complains if no uint, list indices must be integers.
        #       How do we make this translatable?
        raddr = s.rd_addr[i].value
        assert raddr < s.nregs
        s.rd_data[i].value = s.regs[ raddr ].value

    @s.posedge_clk
    def seq_logic():
      if s.wr_en.value:

        # TODO: this won't simulate correctly when translated/verilated!!!
        #       mismatch between Verilog and PyMTL sim semantics...
        #waddr = s.wr_addr.value.uint
        #assert waddr < s.nregs
        #s.regs[ waddr ].next = s.wr_data.value

        s.regs[ s.wr_addr.value ].next = s.wr_data.value

    def line_trace( s ):
      return [x.value for x in s.regs]

