#=======================================================================

from new_pymtl                       import *
from new_pmlib                       import mem_msgs
from new_pmlib                       import InValRdyBundle, OutValRdyBundle
from new_dpproc.ParcProcPipelinedMul import ParcProcPipelinedMul
from DotProductRTL                   import DotProduct

# Cache with single-cycle hit lantency
from new_cache.DirectMappedWriteBackCache import DirectMappedWriteBackCache

Processor = ParcProcPipelinedMul

#-----------------------------------------------------------------------
# Tile
#-----------------------------------------------------------------------
class Tile( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, reset_vector = 0, mem_data_nbits = 32,
                   cache_nbytes = 16384 ):

    s.req_msg = mem_msgs.MemReqParams ( 32, mem_data_nbits )
    s.rsp_msg = mem_msgs.MemRespParams( mem_data_nbits )

    s.mem_data_nbits = mem_data_nbits
    s.cache_nbytes   = cache_nbytes


    # TestProcManager Interface

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Memory Interface

    s.memreq  = OutValRdyBundle[2]( s.req_msg.nbits  )
    s.memresp = InValRdyBundle [2]( s.rsp_msg.nbits )

  def elaborate_logic( s ):

    nlanes      = 1
    nmul_stages = 4

    s.proc     = Processor( reset_vector=0x00000400 )
    s.cp2      = DotProduct(   nmul_stages,
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
      if not s.cp2.state == 0:
        s.memreq [1].msg.value = s.cp2.req.msg
        s.memreq [1].val.value = s.cp2.req.val
        s.memresp[1].rdy.value = s.cp2.resp.rdy
      else:
        s.memreq [1].msg.value = s.proc.dmemreq    .msg
        s.memreq [1].val.value = s.proc.dmemreq    .val
        s.memresp[1].rdy.value = s.proc.dmemresp   .rdy

    # Connect accel and proc data resp msg/val and req rdy to memory

    s.connect( s.memresp[1].msg, s.proc.dmemresp    .msg )
    s.connect( s.memresp[1].val, s.proc.dmemresp    .val )
    s.connect( s.memreq [1].rdy, s.proc.dmemreq     .rdy )
    s.connect( s.memresp[1].msg, s.cp2.resp.msg )
    s.connect( s.memresp[1].val, s.cp2.resp.val )
    s.connect( s.memreq [1].rdy, s.cp2.req.rdy )

  #---------------------------------------------------------------------
  # enable_caches()
  #---------------------------------------------------------------------
  def enable_caches( s ):

    s.icache   = DirectMappedWriteBackCache( mem_nbytes=s.cache_nbytes,
                                             addr_nbits=32,
                                             data_nbits=32,
                                             line_nbits=s.mem_data_nbits )
    s.dcache   = DirectMappedWriteBackCache( mem_nbytes=s.cache_nbytes,
                                             addr_nbits=32,
                                             data_nbits=32,
                                             line_nbits=s.mem_data_nbits )

    # Connect the proc instruction port to icache, icache to memory

    s.connect( s.proc.imemreq,    s.icache.cachereq   )
    s.connect( s.proc.imemresp,   s.icache.cacheresp  )
    s.connect( s.memreq [0],      s.icache.memreq     )
    s.connect( s.memresp[0],      s.icache.memresp    )

    # Multiplex accel and proc data req msg/val and data resp rdy to dcache

    @s.combinational
    def logic():
      if s.cp2.ctrl.state != 0 and s.cp2.ctrl.state != 4:
        s.dcache.cachereq .msg.value = s.cp2.req.msg
        s.dcache.cachereq .val.value = s.cp2.req.val
        s.dcache.cacheresp.rdy.value = s.cp2.resp.rdy

        s.proc.dmemreq.rdy.value = 0

      else:
        s.dcache.cachereq .msg.value = s.proc.dmemreq    .msg
        s.dcache.cachereq .val.value = s.proc.dmemreq    .val
        s.dcache.cacheresp.rdy.value = s.proc.dmemresp   .rdy

        s.proc.dmemreq.rdy.value = s.dcache.cachereq.rdy

    # Connect accel and proc data resp msg/val and req rdy to dcache

    s.connect( s.dcache.cacheresp.msg, s.proc.dmemresp    .msg )
    s.connect( s.dcache.cacheresp.val, s.proc.dmemresp    .val )
    s.connect( s.dcache.cacheresp.msg, s.cp2 .resp.msg )
    s.connect( s.dcache.cacheresp.val, s.cp2 .resp.val )
    s.connect( s.dcache.cachereq .rdy, s.cp2 .req.rdy )

    # Connect the dcache to memory

    s.connect( s.memreq [1],           s.dcache.memreq  )
    s.connect( s.memresp[1],           s.dcache.memresp )

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    return s.proc.line_trace() +"( {} {} {} {})".format(s.proc.dpath.wb_mux_W.out, s.proc.dpath.wb_mux_W_sel, s.proc.dpath.wb_mux_W.out, s.proc.dpath.rf_wen_W[0]) +s.cp2.line_trace()
    #return s.proc.line_trace() + s.cp2.line_trace() + \
    #    " I$ {} {}".format(s.proc.imemreq, s.proc.imemresp) + \
    #    " D$ {} {}".format(s.proc.dmemreq, s.proc.dmemresp)

