#=======================================================================
# SRAMs.py
#=======================================================================
# Collection of various SRAM models.

from pymtl     import *
from pclib.rtl import Reg

#-----------------------------------------------------------------------
# SRAMBitsComb_rst_1rw
#-----------------------------------------------------------------------
# Single Ported SRAM model with s.combinational reads and synchronous
# writes and a reset value. Modeled using flip-flops. SRAM model is
# parameterized with parameters for number of entries, number of bits
# for each entry and the default reset value.
#
# The behavior of a s.combinational SRAM is very similar to that of the
# register file. The read and write operations are as below:
#
# Read Operation
# --------------
#
# For read operations, the address at the input port must be set to the
# address of the location we intend to read and the write enable must
# set low during a given cycle. The data is read out s.combinationally
# in the same cycle. The read data is undefined if the write enable is
# set high and we model this by setting it to value zero.
#
# Write Operation
# ---------------
#
# For write operations, the address at the input port is set to the
# address of the memory cells we intend to write to along with the write
# data and the write enable is set high during a given cycle. The write
# operation takes place at the end of the cycle.
#
# Note: Real SRAM cells do not model the reset value.
#
class SRAMBitsComb_rst_1rw( Model ):

  def __init__( s, num_entries, data_nbits, reset_value = 0 ):

    addr_nbits    = clog2( num_entries )
    s.reset_value = reset_value
    s.num_entries = num_entries
    s.data_nbits  = data_nbits

    s.wen         = InPort  ( 1 )            # Write enable
    s.addr        = InPort  ( addr_nbits )   # Address
    s.wdata       = InPort  ( data_nbits )   # Write data
    s.rdata       = OutPort ( data_nbits )   # Read  data

    # Memory array

    s.mem         = [ Wire( data_nbits ) for x in xrange( num_entries ) ]

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():

      if ~s.wen: s.rdata.value = s.mem[ s.addr ]
      else:      s.rdata.value = 0

    @s.posedge_clk
    def seq_logic():

      if   s.reset:
        for i in xrange( s.num_entries ):
          s.mem[ i ].next = s.reset_value
      elif s.wen:
        s.mem[ s.addr ].next = s.wdata

#-----------------------------------------------------------------------
# SRAMBytesComb_rst_1rw
#-----------------------------------------------------------------------
# Single Ported SRAM model with s.combinational reads and synchronous
# writes and a reset value. Modeled using flip-flops. SRAM model is
# parameterized with parameters for number of entries, number of bytes
# for each entry and the default reset value.
#
# The behavior of a s.combinational SRAM is very similar to that of the
# register file. The read and write operations are as below:
#
# Read Operation
# --------------
#
# For read operations, the address at the input port must be set to the
# address of the location we intend to read and the write enable must
# set low during a given cycle. The data is read out s.combinationally
# in the same cycle. The read data is undefined if the write enable is
# set high and we model this by setting it to value zero.
#
# Write Operation
# ---------------
#
# For write operations, the address at the input port is set to the
# address of the memory cells we intend to write to along with the write
# data, write byte enables and the write enable is set high during a
# given cycle.  The write operation takes place at the end of the cycle.
#
# Note: Real SRAM cells do not model the reset value.
#
class SRAMBytesComb_rst_1rw( Model ):

  def __init__( s, num_entries, num_nbytes, reset_value = 0 ):

    addr_nbits    = clog2( num_entries )
    s.reset_value = reset_value
    s.num_entries = num_entries
    s.num_nbytes  = num_nbytes
    s.data_nbits  = num_nbytes*8

    s.wen         = InPort  ( 1 )              # Write enable
    s.wben        = InPort  ( s.num_nbytes )   # Write byte enable
    s.addr        = InPort  ( addr_nbits   )   # Address
    s.wdata       = InPort  ( s.data_nbits )   # Write data
    s.rdata       = OutPort ( s.data_nbits )   # Read  data

    # Memory array

    s.mem = [ Wire( s.data_nbits ) for x in xrange( num_entries ) ]

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():

      if ~s.wen: s.rdata.value = s.mem[ s.addr ]
      else:      s.rdata.value = 0

    @s.posedge_clk
    def seq_logic():

      if  s.reset:
        for i in xrange( s.num_entries ):
          s.mem[i].next = s.reset_value

      elif s.wen:
        for i in xrange( s.num_nbytes ):
          if s.wben[i]:
            s.mem[s.addr][i*8:i*8+8].next = s.wdata[i*8:i*8+8]

