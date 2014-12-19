#==============================================================================
# MatrixVecFL.py
#==============================================================================

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle, mem_msgs

from LaneManager      import LaneManager
from MatrixVecLaneFL  import MatrixVecLaneFL

class MatrixVecFL( Model ):

  def __init__( s, nlanes, nmul_stages,
                cop_addr_nbits=5,  cop_data_nbits=32,
                mem_addr_nbits=32, mem_data_nbits=32 ):

    # Config Params

    s.nlanes         = nlanes
    s.nmul_stages    = nmul_stages
    s.cop_addr_nbits = cop_addr_nbits
    s.cop_data_nbits = cop_data_nbits
    s.memreq_params  = mem_msgs.MemReqParams( mem_addr_nbits, mem_data_nbits )
    s.memresp_params = mem_msgs.MemRespParams( mem_data_nbits)

    # Interface

    s.from_cpu  = InValRdyBundle( cop_addr_nbits + cop_data_nbits )
    s.to_cpu    = OutPort       ( 1 )
    s.lane_req  = [ OutValRdyBundle( s.memreq_params .nbits )
                    for x in range( s.nlanes ) ]
    s.lane_resp = [ InValRdyBundle ( s.memresp_params.nbits )
                    for x in range( s.nlanes ) ]

  def elaborate_logic( s ):

    mreq  = s.memreq_params
    mresp = s.memresp_params

    s.mgr  = LaneManager( s.nlanes, s.cop_addr_nbits, s.cop_data_nbits )

    s.lane = [ MatrixVecLaneFL( x, mreq, mresp )
               for x in range( s.nlanes ) ]

    s.connect( s.from_cpu, s.mgr.from_cpu )
    s.connect( s.to_cpu,   s.mgr.to_cpu   )

    for i in range( s.nlanes ):
      s.connect( s.mgr.size,     s.lane[i].size       )
      s.connect( s.mgr.r_baddr,  s.lane[i].m_baseaddr )
      s.connect( s.mgr.v_baddr,  s.lane[i].v_baseaddr )
      s.connect( s.mgr.d_baddr,  s.lane[i].d_baseaddr )
      s.connect( s.mgr.go,       s.lane[i].go         )
      s.connect( s.mgr.done[i],  s.lane[i].done       )

      s.connect( s.lane_req[i],  s.lane[i].req        )
      s.connect( s.lane_resp[i], s.lane[i].resp       )

  def line_trace( s ):
    addr = s.from_cpu.to_str( s.from_cpu.msg[32:35] )
    data = s.from_cpu.to_str( s.from_cpu.msg[  :32] )
    go   = 'G' if s.mgr.go else ' '
    done = 'D' if s.to_cpu else ' '
    return '|{} {} {}{}|'.format( addr, data, go, done )

