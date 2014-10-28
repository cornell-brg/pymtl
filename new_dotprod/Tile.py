#=======================================================================

from pymtl                       import *
from pclib                       import mem_msgs
from pclib                       import InValRdyBundle, OutValRdyBundle
from pclib                       import MemMsg
from pclib                       import CP2Msg
from new_dpproc.ParcProcPipelinedMul import ParcProcPipelinedMul
from DotProductRTL                   import DotProductRTL
from DotProductFL                    import DotProductFL

# Cache with single-cycle hit lantency
from mem.simple_cache.DirectMappedWriteBackCache import (
    DirectMappedWriteBackCache
)

Processor  = ParcProcPipelinedMul
DotProduct = DotProductFL

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

    mem_ifc = MemMsg   ( 32, 32)
    cpu_ifc = CP2Msg   ( 5, 32 )

    s.cp2      = DotProduct(mem_ifc, cpu_ifc )

    s.connect( s.go,           s.proc.go        )
    s.connect( s.status,       s.proc.status    )
    s.connect( s.stats_en,     s.proc.stats_en  )
    s.connect( s.num_insts,    s.proc.num_insts )

    s.to_cp2_msg = Wire( 37 )
    s.to_cp2_val = Wire( 1  )
    s.to_cp2_rdy = Wire( 1  )

    s.from_cp2_msg = Wire( 32 )
    s.from_cp2_val = Wire( 1  )
    s.from_cp2_rdy = Wire( 1  )

    s.connect( s.proc.to_cp2.msg, s.to_cp2_msg   )
    s.connect( s.proc.to_cp2.val, s.to_cp2_val   )
    s.connect( s.proc.to_cp2.rdy, s.to_cp2_rdy   )


    s.connect( s.from_cp2_msg, s.proc.from_cp2.msg  )
    s.connect( s.from_cp2_val, s.proc.from_cp2.val  )
    s.connect( s.from_cp2_rdy, s.proc.from_cp2.rdy  )

    if s.mem_data_nbits == 32: s.disable_caches()
    else:                      s.enable_caches ()

    @s.combinational
    def connect_bitstructs():
      s.cp2.cpu_ifc.req_msg.value = s.to_cp2_msg
      s.cp2.cpu_ifc.req_val.value = s.to_cp2_val
      s.to_cp2_rdy.value = s.cp2.cpu_ifc.req_rdy

      s.from_cp2_msg.value = s.cp2.cpu_ifc.resp_msg
      s.cp2.cpu_ifc.resp_rdy.value = s.from_cp2_rdy
      s.from_cp2_val.value = s.cp2.cpu_ifc.resp_val.value


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
      if s.cp2.mem_ifc.req_val or s.cp2.mem_ifc.resp_rdy:
        s.memreq [1].msg.value = s.cp2.mem_ifc.req_msg
        s.memreq [1].val.value = s.cp2.mem_ifc.req_val
        s.memresp[1].rdy.value = s.cp2.mem_ifc.resp_rdy
      else:
        s.memreq [1].msg.value = s.proc.dmemreq    .msg
        s.memreq [1].val.value = s.proc.dmemreq    .val
        s.memresp[1].rdy.value = s.proc.dmemresp   .rdy

      s.cp2.mem_ifc.resp_msg.value = s.memresp[1].msg
      s.cp2.mem_ifc.resp_val.value = s.memresp[1].val
      s.cp2.mem_ifc.req_rdy.value = s.memreq [1].rdy



    # Connect accel and proc data resp msg/val and req rdy to memory

    s.connect( s.memresp[1].msg, s.proc.dmemresp    .msg )
    s.connect( s.memresp[1].val, s.proc.dmemresp    .val )
    s.connect( s.memreq [1].rdy, s.proc.dmemreq     .rdy )
    

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
    return s.proc.line_trace() + s.cp2.line_trace()
    #return s.proc.line_trace() + s.cp2.line_trace() + \
    #    " I$ {} {}".format(s.proc.imemreq, s.proc.imemresp) + \
    #    " D$ {} {}".format(s.proc.dmemreq, s.proc.dmemresp)

