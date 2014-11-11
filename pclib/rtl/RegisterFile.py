#=======================================================================
# RegisterFile.py
#=======================================================================

from pymtl import *

#=======================================================================
# RegisterFile
#=======================================================================
class RegisterFile( Model ):

  #---------------------------------------------------------------------
  # elaborate_logic()
  #---------------------------------------------------------------------
  def __init__( s, nbits=32, nregs=32, rd_ports=1, wr_ports=1,
                const_zero=False ):

    s.rd_ports   = rd_ports
    s.wr_ports   = wr_ports
    s.nregs      = nregs
    s.nbits      = nbits
    s.const_zero = const_zero

    addr_bits  = get_sel_nbits( nregs )

    s.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    s.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]

    # TODO: temporary hacky handling for up to 2 write_ports, fix!
    assert wr_ports <= 2
    s.wr_addr  = InPort( addr_bits )
    s.wr_data  = InPort( nbits )
    s.wr_en    = InPort( 1 )
    if wr_ports == 2:
      s.wr_addr2 = InPort( addr_bits )
      s.wr_data2 = InPort( nbits )
      s.wr_en2   = InPort( 1 )

    #if wr_ports == 1:
    #  s.wr_addr  = InPort( addr_bits )
    #  s.wr_data  = InPort( nbits )
    #  s.wr_en    = InPort( 1 )
    #else:
    #  s.wr_addr  = [ InPort( addr_bits ) for x in range(wr_ports) ]
    #  s.wr_data  = [ InPort( nbits )     for x in range(wr_ports) ]
    #  s.wr_en    = [ InPort( 1 )         for x in range(wr_ports) ]

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
    # Sequential write logic, single write port
    #-------------------------------------------------------------------
    if s.wr_ports == 1 and not s.const_zero:

      @s.posedge_clk
      def seq_logic():
        if s.wr_en:
          s.regs[ s.wr_addr ].next = s.wr_data

    #-------------------------------------------------------------------
    # Sequential write logic, single write port, constant zero
    #-------------------------------------------------------------------
    elif s.wr_ports == 1:

      @s.posedge_clk
      def seq_logic_const_zero():
        if s.wr_en and s.wr_addr != 0:
          s.regs[ s.wr_addr ].next = s.wr_data

    #-------------------------------------------------------------------
    # Sequential write logic, multiple write ports
    #-------------------------------------------------------------------
    elif not s.const_zero:

      @s.posedge_clk
      def seq_logic_multiple_wr():
        if s.wr_en:  s.regs[ s.wr_addr ] .next = s.wr_data
        if s.wr_en2: s.regs[ s.wr_addr2 ].next = s.wr_data2

      # TODO: fix translation of this!
      #@s.posedge_clk
      #def seq_logic_multiple_wr():
      #  for i in range( s.wr_ports ):
      #    if s.wr_en[i]:
      #      s.regs[ s.wr_addr[i] ].next = s.wr_data[i]

    #-------------------------------------------------------------------
    # Sequential write logic, multiple write ports, constant zero
    #-------------------------------------------------------------------
    else:

      @s.posedge_clk
      def seq_logic_multiple_wr():
        if s.wr_en  and s.wr_addr  != 0: s.regs[ s.wr_addr  ].next = s.wr_data
        if s.wr_en2 and s.wr_addr2 != 0: s.regs[ s.wr_addr2 ].next = s.wr_data2

      # TODO: fix translation of this!
      #@s.posedge_clk
      #def seq_logic_multiple_wr():
      #  for i in range( s.wr_ports ):
      #    if s.wr_en[i] and s.wr_addr[i] != 0:
      #      s.regs[ s.wr_addr[i] ].next = s.wr_data[i]


  def line_trace( s ):
    return [x.uint() for x in s.regs]

