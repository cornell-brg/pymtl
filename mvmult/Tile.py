#=======================================================================

from new_pymtl                  import *
from new_pmlib                  import mem_msgs
from new_pmlib                  import InValRdyBundle, OutValRdyBundle
from new_proc.ParcProc5stBypass import ParcProc5stBypass
from MatrixVecCOP               import MatrixVecCOP

#-----------------------------------------------------------------------
# Tile
#-----------------------------------------------------------------------
class Tile( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, reset_vector = 0 ):

    mreq  = mem_msgs.MemReqParams ( 32, 32 )
    mresp = mem_msgs.MemRespParams( 32 )

    # TestProcManager Interface

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    #s.stats_en  = OutPort  ( 1  )
    #s.num_insts = OutPort  ( 32 )

    # Memory Interface

    s.memreq  = OutValRdyBundle[2]( mreq.nbits  )
    s.memresp = InValRdyBundle [2]( mresp.nbits )

  def elaborate_logic( s ):

    nlanes      = 1
    nmul_stages = 4

    s.proc     = ParcProc5stBypass( reset_vector=0x00000400 )
    s.cp2      = MatrixVecCOP( nlanes, nmul_stages,
                               cop_addr_nbits=5,  cop_data_nbits=32,
                               mem_addr_nbits=32, mem_data_nbits=32 )

    s.connect( s.go,         s.proc.go       )
    s.connect( s.status,     s.proc.status   )
    s.connect( s.memreq [0], s.proc.imemreq  )
    s.connect( s.memresp[0], s.proc.imemresp )
    #s.connect( s.memreq [1], s.proc.dmemreq  )
    #s.connect( s.memresp[1], s.proc.dmemresp )

    s.connect( s.cp2.from_cpu, s.proc.to_cp2   )
    s.connect( s.cp2.to_cpu,   s.proc.from_cp2 )

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

    s.connect( s.memresp[1].msg, s.proc.dmemresp    .msg )
    s.connect( s.memresp[1].val, s.proc.dmemresp    .val )
    s.connect( s.memreq [1].rdy, s.proc.dmemreq     .rdy )
    s.connect( s.memresp[1].msg, s.cp2 .lane_resp[0].msg )
    s.connect( s.memresp[1].val, s.cp2 .lane_resp[0].val )
    s.connect( s.memreq [1].rdy, s.cp2 .lane_req[0] .rdy )

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):
    return s.proc.line_trace()

