#=========================================================================
# DirectedMappedWriteBackCacheSync
#=========================================================================
# DirectMappedWriteBackCache using s.combinational reads and synchronous
# writes for the Tag and Data Arrays. Control unit implements a mixed Moore
# and Mealy style FSM.

from   new_pymtl import *
from   new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle
import new_pmlib
from   new_pmlib.queues_rtl   import SingleElementBypassQueue
from   new_pmlib.queues_rtl   import SingleElementSkidQueue
import math
from   SRAMs import SRAMBitsComb_rst_1rw
from   SRAMs import SRAMBitsSync_rst_1rw
from   SRAMs import SRAMBytesSync_rst_1rw

r = Bits(1,0)
w = Bits(1,1)

#-------------------------------------------------------------------------
# DirectMappedWriteBackCacheCtrl
#-------------------------------------------------------------------------
class DirectMappedWriteBackCacheCtrl (Model):

#--- gen-harness : begin cut ---------------------------------------------
  def __init__( s, num_lines ):

    # size cache line index in bits

    s.num_lines = num_lines
    idx_nbits   = int( math.ceil( math.log( num_lines, 2 ) ) )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    s.cachereq_val  = InPort  ( 1 )
    s.cachereq_rdy  = OutPort ( 1 )

    s.cacheresp_val = OutPort ( 1 )
    s.cacheresp_rdy = InPort  ( 1 )

    s.memreq_val    = OutPort ( 1 )
    s.memreq_rdy    = InPort  ( 1 )

    s.memresp_val   = InPort  ( 1 )
    s.memresp_rdy   = OutPort ( 1 )

    #---------------------------------------------------------------------
    # Control Signals (ctrl -> dpath)
    #---------------------------------------------------------------------

    s.cachereq_enq_val = OutPort ( 1 )
    s.cachereq_deq_rdy = OutPort ( 1 )

    s.cacheresp_enq_val = OutPort ( 1 )
    s.cacheresp_deq_rdy = OutPort ( 1 )

    s.cachereq_en     = OutPort ( 1 )
    s.memresp_en      = OutPort ( 1 )
    s.wr_shamt        = OutPort ( 5 )
    s.tag_array_wen   = OutPort ( 1 )
    s.is_refill       = OutPort ( 1 )
    s.is_search       = OutPort ( 1 )
    s.data_array_wen  = OutPort ( 1 )
    s.data_array_wben = OutPort ( 16 )
    s.memreq_type     = OutPort ( 1 )
    s.word_offset     = OutPort ( 2 )
    s.rd_shamt        = OutPort ( 5 )
    s.cacheresp_type  = OutPort ( 1 )
    s.cacheresp_len   = OutPort ( 2 )

    #---------------------------------------------------------------------
    # Status Signals (ctrl <- dpath)
    #---------------------------------------------------------------------

    s.valid_idx       = InPort ( idx_nbits )
    s.dirty_idx       = InPort ( idx_nbits )
    s.cachereq_type   = InPort ( 1 )
    s.cachereq_len    = InPort ( 2 )
    s.cachereq_off    = InPort ( 4 )
    s.cachereq_off_h  = InPort ( 4 )
    s.tag_match       = InPort ( 1 )

    s.cachereq_enq_rdy = InPort ( 1 )
    s.cachereq_deq_val = InPort ( 1 )

    s.cacheresp_enq_rdy = InPort ( 1 )
    s.cacheresp_deq_val = InPort ( 1 )

  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Control Unit
    #---------------------------------------------------------------------

    # s.connect cacheresp type and len

    s.connect( s.cacheresp_type, s.cachereq_type )
    s.connect( s.cacheresp_len,  s.cachereq_len  )

    # Valid Bits SRAM

    s.valid_bits = m = SRAMBitsComb_rst_1rw( s.num_lines, 1 )
    s.connect( s.valid_bits.addr, s.valid_idx )

    # Dirty Bits SRAM

    s.dirty_bits = m = SRAMBitsComb_rst_1rw( s.num_lines, 1 )
    s.connect( s.dirty_bits.addr, s.dirty_idx )

    # State Element

    s.ST_NBITS       = 4

    s.ST_IDLE        = 0
    s.ST_TAG_CHECK   = 1
    s.ST_DATA_ACCESS = 2
    s.ST_WAIT        = 3
    s.ST_REFILL_REQ  = 4
    s.ST_REFILL_WAIT = 5
    s.ST_REFILL_DO   = 6
    s.ST_EVICT_REQ   = 7
    s.ST_EVICT_WAIT  = 8

    s.state = new_pmlib.regs.RegRst( s.ST_NBITS,
                                    reset_value = s.ST_IDLE )

    s.match = Wire(1)

    #-----------------------------------------------------------------------
    # State transitions
    #-----------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      current_state = s.state.out
      next_state    = s.state.out

      # Transitions out of IDLE

      if s.state.out == s.ST_IDLE:
        if s.cachereq_val and s.cachereq_enq_rdy:
          next_state = s.ST_TAG_CHECK

      # Transitions out of TAG CHECK

      s.match = s.valid_bits.rdata & s.tag_match
      dirty   = s.dirty_bits.rdata

      if s.state.out == s.ST_TAG_CHECK:
        if   s.match:
          if s.cachereq_type == r:
            if s.cacheresp_enq_rdy:
              if s.cachereq_val:
                next_state = s.ST_TAG_CHECK
              else:
                next_state = s.ST_IDLE
            else:
              next_state = s.ST_TAG_CHECK
          else: #write
            next_state = s.ST_DATA_ACCESS

        elif ~dirty & ~s.match:
          next_state = s.ST_REFILL_REQ
        elif  dirty & ~s.match:
          next_state = s.ST_EVICT_REQ

      # Transitions out of DATA ACCESS

      if s.state.out == s.ST_DATA_ACCESS:
        if s.cacheresp_enq_rdy:
          if s.cachereq_val:
            next_state = s.ST_TAG_CHECK
          else:
            next_state = s.ST_IDLE
        else:
          next_state = s.ST_DATA_ACCESS

      # Transitions out of REFILL REQUEST

      if s.state.out == s.ST_REFILL_REQ:
        if s.memreq_rdy:
          next_state = s.ST_REFILL_WAIT

      # Transitions out of REFILL WAIT

      if s.state.out == s.ST_REFILL_WAIT:
        if s.memresp_val:
          next_state = s.ST_REFILL_DO

      # Transitions out of REFILL DO

      if s.state.out == s.ST_REFILL_DO:
        if s.cachereq_type == r:
          next_state = s.ST_TAG_CHECK
        else:
          next_state = s.ST_DATA_ACCESS

      # Transitions out of EVICT REQUEST

      if s.state.out == s.ST_EVICT_REQ:
        if s.memreq_rdy:
          next_state = s.ST_EVICT_WAIT

      # Transitions out of EVICT WAIT

      if s.state.out == s.ST_EVICT_WAIT:
        if s.memresp_val:
          next_state = s.ST_REFILL_REQ

      s.state.in_.value = next_state

    #-----------------------------------------------------------------------
    # State outputs
    #-----------------------------------------------------------------------

    # State Ouputs

    s.is_match           = Wire( 1 )
    s.cachereq_off_shift = Wire( 5 )

    @s.combinational
    def state_outputs():

      st = s.state.out # Helper Signal
      #c  = s.c        # Helper Function
      # Short Names for Signals

      I  = s.ST_IDLE
      TC = s.ST_TAG_CHECK
      DA = s.ST_DATA_ACCESS
      W  = s.ST_WAIT
      RR = s.ST_REFILL_REQ
      RW = s.ST_REFILL_WAIT
      RD = s.ST_REFILL_DO
      ER = s.ST_EVICT_REQ
      EW = s.ST_EVICT_WAIT

      # Local Constants

      n = Bits(1,0)
      y = Bits(1,1)

      # Write request enable helper signal

      w_h = s.cachereq_type
      # INDEX INTO ARRAY       8    7    6    5     4    3    2     1     0
      #                        creq creq creq cresp mreq mreq mresp valid dirty
      #                        eval en   drdy eval  val  type rdy   wen   wen
      if   st == I :cs=concat( y,   y,   y,   n,    n,   n,   n,    n,    n   )
      elif st == TC:cs=concat( y,   y,   y,   y,    n,   n,   n,    n,    n   )
      elif st == DA:cs=concat( y,   y,   y,   y,    n,   n,   n,    n,    w_h )
      elif st == RR:cs=concat( n,   n,   n,   n,    y,   r,   n,    n,    n   )
      elif st == RW:cs=concat( n,   n,   n,   n,    n,   n,   y,    n,    n   )
      elif st == RD:cs=concat( n,   n,   n,   n,    n,   n,   n,    y,    y   )
      elif st == ER:cs=concat( n,   n,   n,   n,    y,   w,   n,    n,    n   )
      elif st == EW:cs=concat( n,   n,   n,   n,    n,   n,   y,    n,    n   )

      # Moore Output Signals
      s.cachereq_rdy.value      = s.cachereq_enq_rdy;
      s.cacheresp_deq_rdy.value = s.cacheresp_rdy;
      s.cacheresp_val.value     = s.cacheresp_deq_val;

      s.cachereq_enq_val.value  = cs[ 8 ] & s.cachereq_val
      s.cachereq_en.value       = cs[ 7 ]
      s.cachereq_deq_rdy.value  = cs[ 6 ]
      s.cacheresp_enq_val.value = cs[ 5 ]
      s.memreq_val.value        = cs[ 4 ]
      s.memreq_type.value       = cs[ 3 ]
      s.memresp_rdy.value       = cs[ 2 ]
      s.valid_bits.wen.value    = cs[ 1 ]
      s.dirty_bits.wen.value    = cs[ 0 ]

      # Mealy Output Signals

      s.is_match = s.valid_bits.rdata & s.tag_match

      if    s.state.out == s.ST_TAG_CHECK:
        if s.cachereq_type == r:
          if s.is_match:
            if not s.cacheresp_enq_rdy:
              s.cachereq_deq_rdy.value = 0
              s.cachereq_en.value      = 0
          else:
            s.cachereq_deq_rdy.value  = 0
            s.cachereq_en.value       = 0
            s.cacheresp_enq_val.value = 0
        elif s.cachereq_type == w:
          s.cachereq_deq_rdy.value  = 0
          s.cachereq_en.value       = 0
          s.cacheresp_enq_val.value = 0

      elif  s.state.out == s.ST_DATA_ACCESS:
        if not s.cacheresp_enq_rdy:
          s.cachereq_deq_rdy.value = 0
          s.cachereq_en.value      = 0


      if   ( s.state.out == s.ST_REFILL_DO ):
        s.tag_array_wen.value  = 0
        s.data_array_wen.value = w_h
      elif ( s.state.out == s.ST_TAG_CHECK ) & s.is_match:
        s.tag_array_wen.value  = 0
        s.data_array_wen.value = w_h
      elif ( s.state.out == s.ST_REFILL_WAIT ) & s.memresp_val:
        s.tag_array_wen.value  = y
        s.data_array_wen.value = y
      else:
        s.tag_array_wen.value  = n
        s.data_array_wen.value = n

      # valid wdata calculations

      s.valid_bits.wdata.value = ( s.state.out == s.ST_REFILL_DO )

      # dirty wdata calculations

      if   s.state.out == s.ST_DATA_ACCESS:
        s.dirty_bits.wdata.value = s.cachereq_type
      elif s.state.out == s.ST_REFILL_DO:
        s.dirty_bits.wdata.value = 0

      # is_refill calculation

      s.is_refill.value = ( s.state.out == s.ST_REFILL_WAIT )

      # is_search calculation

      s.is_search.value = ( s.state.out == s.ST_IDLE )

      # data array wben, rd_shamt, wr_shamt calculations

      if s.state.out == s.ST_REFILL_WAIT:
        s.data_array_wben.value = 0xffff

      elif s.cachereq_len == 0:

        # for word operations

        s.data_array_wben.value = Bits(16,0b1111) << s.cachereq_off
        s.rd_shamt.value        = 0
        s.wr_shamt.value        = 0

      else:

        # for subword operations

        s.data_array_wben.value = (((Bits(16,1) << s.cachereq_len) - 1)
                                   << s.cachereq_off )
        s.rd_shamt.value        = concat( s.cachereq_off_h[0:2], Bits(3,0) )
        s.wr_shamt.value        = concat( s.cachereq_off[0:2], Bits(3,0) )
        s.wr_shamt.value        = concat( s.cachereq_off[0:2], Bits(3,0) )

      # word_offset

      s.word_offset.value = s.cachereq_off_h[2:4]

