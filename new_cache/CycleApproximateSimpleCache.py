#=======================================================================
# CycleApproximateSimpleCache.py
#=======================================================================

from pymtl          import *
from new_pmlib          import InValRdyBundle, OutValRdyBundle
from new_pmlib          import mem_msgs

from new_pmlib.mem_msgs import MemReqParams, MemRespParams
from new_pmlib.mem_msgs import MemReqFromBits, MemRespFromBits
from new_pmlib.mem_msgs import MemReqToBits, MemRespToBits

from math               import log
from math               import ceil

#-----------------------------------------------------------------------
# CL_Cache
#-----------------------------------------------------------------------
# (In a few places) HARD CODED FOR THE DEFAULT ARGUMENTS
# TODO rename and add headers
class CL_Cache( Model ):

  STATE_READY    = 0
  STATE_HIT      = 1
  STATE_READ     = 2
  STATE_EVICT    = 3
  STATE_COMPLETE = 4

  RD = 0
  WR = 1

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, line_nbytes   = 16, cache_nlines = 16, nways       = 1,
                   address_nbits = 32, data_nbits   = 32, hit_penalty = 0,
                   miss_penalty  = 0,  id = 0 ):

    #Val Ready Cache
    s.creq_len = int(ceil(log(data_nbits/8, 2)))

    s.cachereq_msg_data = InPort (data_nbits)
    s.cachereq_msg_addr = InPort (address_nbits)
    s.cachereq_msg_len  = InPort (s.creq_len)
    s.cachereq_msg_type = InPort (1)
    s.cachereq_val      = InPort (1)
    s.cachereq_rdy      = OutPort(1)

    s.cacheresp_msg_data = OutPort(data_nbits)
    s.cacheresp_msg_len  = OutPort(s.creq_len)
    s.cacheresp_msg_type = OutPort(1)
    s.cacheresp_val      = OutPort(1)
    s.cacheresp_rdy      = InPort (1)

    #Val Ready Mem
    mdata_nbits = line_nbytes * 8
    s.mreq_len  = int(ceil(log(line_nbytes, 2)))

    s.memreq_msg_data = [ OutPort(32) for x in range(mdata_nbits/32) ]
    s.memreq_msg_addr = OutPort(address_nbits)
    s.memreq_msg_len  = OutPort(s.mreq_len)
    s.memreq_msg_type = OutPort(1)
    s.memreq_val      = OutPort(1)
    s.memreq_rdy      = InPort (1)

    s.memresp_msg_data = [ InPort(32) for x in range(mdata_nbits/32) ]
    s.memresp_msg_len  = InPort (s.mreq_len)
    s.memresp_msg_type = InPort (1)
    s.memresp_val      = InPort (1)
    s.memresp_rdy      = OutPort(1)

    s.address_nbits = address_nbits
    s.data_nbits    = data_nbits
    s.line_nbytes   = line_nbytes

    s.nsets         = (cache_nlines)/(nways)
    s.nways         = nways
    s.nwords        = line_nbytes / 4

    #Set index accesses for pieces of address
    s.offset_start = 0
    s.offset_end   = int(log(line_nbytes,2))
    s.set_start    = s.offset_end
    s.set_end      = int(s.set_start + log(s.nsets, 2))
    s.tag_start    = s.set_end
    s.tag_end      = address_nbits


    s.cachelines  = [ Bits(32) for k in range( s.nsets * s.nways * s.nwords ) ]
    s.taglines    = [ Bits(32) for i in range( s.nsets * s.nways ) ]
    s.dirty_bits  = [ False    for i in range( s.nsets * s.nways ) ]
    s.valid_bits  = [ False    for i in range( s.nsets * s.nways ) ]
    s.arbitration = [0] * s.nsets

    s.miss_penalty = miss_penalty
    s.hit_penalty  = hit_penalty

    s.idx     = Bits(32)
    s.mask    = Bits(32)
    s.wr_mask = Bits(32)

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.stall_count = 0
    s.state       = s.STATE_READY

    s.buffer_msg_data = Bits(s.data_nbits)
    s.buffer_msg_addr = Bits(s.address_nbits)
    s.buffer_msg_len  = Bits(s.creq_len)
    s.buffer_msg_type = Bits(1)
    s.buffer_full     = False

    s.addr        = Bits(s.address_nbits)
    s.ilength     = Bits(s.creq_len)
    s.length      = Bits(s.data_nbits)
    s.type        = Bits(1)
    s.data        = Bits(s.data_nbits)

    s.curr_way    = Bits(s.nways)
    s.sent_mem    = False
    s.eaddr       = Bits(s.address_nbits) #address to memory
    s.set         = Bits(s.nsets,value = 0)
    s.word_offset = Bits(32, value = 0)
    s.byte_offset = Bits(32, value = 0)
    s.tag         = Bits(32,value = 0)

    s.in_go  = False
    s.out_go = False

    #-------------------------------------------------------------------
    # logic
    #-------------------------------------------------------------------
    @s.tick
    def logic():

      if s.reset:
        s.state       = s.STATE_READY
        s.buffer_full = False
        s.stall_count = False
        s.sent_mem    = False
        s.set.value         = 0
        s.word_offset.value = 0
        s.byte_offset.value = 0
        s.tag.value         = 0
        for i in range( s.nsets*s.nways ):
          s.dirty_bits[i] = False
          s.valid_bits[i] = False
        for i in range( s.nsets ):
          s.arbitration[i] = 0

      s.in_go  = s.cachereq_val  and s.cachereq_rdy
      s.out_go = s.cacheresp_val and s.cacheresp_rdy

      if s.out_go:
        s.buffer_full = False
        s.state       = s.STATE_READY

      if s.in_go and s.state == s.STATE_READY:
        s.buffer_msg_data.value = s.cachereq_msg_data
        s.buffer_msg_addr.value = s.cachereq_msg_addr
        s.buffer_msg_len .value = s.cachereq_msg_len
        s.buffer_msg_type.value = s.cachereq_msg_type
        s.buffer_full           = True

      #Set default values to be changed based on state
      s.cachereq_rdy.next  = 0
      s.cacheresp_val.next = 0
      s.memresp_rdy.next   = 0
      s.memreq_val.next    = 0

      s.type.value    = s.buffer_msg_type
      s.ilength.value = s.buffer_msg_len
      s.addr.value    = s.buffer_msg_addr
      s.data.value    = s.buffer_msg_data

      s.tag.value         = s.rshift( s.addr, s.tag_start )
      s.set.value         = s.rshift( s.addr & ((1<<s.set_end)-1),
                                      s.set_start
                                    )
      s.word_offset.value = (s.addr & ((1<<s.offset_end)-1)) / 4
      s.byte_offset.value = (s.addr & ((1<<s.offset_end)-1)) % 4
      s.length.value      = s.ilength

      if s.length == 0:
        s.length.value = s.data_nbits / 8

      s.length.value = s.length * 8

      if s.state == s.STATE_READY:
        s.cachereq_rdy.next = 1

        if s.buffer_full:
          s.curr_way.value    = 0
          s.cachereq_rdy.next = 0

      #Search Tag Array First
          while s.curr_way < s.nways:
            if s.tag == s.taglines[s.set*s.nways + s.curr_way] \
               and s.valid_bits[s.set*s.nways + s.curr_way]:
              break

            s.curr_way.value = s.curr_way + 1

          #Tag not found
          if s.curr_way >= s.nways:
            s.sent_mem = False

            if s.dirty_bits[s.set*s.nways + s.arbitration[s.set]]:
              s.state = s.STATE_EVICT

            else:
              s.state = s.STATE_READ

          else:
            if(not s.fake_stall(s.hit_penalty)):

              if(s.type == s.RD):
                s.state = s.STATE_COMPLETE

              elif(s.type == s.WR):


                #TODO Support Bits Constructor in @s.tick
                #s.cachelines[s.set][s.curr_way.value][offset:offset+length].value = Bits(length,value=s.data.value,trunc = True).value
                assert not s.length == 0
                #TODO :( bits translatable

                if   s.length == 32: s.mask = 0xFFFFFFFF
                elif s.length ==  8: s.mask = 0xFF   << (s.byte_offset.uint() * 8)
                elif s.length == 16: s.mask = 0xFFFF << (s.byte_offset.uint() * 8)

                if   s.length == 32: s.wr_mask = 0xFFFFFFFF
                elif s.length ==  8: s.wr_mask = 0xFF
                elif s.length == 16: s.wr_mask = 0xFFFF

                s.idx = s.set*s.nways*s.nwords + s.curr_way*s.nwords + s.word_offset

                s.cachelines[s.idx].value = \
                    (s.cachelines[s.idx] & (0xFFFFFFFF ^ s.mask)) \
                    | ((s.data.uint() & s.wr_mask) << s.byte_offset.uint() * 8 )

                s.state = s.STATE_COMPLETE

              s.stall_count = 0

      if(s.state == s.STATE_EVICT):

        if(not s.sent_mem):
          s.curr_way.value = s.arbitration[s.set]
          s.eaddr.value = 0
          s.eaddr.value = ((s.taglines[s.set*s.nways + s.curr_way] <<
                            s.tag_start) | (s.set << s.set_start))

          s.memreq_val.next = 1
          s.memreq_msg_type.value = s.WR
          s.memreq_msg_addr.value = s.eaddr
          s.memreq_msg_len.value = 0
          s.idx = s.set*s.nways*s.nwords + s.curr_way*s.nwords
          s.memreq_msg_data[0].value = s.cachelines[s.idx + 0]
          s.memreq_msg_data[1].value = s.cachelines[s.idx + 1]
          s.memreq_msg_data[2].value = s.cachelines[s.idx + 2]
          s.memreq_msg_data[3].value = s.cachelines[s.idx + 3]


          if s.miss_penalty == 0:
            s.memresp_rdy.next = 1

          if s.memreq_rdy and s.memreq_val:
            s.memreq_val.next = 0
            s.sent_mem        = True


        if s.sent_mem:

          if s.fake_stall(s.miss_penalty):

            if s.stall_count == s.miss_penalty:
              s.memresp_rdy.next = 1

          else:
            s.memresp_rdy.next = 1

            if s.memresp_val and s.memresp_rdy:
              s.memresp_rdy.next = 0
              s.state            = s.STATE_READ
              s.sent_mem         = False
              s.stall_count      = 0

      if s.state == s.STATE_READ:
        if not s.sent_mem:
          s.curr_way.value = s.arbitration[s.set]
          s.eaddr = (s.addr >> s.offset_end) << (s.offset_end)
          s.memreq_val.next = 1

          if s.miss_penalty == 0:
            s.memresp_rdy.next = 1

          s.memreq_msg_type.value = s.RD

          s.memreq_msg_addr.value = s.eaddr
          s.memreq_msg_len.value = 0
          s.memreq_msg_data[0].value = 0
          s.memreq_msg_data[1].value = 0
          s.memreq_msg_data[2].value = 0
          s.memreq_msg_data[3].value = 0
          if s.memreq_rdy and s.memreq_val:
            s.sent_mem        = True
            s.memreq_val.next = 0

        if s.sent_mem:
          if s.stall_count < s.miss_penalty:
            s.stall_count = s.stall_count + 1

            if s.stall_count == s.miss_penalty:
              s.memresp_rdy.next = 1

          else:
            s.memresp_rdy.next = 1

            if s.memresp_val and s.memresp_rdy:
              s.memresp_rdy.next = 0
              s.idx = s.set*s.nways*s.nwords + s.curr_way*s.nwords
              s.cachelines[s.idx + 0].value = s.memresp_msg_data[0]
              s.cachelines[s.idx + 1].value = s.memresp_msg_data[1]
              s.cachelines[s.idx + 2].value = s.memresp_msg_data[2]
              s.cachelines[s.idx + 3].value = s.memresp_msg_data[3]

              s.taglines[s.set*s.nways + s.curr_way].value = (s.addr >> s.tag_start)

              s.valid_bits[s.set*s.nways + s.curr_way] = True

              if s.type == s.WR:

                if   s.length == 32: s.mask = 0xFFFFFFFF
                elif s.length ==  8: s.mask = 0xFF   << (s.byte_offset.uint() * 8)
                elif s.length == 16: s.mask = 0xFFFF << (s.byte_offset.uint() * 8)

                if   s.length == 32: s.wr_mask = 0xFFFFFFFF
                elif s.length ==  8: s.wr_mask = 0xFF
                elif s.length == 16: s.wr_mask = 0xFFFF

                s.idx = s.set*s.nways*s.nwords + s.curr_way*s.nwords + s.word_offset

                s.cachelines[s.idx].value = \
                    (s.cachelines[s.idx] & (0xFFFFFFFF ^ s.mask)) \
                    | ((s.data.uint() & s.wr_mask) << s.byte_offset.uint() * 8 )

                s.dirty_bits[s.set*s.nways + s.curr_way] = True

              elif s.type == s.RD:
                s.dirty_bits[s.set*s.nways + s.curr_way] = False

              s.state = s.STATE_COMPLETE
              s.sent_mem = False
              s.stall_count = 0

      if s.state == s.STATE_COMPLETE:
        s.stall_count = 0

        s.cacheresp_msg_type.next = s.type
        s.cacheresp_msg_len.next  = s.ilength

        s.idx = s.set*s.nways*s.nwords + s.curr_way*s.nwords + s.word_offset

        if   s.length == 32: s.mask = 0xFFFFFFFF
        elif s.length ==  8: s.mask = 0xFF   << (s.byte_offset.uint() * 8)
        elif s.length == 16: s.mask = 0xFFFF << (s.byte_offset.uint() * 8)

        s.cacheresp_msg_data.next = \
            s.rshift( s.cachelines[s.idx] & s.mask, s.byte_offset.uint()*8 )

        s.cacheresp_val.next = 1

        if s.cacheresp_rdy:
          s.cachereq_rdy.next = 1
          s.arbitration[s.set] = (s.curr_way + 1) % s.nways
          s.buffer_full = False

  #---------------------------------------------------------------------
  # fake_stall
  #---------------------------------------------------------------------
  def fake_stall( s, penalty=0 ):
    if s.stall_count < penalty:
      s.stall_count        = s.stall_count + 1
      s.cachereq_rdy .next = 0
      s.cacheresp_val.next = 0
      s.memresp_rdy  .next = 0
      s.memreq_val   .next = 0
      return True
    else:
      return False

  #---------------------------------------------------------------------
  # rshift
  #---------------------------------------------------------------------
  def rshift( s, val=0, n=0 ):
      return (val % 0x100000000) >> n


  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  # TODO clean up and provide more useful info
  def line_trace( s ):
    #return '{} {} {} {}'.format( s.state, s.buffer, s.cacheresp, s.cachereq )
    return "TODO"

