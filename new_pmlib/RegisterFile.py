#=======================================================================
# RegisterFile.py
#=======================================================================

from new_pymtl import *

#=======================================================================
# RegisterFile
#=======================================================================
class RegisterFile( Model ):

  #---------------------------------------------------------------------
  # elaborate_logic()
  #---------------------------------------------------------------------
  def __init__( s, nbits=32, nregs=32, rd_ports=1, const_zero=False ):

    s.rd_ports   = rd_ports
    s.nregs      = nregs
    s.nbits      = nbits
    s.const_zero = const_zero

    addr_bits  = get_sel_nbits( nregs )

    s.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    s.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]
    s.wr_addr  = InPort( addr_bits )
    s.wr_data  = InPort( nbits )
    s.wr_en    = InPort( 1 )

  #---------------------------------------------------------------------
  # elaborate_logic()
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.regs     = [ Wire( s.nbits ) for x in xrange( s.nregs ) ]

    #-------------------------------------------------------------------
    # Combinational read logic
    #-------------------------------------------------------------------
    @s.combinational
    def comb_logic():

      for i in xrange( s.rd_ports ):
        assert s.rd_addr[i] < s.nregs
        s.rd_data[i].value = s.regs[ s.rd_addr[i] ]

    # Select write logic depending on if this register file should have
    # a constant zero register or not!

    #-------------------------------------------------------------------
    # Sequential write logic
    #-------------------------------------------------------------------
    if not s.const_zero:
      @s.posedge_clk
      def seq_logic():
        if s.wr_en:
          s.regs[ s.wr_addr ].next = s.wr_data

    #-------------------------------------------------------------------
    # Sequential write logic with constant zero
    #-------------------------------------------------------------------
    else:
      @s.posedge_clk
      def seq_logic_const_zero():
        if s.wr_en and s.wr_addr != 0:
          s.regs[ s.wr_addr ].next = s.wr_data

    # TODO: this won't simulate correctly when translated/verilated!!!
    #       mismatch between Verilog and PyMTL sim semantics...
    #waddr = s.wr_addr.value.uint()
    #assert waddr < s.nregs
    #s.regs[ waddr ].next = s.wr_data.value

  def line_trace( s ):
    return [x.uint() for x in s.regs]