#--- gen-harness : end cut ---------------------------------------------

#-------------------------------------------------------------------------
# DirectMappedWriteBackCacheDpath
#-------------------------------------------------------------------------

#--- gen-harness : begin cut ---------------------------------------------
class AddrGen (Model):

  def __init__( s, tag_nbits, idx_nbits, addr_nbits ):

    s.tag_nbits  = tag_nbits
    s.idx_nbits  = idx_nbits
    s.addr_nbits = addr_nbits

    s.tag        = InPort  ( tag_nbits )
    s.idx        = InPort  ( idx_nbits )
    s.addr       = OutPort ( addr_nbits )

    s.idx_start = s.addr_nbits - s.tag_nbits - s.idx_nbits
    s.tag_start = s.addr_nbits - s.tag_nbits

  def elaborate_logic( s ):
    @s.combinational
    def comb():

      s.addr[          0:s. idx_start].value = 0
      s.addr[s.idx_start:s. tag_start].value = s.idx
      s.addr[s.tag_start:s.addr_nbits].value = s.tag

class Replicate (Model):

  def __init__( s, in_nbits, out_nbits ):

    s.in_nbits  = in_nbits
    s.out_nbits = out_nbits

    s.in_       = InPort  ( in_nbits )
    s.out       = OutPort ( out_nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb():
      for i in xrange( s.out_nbits/s.in_nbits ):
        s.out[ i*s.in_nbits : i*s.in_nbits + s.in_nbits ].value = s.in_
#--- gen-harness : end cut ---------------------------------------------

# DirectMappedWriteBackCacheDpath

class DirectMappedWriteBackCacheDpath (Model):

#--- gen-harness : begin cut ---------------------------------------------
  def __init__( s, mem_nbytes, addr_nbits, data_nbits, line_nbits ):

    #---------------------------------------------------------------------
    # Local Constants
    #---------------------------------------------------------------------

    # cache/memory request/response message parameters

    s.addr_nbits = addr_nbits
    s.data_nbits = data_nbits
    s.creq  = new_pmlib.mem_msgs.MemReqParams ( s.addr_nbits, s.data_nbits )
    s.cresp = new_pmlib.mem_msgs.MemRespParams( s.data_nbits )

    s.mreq  = new_pmlib.mem_msgs.MemReqParams ( s.addr_nbits, line_nbits )
    s.mresp = new_pmlib.mem_msgs.MemRespParams( line_nbits )

    # number of bytes in data "word"

    data_nbytes = s.data_nbits / 8

    # number of bytes in cache line

    s.line_nbytes = line_nbits / 8

    # total number of cache lines

    s.num_lines   = mem_nbytes / s.line_nbytes

    # size of byte offset in bits

    off_nbits   = int( math.ceil( math.log( s.line_nbytes, 2 ) ) )

    # size cache line index in bits

    s.idx_nbits   = int( math.ceil( math.log( s.num_lines, 2 ) ) )

    # size of tag in bits

    s.tag_nbits   = s.addr_nbits - s.idx_nbits - off_nbits

    # cache request message slices

    s.creq_off = slice( 0            ,   off_nbits                 )
    s.creq_idx = slice( s.creq_off.stop,   s.idx_nbits + s.creq_off.stop )
    s.creq_tag = slice( s.creq_idx.stop,   s.tag_nbits + s.creq_idx.stop )

    # Constants

    EVICT  = 1
    REFILL = 0

    RD     = s.creq.type_read
    WR     = s.creq.type_write

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # processor to cache request interface

    s.cachereq_msg    = InPort  ( s.creq.nbits )

    # cache to processor response interface

    s.cacheresp_msg   = OutPort ( s.cresp.nbits )

    # cache to memory request interface

    s.memreq_msg      = OutPort ( s.mreq.nbits )

    # memory to cache response interface

    s.memresp_msg     = InPort  ( s.mresp.nbits )

    #---------------------------------------------------------------------
    # Control Signals (ctrl -> dpath)
    #---------------------------------------------------------------------


    s.cachereq_enq_val     = InPort  ( 1 )
    s.cachereq_deq_rdy     = InPort  ( 1 )

    s.cacheresp_enq_val     = InPort  ( 1 )
    s.cacheresp_deq_rdy     = InPort  ( 1 )

    s.cachereq_en     = InPort ( 1 )
    s.memresp_en      = InPort ( 1 )
    s.wr_shamt        = InPort ( 5 )
    s.tag_array_wen   = InPort ( 1 )
    s.is_refill       = InPort ( 1 )
    s.is_search       = InPort ( 1 )
    s.data_array_wen  = InPort ( 1 )
    s.data_array_wben = InPort ( 16 )
    s.memreq_type     = InPort ( 1 )
    s.word_offset     = InPort ( 2 )
    s.rd_shamt        = InPort ( 5 )
    s.cacheresp_type  = InPort ( 1 )
    s.cacheresp_len   = InPort ( 2 )

    #---------------------------------------------------------------------
    # Status Signals (ctrl <- dpath)
    #---------------------------------------------------------------------

    s.valid_idx       = OutPort ( s.idx_nbits )
    s.dirty_idx       = OutPort ( s.idx_nbits )
    s.cachereq_type   = OutPort ( 1 )
    s.cachereq_len    = OutPort ( 2 )
    s.cachereq_off    = OutPort ( 4 )
    s.cachereq_off_h  = OutPort ( 4 )
    s.tag_match       = OutPort ( 1 )

    s.cachereq_enq_rdy     = OutPort ( 1 )
    s.cachereq_deq_val     = OutPort ( 1 )

    s.cacheresp_enq_rdy     = OutPort ( 1 )
    s.cacheresp_deq_val     = OutPort ( 1 )

  def elaborate_logic( s ):

    SEARCH = 1
    ACCESS = 0

    #---------------------------------------------------------------------
    # Datapath
    #---------------------------------------------------------------------

    s.cachereq_queue_out = Wire(s.creq.nbits)
    # cachereq_queue
    s.cachereq_queue = m = SingleElementSkidQueue(s.creq.nbits)
    s.connect_dict({
      m.enq.val : s.cachereq_enq_val,
      m.enq.rdy : s.cachereq_enq_rdy,
      m.enq.msg : s.cachereq_msg,

      m.deq.rdy : s.cachereq_deq_rdy,
      m.deq.val : s.cachereq_deq_val,
      m.deq.msg : s.cachereq_queue_out
    })

    #cacheresp_queue
    s.cacheresp_queue = m = SingleElementBypassQueue(s.cresp.nbits)
    s.connect_dict({
      m.enq.val : s.cacheresp_enq_val,
      m.enq.rdy : s.cacheresp_enq_rdy,

      m.deq.msg : s.cacheresp_msg,
      m.deq.rdy : s.cacheresp_deq_rdy,
      m.deq.val : s.cacheresp_deq_val
    })

    #hold register
    s.cachereq_hold_reg = m = new_pmlib.regs.RegEn( s.creq.nbits )
    s.connect_dict({
      m.en  : s.cachereq_en
    })

    s.cachereq_addr_h     = Wire(s.creq.addr_nbits)
    s.cachereq_addr       = Wire(s.creq.addr_nbits)
    s.cachereq_data       = Wire(s.creq.data_nbits)


    # cachereq_addr_mux

    s.cachereq_addr_mux = m = new_pmlib.Mux( s.addr_nbits, 2 )
    s.connect_dict({
      #m.in_[SEARCH] : s.cachereq_msg[ s.creq.addr_slice ],
      #m.in_[ACCESS] : s.cachereq_addr_reg.out,
      m.sel         : s.is_search
    })

    # tag_array

    s.tag_array = m = SRAMBitsSync_rst_1rw( s.num_lines, s.tag_nbits )
    s.connect_dict({
      m.wen   : s.tag_array_wen,
      #m.wdata : s.cachereq_addr_mux.out[ s.creq_tag ],
      #m.addr  : s.cachereq_addr_mux.out[ s.creq_idx ]
    })

    # tag compare

    s.tag_cmp = m = new_pmlib.arith.EqComparator( s.tag_nbits )
    s.connect_dict({
      #m.in0 : s.cachereq_addr_reg.out[ s.creq_tag ],
      m.in1 : s.tag_array.rdata,
      m.out : s.tag_match
    })

    # wdata_shifter

    s.wdata_shifter = m = new_pmlib.arith.LeftLogicalShifter( s.creq.data_nbits, 5 )
    s.connect_dict({
      m.in_   : s.cachereq_data,
      m.shamt : s.wr_shamt
    })

    # replicate

    s.replicate = Replicate( 32, 128 )
    s.connect( s.replicate.in_, s.wdata_shifter.out )

    # wdata_mux

    s.wdata_mux = m = new_pmlib.Mux( 128, 2 )
    s.connect_dict({
      m.in_[0] : s.replicate.out,
      m.in_[1] : s.memresp_msg[ s.mresp.data_slice ],
      m.sel    : s.is_refill
    })

    # data array

    s.data_array = m = SRAMBytesSync_rst_1rw( s.num_lines, s.line_nbytes )
    s.connect_dict({
      m.wen    : s.data_array_wen,
      m.wben   : s.data_array_wben,
      #m.addr   : s.cachereq_addr_reg.out[ s.creq_idx ],
      m.wdata  : s.wdata_mux.out
    })

    # refill_addr_gen

    s.refill_addr_gen = m = AddrGen( s.tag_nbits, s.idx_nbits, s.addr_nbits )
    #s.connect_dict({
    #  m.tag : s.cachereq_addr_reg.out[ s.creq_tag ],
    #  m.idx : s.cachereq_addr_reg.out[ s.creq_idx ]
    #})

    # evict_addr_gen

    s.evict_addr_gen = m = AddrGen( s.tag_nbits, s.idx_nbits, s.addr_nbits )
    s.connect_dict({
      m.tag : s.tag_array.rdata,
      #m.idx : s.cachereq_addr_reg.out[ s.creq_idx ]
    })

    # memreq_addr_mux

    s.memreq_addr_mux = m = new_pmlib.Mux( s.addr_nbits, 2 )
    s.connect_dict({
      m.in_[0] : s.refill_addr_gen.addr,
      m.in_[1] : s.evict_addr_gen.addr,
      m.sel    : s.memreq_type
    })

    # memreq_msg

    s.connect( s.memreq_msg[ s.mreq.addr_slice ], s.memreq_addr_mux.out )
    s.connect( s.memreq_msg[ s.mreq.type_slice ], s.memreq_type         )
    s.connect( s.memreq_msg[ s.mreq.len_slice  ], 0                     )
    s.connect( s.memreq_msg[ s.mreq.data_slice ], s.data_array.rdata    )

    # data array output response mux

    s.outresp_mux = m = new_pmlib.Mux( s.data_nbits, 4 )
    s.connect_dict({
      #m.in_[0] : s.data_array.rdata[0:32  ],
      #m.in_[1] : s.data_array.rdata[32:64 ],
      #m.in_[2] : s.data_array.rdata[64:96 ],
      #m.in_[3] : s.data_array.rdata[96:128],
      m.sel    : s.word_offset
    })

    # out data shifter

    s.out_data_shifter = m = new_pmlib.arith.RightLogicalShifter( s.creq.data_nbits, 5 )
    s.connect_dict({
      m.in_   : s.outresp_mux.out,
      m.shamt : s.rd_shamt
    })

    # cache resp s.connections

    #s.connect( s.cacheresp_msg[ s.cresp.type_slice ], s.cacheresp_type )
    #s.connect( s.cacheresp_msg[ s.cresp.len_slice ],  s.cacheresp_len  )
    #s.connect( s.cacheresp_msg[ s.cresp.data_slice ], s.out_data_shifter.out )

    # TODO: temporary hack to work around issue #79

    @s.combinational
    def temp():

      s.cachereq_addr_h      .value = s.cachereq_hold_reg.out [ s.creq.addr_slice ]
      s.cachereq_type        .value = s.cachereq_hold_reg.out [ s.creq.type_slice ]

      s.cachereq_addr        .value = s.cachereq_queue.deq.msg[ s.creq.addr_slice ]
      s.cachereq_len         .value = s.cachereq_queue.deq.msg[ s.creq.len_slice  ]
      s.cachereq_data        .value = s.cachereq_queue.deq.msg[ s.creq.data_slice ]
      s.cachereq_off         .value = s.cachereq_addr  [ 0:4        ]
      s.cachereq_off_h       .value = s.cachereq_addr_h[ 0:4        ]
      s.valid_idx            .value = s.cachereq_addr_h[ s.creq_idx ]
      s.dirty_idx            .value = s.cachereq_addr_h[ s.creq_idx ]

      s.cachereq_hold_reg.in_[ s.creq.type_slice ].value = s.cachereq_queue.deq.msg[ s.creq.type_slice ]
      s.cachereq_hold_reg.in_[ s.creq.addr_slice ].value = s.cachereq_queue.deq.msg[ s.creq.addr_slice ]
      s.cachereq_hold_reg.in_[ s.creq.len_slice  ].value = s.cachereq_queue.deq.msg[ s.creq.len_slice  ]
      s.cachereq_hold_reg.in_[ s.creq.data_slice ].value = s.cachereq_queue.deq.msg[ s.creq.data_slice ]

      s.cachereq_addr_mux.in_[SEARCH].value = s.cachereq_msg[ s.creq.addr_slice ]
      s.cachereq_addr_mux.in_[ACCESS].value = s.cachereq_addr
      s.tag_array.wdata      .value = s.cachereq_addr_mux.out[ s.creq_tag ]
      s.tag_array.addr       .value = s.cachereq_addr_mux.out[ s.creq_idx ]

      s.tag_cmp.in0          .value = s.cachereq_addr_h[ s.creq_tag ]

      s.data_array.addr      .value = s.cachereq_addr  [ s.creq_idx ]
      s.refill_addr_gen.tag  .value = s.cachereq_addr_h[ s.creq_tag ]
      s.refill_addr_gen.idx  .value = s.cachereq_addr_h[ s.creq_idx ]
      s.evict_addr_gen.idx   .value = s.cachereq_addr_h[ s.creq_idx ]

      s.outresp_mux.in_[0]   .value = s.data_array.rdata[0:32  ]
      s.outresp_mux.in_[1]   .value = s.data_array.rdata[32:64 ]
      s.outresp_mux.in_[2]   .value = s.data_array.rdata[64:96 ]
      s.outresp_mux.in_[3]   .value = s.data_array.rdata[96:128]

      s.cacheresp_queue.enq.msg[ s.cresp.type_slice ].value = s.cacheresp_type
      s.cacheresp_queue.enq.msg[ s.cresp.len_slice ] .value = s.cacheresp_len
      s.cacheresp_queue.enq.msg[ s.cresp.data_slice ].value = s.out_data_shifter.out


#--- gen-harness : end cut ---------------------------------------------

#-------------------------------------------------------------------------
# DirectMappedWriteBackCache
#-------------------------------------------------------------------------

class DirectMappedWriteBackCache (Model):

  def __init__( s, mem_nbytes, addr_nbits, data_nbits, line_nbits):

    #---------------------------------------------------------------------
    # Local Constants
    #---------------------------------------------------------------------

    # TODO: certain things are hardcoded in the implementation right now
    #       fix!  for now throw an assert
    assert line_nbits == 128

    # cache/memory request/response message parameters

    s.creq  = new_pmlib.mem_msgs.MemReqParams ( addr_nbits, data_nbits )
    s.cresp = new_pmlib.mem_msgs.MemRespParams( data_nbits )

    s.mreq  = new_pmlib.mem_msgs.MemReqParams ( addr_nbits, line_nbits )
    s.mresp = new_pmlib.mem_msgs.MemRespParams( line_nbits )

    # number of bytes in data "word"

    data_nbytes = data_nbits / 8

    # number of bytes in cache line

    line_nbytes = line_nbits / 8

    # total number of cache lines

    num_lines   = mem_nbytes / line_nbytes

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # Processor <-> Cache Interface

    s.cachereq  = InValRdyBundle ( s.creq.nbits  )
    s.cacheresp = OutValRdyBundle( s.cresp.nbits )

    # Cache <-> Memory Interface

    s.memreq  = OutValRdyBundle( s.mreq.nbits  )
    s.memresp = InValRdyBundle ( s.mresp.nbits )

    s.ctrl  = DirectMappedWriteBackCacheCtrl( num_lines )
    s.dpath = DirectMappedWriteBackCacheDpath( mem_nbytes, addr_nbits,
                                                  data_nbits, line_nbits )

  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------


    # Connect ctrl

    s.connect( s.ctrl.cachereq_val,  s.cachereq.val   )
    s.connect( s.ctrl.cachereq_rdy,  s.cachereq.rdy   )
    s.connect( s.ctrl.cacheresp_val, s.cacheresp.val  )
    s.connect( s.ctrl.cacheresp_rdy, s.cacheresp.rdy  )
    s.connect( s.ctrl.memreq_val,    s.memreq.val     )
    s.connect( s.ctrl.memreq_rdy,    s.memreq.rdy     )
    s.connect( s.ctrl.memresp_val,   s.memresp.val    )
    s.connect( s.ctrl.memresp_rdy,   s.memresp.rdy    )

    # Connect dpath

    s.connect( s.dpath.cachereq_msg,  s.cachereq.msg  )
    s.connect( s.dpath.cacheresp_msg, s.cacheresp.msg )
    s.connect( s.dpath.memreq_msg,    s.memreq.msg    )
    s.connect( s.dpath.memresp_msg,   s.memresp.msg   )

    # Connect control signals (ctrl -> dpath)

#--- gen-harness : begin cut ---------------------------------------------

    s.connect( s.ctrl.cachereq_en,    s.dpath.cachereq_en    )
    s.connect( s.ctrl.memresp_en,     s.dpath.memresp_en     )
    s.connect( s.ctrl.wr_shamt,       s.dpath.wr_shamt       )
    s.connect( s.ctrl.tag_array_wen,  s.dpath.tag_array_wen  )
    s.connect( s.ctrl.is_refill,      s.dpath.is_refill      )
    s.connect( s.ctrl.is_search,      s.dpath.is_search      )
    s.connect( s.ctrl.data_array_wen, s.dpath.data_array_wen )
    s.connect( s.ctrl.data_array_wben,s.dpath.data_array_wben)
    s.connect( s.ctrl.memreq_type,    s.dpath.memreq_type    )
    s.connect( s.ctrl.word_offset,    s.dpath.word_offset    )
    s.connect( s.ctrl.rd_shamt,       s.dpath.rd_shamt       )
    s.connect( s.ctrl.cacheresp_type, s.dpath.cacheresp_type )
    s.connect( s.ctrl.cacheresp_len,  s.dpath.cacheresp_len  )

    # Connect Queue Signals
    s.connect( s.ctrl.cachereq_deq_rdy,  s.dpath.cachereq_deq_rdy  )
    s.connect( s.ctrl.cachereq_deq_val,  s.dpath.cachereq_deq_val  )
    s.connect( s.ctrl.cachereq_enq_val,  s.dpath.cachereq_enq_val  )
    s.connect( s.ctrl.cachereq_enq_rdy,  s.dpath.cachereq_enq_rdy  )

    s.connect( s.ctrl.cacheresp_deq_rdy,  s.dpath.cacheresp_deq_rdy  )
    s.connect( s.ctrl.cacheresp_deq_val,  s.dpath.cacheresp_deq_val  )
    s.connect( s.ctrl.cacheresp_enq_val,  s.dpath.cacheresp_enq_val  )
    s.connect( s.ctrl.cacheresp_enq_rdy,  s.dpath.cacheresp_enq_rdy  )


    # Connect status signals (ctrl <- dpath)

    s.connect( s.ctrl.valid_idx,      s.dpath.valid_idx      )
    s.connect( s.ctrl.dirty_idx,      s.dpath.dirty_idx      )
    s.connect( s.ctrl.cachereq_type,  s.dpath.cachereq_type  )
    s.connect( s.ctrl.cachereq_len,   s.dpath.cachereq_len   )
    s.connect( s.ctrl.cachereq_off,   s.dpath.cachereq_off   )
    s.connect( s.ctrl.cachereq_off_h, s.dpath.cachereq_off_h )
    s.connect( s.ctrl.tag_match,      s.dpath.tag_match      )

#--- gen-harness : end cut ---------------------------------------------

    # Line Tracing

    s.cachereq_trace  = new_pmlib.mem_msgs.MemReqFromBits( s.creq  )
    s.connect( s.cachereq_trace.bits, s.cachereq.msg )

    s.cacheresp_trace = new_pmlib.mem_msgs.MemRespFromBits ( s.cresp )
    s.connect( s.cacheresp_trace.bits, s.dpath.cacheresp_msg )

    s.memreq_trace    = new_pmlib.mem_msgs.MemReqFromBits( s.mreq  )
    s.connect( s.memreq_trace.bits, s.memreq.msg )

    s.memresp_trace   = new_pmlib.mem_msgs.MemRespFromBits ( s.mresp )
    s.connect( s.memresp_trace.bits, s.memresp.msg )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    # If you would like poke into your design and add extra line trace
    # debugging information do so here. Ensure that the line trace string
    # always has the same fixed width every cycle to create well-structured
    # line traces. You may to modify the trace options below based on the
    # names you use in your design

    cachereq_str = \
      new_pmlib.valrdy.valrdy_to_str( s.cachereq_trace.line_trace(),
        s.cachereq.val, s.cachereq.rdy )

    cacheresp_str = \
      new_pmlib.valrdy.valrdy_to_str( s.cacheresp_trace.line_trace(),
        s.cacheresp.val, s.cacheresp.rdy )

    memreq_str = \
      new_pmlib.valrdy.valrdy_to_str( s.memreq_trace.line_trace(),
        s.memreq.val, s.memreq.rdy )

    memresp_str = \
      new_pmlib.valrdy.valrdy_to_str( s.memresp_trace.line_trace(),
        s.memresp.val, s.memresp.rdy )

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.ST_IDLE:        state_str = "I "
    if s.ctrl.state.out == s.ctrl.ST_TAG_CHECK:   state_str = "TC"
    if s.ctrl.state.out == s.ctrl.ST_DATA_ACCESS: state_str = "DA"
    if s.ctrl.state.out == s.ctrl.ST_WAIT:        state_str = "W "
    if s.ctrl.state.out == s.ctrl.ST_REFILL_REQ:  state_str = "RR"
    if s.ctrl.state.out == s.ctrl.ST_REFILL_WAIT: state_str = "RW"
    if s.ctrl.state.out == s.ctrl.ST_REFILL_DO:   state_str = "RD"
    if s.ctrl.state.out == s.ctrl.ST_EVICT_REQ:   state_str = "ER"
    if s.ctrl.state.out == s.ctrl.ST_EVICT_WAIT:  state_str = "EW"

    return "{}({},{},{}){}|{}|{}  |Q:| {} | {}" \
        .format( cachereq_str,s.dpath.outresp_mux.sel,s.dpath.data_array.addr, state_str, cacheresp_str,
                 memreq_str, memresp_str,
                 s.dpath.cachereq_queue.line_trace(),
                 s.dpath.cacheresp_queue.line_trace())