#-----------------------------------------------------------------------
# SRAMBitsSync_rst_1rw
#-----------------------------------------------------------------------
# Single Ported SRAM model with synchronous reads and synchronous writes
# and a reset value. SRAM model is parameterized with parameters for
# number of entries, number of bits for each entry and the default reset
# value.
#
# Synchronous SRAMs register the input control signals and the write
# data before begining the read or write operations. This is modeled by
# input registering the control signals and the write data with the
# acutal SRAM memory cells being modeled by the s.combinational SRAM
# model.
#
# For more details refer to IBM Application Note on "Understanding
# Static RAM Operation"
#
# Note: Real SRAM cells do not model the reset value.
#
class SRAMBitsSync_rst_1rw( Model ):

  def __init__( s, num_entries, data_nbits, reset_value = 0 ):

    s.addr_nbits  = clog2( num_entries )
    s.reset_value = reset_value
    s.num_entries = num_entries
    s.data_nbits  = data_nbits

    s.wen    = InPort  ( 1 )               # Write enable
    s.addr   = InPort  ( s.addr_nbits  )   # Address
    s.wdata  = InPort  ( s.data_nbits  )   # Write data
    s.rdata  = OutPort ( s.data_nbits  )   # Read  data

  def elaborate_logic( s ):

    # input register wen, addr, wdata

    s.wen_reg   = Reg( 1 )
    s.connect( s.wen_reg.in_,   s.wen   )

    s.addr_reg  = Reg( s.addr_nbits )
    s.connect( s.addr_reg.in_,  s.addr  )

    s.wdata_reg = Reg( s.data_nbits )
    s.connect( s.wdata_reg.in_, s.wdata )

    # instantiate a s.combinational SRAM

    s.SRAM = m = SRAMBitsComb_rst_1rw( s.num_entries, s.data_nbits,
                                       reset_value = s.reset_value )
    s.connect_dict({
      m.wen    : s.wen_reg.out,
      m.addr   : s.addr_reg.out,
      m.wdata  : s.wdata_reg.out,
      m.rdata  : s.rdata
    })

#-----------------------------------------------------------------------
# SRAMBytesSync_rst_1rw
#-----------------------------------------------------------------------
# Single Ported SRAM model with synchronous reads and synchronous writes
# and a reset value. SRAM model is parameterized with parameters for
# number of entries, number of bytes for each entry and the default
# reset value.
#
# Synchronous SRAMs register the input control signals and the write
# data before begining the read or write operations. This is modeled by
# input registering the control signals and the write data with the
# acutal SRAM memory cells being modeled by the s.combinational SRAM
# model.
#
# For more details refer to IBM Application Note on "Understanding
# Static RAM Operation"
#
# Note: Real SRAM cells do not model the reset value.
#
class SRAMBytesSync_rst_1rw( Model ):

  def __init__( s, num_entries, num_nbytes, reset_value = 0 ):

    s.addr_nbits  = clog2( num_entries )
    s.reset_value = reset_value
    s.num_entries = num_entries
    s.num_nbytes  = num_nbytes
    s.data_nbits  = num_nbytes*8

    s.wen    = InPort  ( 1 )              # Write enable
    s.wben   = InPort  ( s.num_nbytes )   # Write byte enable
    s.addr   = InPort  ( s.addr_nbits )   # Address
    s.wdata  = InPort  ( s.data_nbits )   # Write data
    s.rdata  = OutPort ( s.data_nbits )   # Read  data

  def elaborate_logic( s ):

    # input register wen, wben, addr, wdata

    s.wen_reg   = Reg( 1 )
    s.connect( s.wen_reg.in_,   s.wen   )

    s.wben_reg  = Reg( s.num_nbytes )
    s.connect( s.wben_reg.in_,  s.wben  )

    s.addr_reg  = Reg( s.addr_nbits )
    s.connect( s.addr_reg.in_,  s.addr  )

    s.wdata_reg = Reg( s.data_nbits )
    s.connect( s.wdata_reg.in_, s.wdata )

    # instantiate a s.combinational SRAM

    s.SRAM = m = SRAMBytesComb_rst_1rw( s.num_entries, s.num_nbytes,
                                        reset_value = s.reset_value )
    s.connect_dict({
      m.wen    : s.wen_reg.out,
      m.wben   : s.wben_reg.out,
      m.addr   : s.addr_reg.out,
      m.wdata  : s.wdata_reg.out,
      m.rdata  : s.rdata
    })
