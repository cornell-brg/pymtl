#=======================================================================
# RegisterFile.py
#=======================================================================

from pymtl import *

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( Model ):

  def __init__( s, dtype = Bits(32), nregs = 32, rd_ports = 1, wr_ports = 1,
                   const_zero=False ):

    addr_nbits  = clog2( nregs )

    s.rd_addr  = [ InPort ( addr_nbits ) for _ in range(rd_ports) ]
    s.rd_data  = [ OutPort( dtype )      for _ in range(rd_ports) ]

    if wr_ports == 1:
      s.wr_addr  = InPort( addr_nbits )
      s.wr_data  = InPort( dtype )
      s.wr_en    = InPort( 1 )
    else:
      s.wr_addr  = [ InPort( addr_nbits ) for _ in range(wr_ports) ]
      s.wr_data  = [ InPort( dtype )      for _ in range(wr_ports) ]
      s.wr_en    = [ InPort( 1 )          for _ in range(wr_ports) ]

    s.regs = [ Wire( dtype ) for _ in range( nregs ) ]

    #-------------------------------------------------------------------
    # Combinational read logic
    #-------------------------------------------------------------------
    @s.combinational
    def comb_logic():

      for i in range( rd_ports ):
        assert s.rd_addr[i] < nregs
        s.rd_data[i].value = s.regs[ s.rd_addr[i] ]

    # Select write logic depending on if this register file should have
    # a constant zero register or not!

    #-------------------------------------------------------------------
    # Sequential write logic, single write port
    #-------------------------------------------------------------------
    if wr_ports == 1 and not const_zero:

      @s.posedge_clk
      def seq_logic():
        if s.wr_en:
          s.regs[ s.wr_addr ].next = s.wr_data

    #-------------------------------------------------------------------
    # Sequential write logic, single write port, constant zero
    #-------------------------------------------------------------------
    elif wr_ports == 1:

      @s.posedge_clk
      def seq_logic_const_zero():
        if s.wr_en and s.wr_addr != 0:
          s.regs[ s.wr_addr ].next = s.wr_data

    #-------------------------------------------------------------------
    # Sequential write logic, multiple write ports
    #-------------------------------------------------------------------
    elif not const_zero:

      @s.posedge_clk
      def seq_logic_multiple_wr():
        for i in range( wr_ports ):
          if s.wr_en[i]:
            s.regs[ s.wr_addr[i] ].next = s.wr_data[i]

    #-------------------------------------------------------------------
    # Sequential write logic, multiple write ports, constant zero
    #-------------------------------------------------------------------
    else:

      @s.posedge_clk
      def seq_logic_multiple_wr():
        for i in range( wr_ports ):
          if s.wr_en[i] and s.wr_addr[i] != 0:
            s.regs[ s.wr_addr[i] ].next = s.wr_data[i]


  def line_trace( s ):
    return [x.uint() for x in s.regs]

