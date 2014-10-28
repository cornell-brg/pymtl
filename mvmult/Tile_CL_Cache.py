#=======================================================================

from pymtl                     import *
from pclib                     import mem_msgs
from pclib                     import InValRdyBundle, OutValRdyBundle
from new_proc.ParcProc5stBypass    import ParcProc5stBypass
from new_proc.ParcProcPipelinedMul import ParcProcPipelinedMul
from MatrixVecCOP                  import MatrixVecCOP

from mem.simple_cache.DirectMappedWriteBackCache import (
  DirectMappedWriteBackCache,
  CL_Cache
)

Processor = ParcProcPipelinedMul

#-----------------------------------------------------------------------
# Tile
#-----------------------------------------------------------------------
class Tile_CL_Cache( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, reset_vector = 0, mem_data_nbits = 32,
                   cache_nbytes = 256 ):

    s.req_msg = mreq  = mem_msgs.MemReqParams ( 32, mem_data_nbits )
    s.rsp_msg = mresp = mem_msgs.MemRespParams( mem_data_nbits )

    s.mem_data_nbits = mem_data_nbits
    s.cache_nbytes   = cache_nbytes


    # TestProcManager Interface

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Memory Interface

    s.memreq  = OutValRdyBundle[2]( mreq.nbits  )
    s.memresp = InValRdyBundle [2]( mresp.nbits )

  def elaborate_logic( s ):

    nlanes      = 1
    nmul_stages = 4

    s.proc     = Processor( reset_vector=0x00000400 )
    s.cp2      = MatrixVecCOP( nlanes, nmul_stages,
                               cop_addr_nbits=5,
                               cop_data_nbits=32,
                               mem_addr_nbits=32,
                               mem_data_nbits=32 )

    s.connect( s.go,           s.proc.go        )
    s.connect( s.status,       s.proc.status    )
    s.connect( s.stats_en,     s.proc.stats_en  )
    s.connect( s.num_insts,    s.proc.num_insts )

    s.connect( s.cp2.from_cpu, s.proc.to_cp2    )
    s.connect( s.cp2.to_cpu,   s.proc.from_cp2  )

    if s.mem_data_nbits == 32: s.disable_caches()
    else:                      s.enable_caches ()

  #---------------------------------------------------------------------
  # disable_caches
  #---------------------------------------------------------------------
  def disable_caches( s ):

    # Connect the proc instruction port to memory

    s.connect( s.memreq [0],   s.proc.imemreq   )
    s.connect( s.memresp[0],   s.proc.imemresp  )

    # Multiplex accel and proc data req msg/val and data resp rdy to memory

    @s.combinational
    def logic():
      if not s.cp2.from_cpu.rdy:
        s.memreq [1].msg.value = s.cp2.lane_req [0].msg
        s.memreq [1].val.value = s.cp2.lane_req [0].val
        s.memresp[1].rdy.value = s.cp2.lane_resp[0].rdy
      else:
        s.memreq [1].msg.value = s.proc.dmemreq    .msg
        s.memreq [1].val.value = s.proc.dmemreq    .val
        s.memresp[1].rdy.value = s.proc.dmemresp   .rdy

    # Connect accel and proc data resp msg/val and req rdy to memory

    s.connect( s.memresp[1].msg, s.proc.dmemresp    .msg )
    s.connect( s.memresp[1].val, s.proc.dmemresp    .val )
    s.connect( s.memreq [1].rdy, s.proc.dmemreq     .rdy )
    s.connect( s.memresp[1].msg, s.cp2 .lane_resp[0].msg )
    s.connect( s.memresp[1].val, s.cp2 .lane_resp[0].val )
    s.connect( s.memreq [1].rdy, s.cp2 .lane_req [0].rdy )

  #---------------------------------------------------------------------
  # enable_caches()
  #---------------------------------------------------------------------
  def enable_caches( s ):

    s.icache   = CL_Cache                  ( cache_nlines  = s.cache_nbytes / s.mem_data_nbits*8,
                                             address_nbits =32,
                                             data_nbits    =32,
                                             hit_penalty   = 0,
                                             miss_penalty  = 3,
                                             line_nbytes   = s.mem_data_nbits/8,
                                             id = 0 ) # temporary hack for c translation

    s.dcache   = CL_Cache                  ( cache_nlines  = s.cache_nbytes / s.mem_data_nbits*8,
                                             address_nbits =32,
                                             data_nbits    =32,
                                             hit_penalty   = 0,
                                             miss_penalty  = 3,
                                             line_nbytes   = s.mem_data_nbits/8,
                                             id = 1 ) # temporary hack for c translation

    #s.icache = get_cpp( s.icache )
    #s.dcache = get_cpp( s.dcache )

    req = mem_msgs.MemReqParams ( 32, 32 )
    rsp = mem_msgs.MemRespParams( 32 )
    mreq = s.req_msg
    mrsp = s.rsp_msg

    #-------------------------------------------------------------------
    # icache to proc
    #-------------------------------------------------------------------

    # Connect the proc instruction port to icache, icache to memory

    #s.connect( s.proc.imemreq.msg[req.data_slice], s.icache.cachereq_msg_data   )
    #s.connect( s.proc.imemreq.msg[req.addr_slice], s.icache.cachereq_msg_addr   )
    #s.connect( s.proc.imemreq.msg[req.len_slice ], s.icache.cachereq_msg_len    )
    #s.connect( s.proc.imemreq.msg[req.type_slice], s.icache.cachereq_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_1():
      s.icache.cachereq_msg_data.value = s.proc.imemreq.msg[req.data_slice]
      s.icache.cachereq_msg_addr.value = s.proc.imemreq.msg[req.addr_slice]
      s.icache.cachereq_msg_len .value = s.proc.imemreq.msg[req.len_slice ]
      s.icache.cachereq_msg_type.value = s.proc.imemreq.msg[req.type_slice]

    s.connect( s.proc.imemreq.val,                 s.icache.cachereq_val   )
    s.connect( s.proc.imemreq.rdy,                 s.icache.cachereq_rdy   )

    #s.connect( s.proc.imemresp.msg[rsp.data_slice], s.icache.cacheresp_msg_data   )
    #s.connect( s.proc.imemresp.msg[rsp.len_slice ], s.icache.cacheresp_msg_len    )
    #s.connect( s.proc.imemresp.msg[rsp.type_slice], s.icache.cacheresp_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_1():
      s.proc.imemresp.msg[rsp.data_slice].value = s.icache.cacheresp_msg_data
      s.proc.imemresp.msg[rsp.len_slice ].value = s.icache.cacheresp_msg_len
      s.proc.imemresp.msg[rsp.type_slice].value = s.icache.cacheresp_msg_type
    s.connect( s.proc.imemresp.val,                 s.icache.cacheresp_val   )
    s.connect( s.proc.imemresp.rdy,                 s.icache.cacheresp_rdy   )

    #-------------------------------------------------------------------
    # icache to mem
    #-------------------------------------------------------------------

    #s.connect( s.memreq[0].msg[ 0: 32],            s.icache.memreq_msg_data[0]  )
    #s.connect( s.memreq[0].msg[32: 64],            s.icache.memreq_msg_data[1]  )
    #s.connect( s.memreq[0].msg[64: 96],            s.icache.memreq_msg_data[2]  )
    #s.connect( s.memreq[0].msg[96:128],            s.icache.memreq_msg_data[3]  )
    #s.connect( s.memreq[0].msg[mreq.addr_slice],         s.icache.memreq_msg_addr   )
    #s.connect( s.memreq[0].msg[mreq.len_slice ],         s.icache.memreq_msg_len    )
    #s.connect( s.memreq[0].msg[mreq.type_slice],         s.icache.memreq_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_3():
      s.memreq[0].msg[ 0: 32].value          = s.icache.memreq_msg_data[0]
      s.memreq[0].msg[32: 64].value          = s.icache.memreq_msg_data[1]
      s.memreq[0].msg[64: 96].value          = s.icache.memreq_msg_data[2]
      s.memreq[0].msg[96:128].value          = s.icache.memreq_msg_data[3]
      s.memreq[0].msg[mreq.addr_slice].value = s.icache.memreq_msg_addr
      s.memreq[0].msg[mreq.len_slice ].value = s.icache.memreq_msg_len
      s.memreq[0].msg[mreq.type_slice].value = s.icache.memreq_msg_type
    s.connect( s.memreq[0].val,                          s.icache.memreq_val   )
    s.connect( s.memreq[0].rdy,                          s.icache.memreq_rdy   )

    #s.connect( s.memresp[0].msg[ 0: 32],                 s.icache.memresp_msg_data[0]  )
    #s.connect( s.memresp[0].msg[32: 64],                 s.icache.memresp_msg_data[1]  )
    #s.connect( s.memresp[0].msg[64: 96],                 s.icache.memresp_msg_data[2]  )
    #s.connect( s.memresp[0].msg[96:128],                 s.icache.memresp_msg_data[3]  )
    #s.connect( s.memresp[0].msg[mrsp.len_slice ],         s.icache.memresp_msg_len    )
    #s.connect( s.memresp[0].msg[mrsp.type_slice],         s.icache.memresp_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_4():
      s.icache.memresp_msg_data[0].value = s.memresp[0].msg[ 0: 32]
      s.icache.memresp_msg_data[1].value = s.memresp[0].msg[32: 64]
      s.icache.memresp_msg_data[2].value = s.memresp[0].msg[64: 96]
      s.icache.memresp_msg_data[3].value = s.memresp[0].msg[96:128]
      s.icache.memresp_msg_len    .value = s.memresp[0].msg[mrsp.len_slice ]
      s.icache.memresp_msg_type   .value = s.memresp[0].msg[mrsp.type_slice]
    s.connect( s.memresp[0].val,                          s.icache.memresp_val   )
    s.connect( s.memresp[0].rdy,                          s.icache.memresp_rdy   )

    #-------------------------------------------------------------------
    # dcache to proc
    #-------------------------------------------------------------------

    # Multiplex accel and proc data req msg/val and data resp rdy to dcache

    @s.combinational
    def logic():

      if not s.cp2.from_cpu.rdy:
        s.dcache.cachereq_msg_data.value = s.cp2.lane_req[0].msg[req.data_slice]
        s.dcache.cachereq_msg_addr.value = s.cp2.lane_req[0].msg[req.addr_slice]
        s.dcache.cachereq_msg_len .value = s.cp2.lane_req[0].msg[req.len_slice ]
        s.dcache.cachereq_msg_type.value = s.cp2.lane_req[0].msg[req.type_slice]
        #s.dcache.cachereq .msg.value = s.cp2.lane_req [0].msg
        s.dcache.cachereq_val .value = s.cp2.lane_req [0].val
        s.dcache.cacheresp_rdy.value = s.cp2.lane_resp[0].rdy
      else:
        s.dcache.cachereq_msg_data.value = s.proc.dmemreq.msg[req.data_slice]
        s.dcache.cachereq_msg_addr.value = s.proc.dmemreq.msg[req.addr_slice]
        s.dcache.cachereq_msg_len .value = s.proc.dmemreq.msg[req.len_slice ]
        s.dcache.cachereq_msg_type.value = s.proc.dmemreq.msg[req.type_slice]
        #s.dcache.cachereq .msg.value = s.proc.dmemreq    .msg
        s.dcache.cachereq_val .value = s.proc.dmemreq    .val
        s.dcache.cacheresp_rdy.value = s.proc.dmemresp   .rdy

      s.proc.dmemresp   .msg[rsp.data_slice].value = s.dcache.cacheresp_msg_data
      s.proc.dmemresp   .msg[rsp.len_slice ].value = s.dcache.cacheresp_msg_len
      s.proc.dmemresp   .msg[rsp.type_slice].value = s.dcache.cacheresp_msg_type

      s.cp2.lane_resp[0].msg[rsp.data_slice].value = s.dcache.cacheresp_msg_data
      s.cp2.lane_resp[0].msg[rsp.len_slice ].value = s.dcache.cacheresp_msg_len
      s.cp2.lane_resp[0].msg[rsp.type_slice].value = s.dcache.cacheresp_msg_type

    # Connect accel and proc data resp msg/val and req rdy to dcache

    s.connect( s.dcache.cacheresp_val, s.proc.dmemresp    .val )
    s.connect( s.dcache.cacheresp_val, s.cp2 .lane_resp[0].val )
    s.connect( s.dcache.cachereq_rdy,  s.proc.dmemreq     .rdy )
    s.connect( s.dcache.cachereq_rdy,  s.cp2 .lane_req [0].rdy )

    #-------------------------------------------------------------------
    # dcache to mem
    #-------------------------------------------------------------------

    # Connect the dcache to memory

    #s.connect( s.memreq[1].msg[ 0: 32],            s.dcache.memreq_msg_data[0]  )
    #s.connect( s.memreq[1].msg[32: 64],            s.dcache.memreq_msg_data[1]  )
    #s.connect( s.memreq[1].msg[64: 96],            s.dcache.memreq_msg_data[2]  )
    #s.connect( s.memreq[1].msg[96:128],            s.dcache.memreq_msg_data[3]  )
    #s.connect( s.memreq[1].msg[mreq.addr_slice],   s.dcache.memreq_msg_addr   )
    #s.connect( s.memreq[1].msg[mreq.len_slice ],   s.dcache.memreq_msg_len    )
    #s.connect( s.memreq[1].msg[mreq.type_slice],   s.dcache.memreq_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_7():
      s.memreq[1].msg[ 0: 32].value          = s.dcache.memreq_msg_data[0]
      s.memreq[1].msg[32: 64].value          = s.dcache.memreq_msg_data[1]
      s.memreq[1].msg[64: 96].value          = s.dcache.memreq_msg_data[2]
      s.memreq[1].msg[96:128].value          = s.dcache.memreq_msg_data[3]
      s.memreq[1].msg[mreq.addr_slice].value = s.dcache.memreq_msg_addr
      s.memreq[1].msg[mreq.len_slice ].value = s.dcache.memreq_msg_len
      s.memreq[1].msg[mreq.type_slice].value = s.dcache.memreq_msg_type
    s.connect( s.memreq[1].val,                s.dcache.memreq_val   )
    s.connect( s.memreq[1].rdy,                s.dcache.memreq_rdy   )

    #s.connect( s.memresp[1].msg[ 0: 32],                 s.dcache.memresp_msg_data[0]  )
    #s.connect( s.memresp[1].msg[32: 64],                 s.dcache.memresp_msg_data[1]  )
    #s.connect( s.memresp[1].msg[64: 96],                 s.dcache.memresp_msg_data[2]  )
    #s.connect( s.memresp[1].msg[96:128],                 s.dcache.memresp_msg_data[3]  )
    #s.connect( s.memresp[1].msg[mrsp.len_slice ],        s.dcache.memresp_msg_len    )
    #s.connect( s.memresp[1].msg[mrsp.type_slice],        s.dcache.memresp_msg_type   )
    @s.combinational # TODO: TEMPORARY HACK
    def fixme_8():
      s.dcache.memresp_msg_data[0].value = s.memresp[1].msg[ 0: 32]
      s.dcache.memresp_msg_data[1].value = s.memresp[1].msg[32: 64]
      s.dcache.memresp_msg_data[2].value = s.memresp[1].msg[64: 96]
      s.dcache.memresp_msg_data[3].value = s.memresp[1].msg[96:128]
      s.dcache.memresp_msg_len    .value = s.memresp[1].msg[mrsp.len_slice ]
      s.dcache.memresp_msg_type   .value = s.memresp[1].msg[mrsp.type_slice]
    s.connect( s.memresp[1].val,           s.dcache.memresp_val   )
    s.connect( s.memresp[1].rdy,           s.dcache.memresp_rdy   )


  #---------------------------------------------------------------------
  # TODO: enable_caches()
  #---------------------------------------------------------------------
  def TODO_enable_caches( s ):

    s.icache   = CL_Cache()
    s.dcache   = CL_Cache()

    # Connect the proc instruction port to icache, icache to memory

    s.connect( s.proc.imemreq,    s.icache.cachereq   )
    s.connect( s.proc.imemresp,   s.icache.cacheresp  )
    s.connect( s.memreq [0],      s.icache.memreq     )
    s.connect( s.memresp[0],      s.icache.memresp    )

    # Multiplex accel and proc data req msg/val and data resp rdy to dcache

    @s.combinational
    def logic():
      if not s.cp2.from_cpu.rdy:
        s.dcache.cachereq .msg.value = s.cp2.lane_req [0].msg
        s.dcache.cachereq .val.value = s.cp2.lane_req [0].val
        s.dcache.cacheresp.rdy.value = s.cp2.lane_resp[0].rdy
      else:
        s.dcache.cachereq .msg.value = s.proc.dmemreq    .msg
        s.dcache.cachereq .val.value = s.proc.dmemreq    .val
        s.dcache.cacheresp.rdy.value = s.proc.dmemresp   .rdy

    # Connect accel and proc data resp msg/val and req rdy to dcache

    s.connect( s.dcache.cacheresp.msg, s.proc.dmemresp    .msg )
    s.connect( s.dcache.cacheresp.val, s.proc.dmemresp    .val )
    s.connect( s.dcache.cachereq .rdy, s.proc.dmemreq     .rdy )
    s.connect( s.dcache.cacheresp.msg, s.cp2 .lane_resp[0].msg )
    s.connect( s.dcache.cacheresp.val, s.cp2 .lane_resp[0].val )
    s.connect( s.dcache.cachereq .rdy, s.cp2 .lane_req [0].rdy )

    # Connect the dcache to memory

    s.connect( s.memreq [1],           s.dcache.memreq  )
    s.connect( s.memresp[1],           s.dcache.memresp )

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    return s.proc.line_trace() + s.cp2.line_trace() + \
        " I$ {} {}".format(s.proc.imemreq, s.proc.imemresp) + \
        " D$ {} {}".format(s.proc.dmemreq, s.proc.dmemresp) #+ \
        #" DM {} {}".format(s.memreq[1], s.memresp[1])
        #" x {} {} {}".format( s.icache.memreq_msg_addr,
        #                         s.icache.memreq_msg_data[3],
        #                         s.icache.memreq_msg_data[2],
        #                         #s.icache.memreq_msg_data[1],
        #                         #s.icache.memreq_msg_data[0], ) + \
        #                             ) + \
        #" X {} {}".format( #s.icache.memresp_msg_data[3],
        #                   #      s.icache.memresp_msg_data[2],
        #                         s.icache.memresp_msg_data[1],
        #                         s.icache.memresp_msg_data[0],
        #                             )
        #" IM {} {}".format(s.memreq[0], s.memresp[0])

    return s.proc.line_trace() + s.cp2.line_trace()
  #  return s.proc.line_trace() + \
  #"[] {} {} {} []".format( s.proc.dpath.snoop_unit_F.in_, s.proc.dpath.snoop_unit_F.out, s.proc.dpath.imemresp_msg ) + \
  #"{} {}".format(s.proc.imemreq, s.proc.imemresp)
  ##"{} {}".format(s.proc.imemresp, s.icache.cacheresp) + \
  ##s.icache.line_trace()

