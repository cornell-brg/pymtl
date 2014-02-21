#==============================================================================
# MatrixVecCOP.py
#==============================================================================

from new_pymtl   import *
from new_pmlib   import InValRdyBundle, OutValRdyBundle, mem_msgs

from LaneManager      import LaneManager
from MatrixVecLaneRTL import MatrixVecLaneRTL

class MatrixVecCOP( Model ):

  @capture_args
  def __init__( s, nlanes, cop_addr_nbits=3, cop_data_nbits=32,
                mem_addr_nbits=32, mem_data_nbits=32 ):

    # Config Params

    s.nlanes         = nlanes
    s.cop_addr_nbits = cop_addr_nbits
    s.cop_data_nbits = cop_data_nbits
    s.memreq_params  = mem_msgs.MemReqParams( mem_addr_nbits, mem_data_nbits )
    s.memresp_params = mem_msgs.MemRespParams( mem_data_nbits)

    # Interface

    s.from_cpu  = InValRdyBundle( cop_addr_nbits + cop_data_nbits )
    s.lane_req  = [ OutValRdyBundle( s.memreq_params .nbits )
                    for x in range( s.nlanes ) ]
    s.lane_resp = [ InValRdyBundle ( s.memresp_params.nbits )
                    for x in range( s.nlanes ) ]

  def elaborate_logic( s ):

    s.mgr  = LaneManager( s.nlanes, s.cop_addr_nbits, s.cop_data_nbits )

    s.lane = [ MatrixVecLaneRTL( x, s.memreq_params, s.memresp_params )
                for x in range( s.nlanes ) ]

    s.connect( s.from_cpu, s.mgr.from_cpu )

    for i in range( s.nlanes ):
      s.connect( s.mgr.size,     s.lane[i].size       )
      s.connect( s.mgr.r_baddr,  s.lane[i].m_baseaddr )
      s.connect( s.mgr.v_baddr,  s.lane[i].v_baseaddr )
      s.connect( s.mgr.d_baddr,  s.lane[i].d_baseaddr )
      s.connect( s.mgr.go,       s.lane[i].go         )
      s.connect( s.mgr.done[i],  s.lane[i].done       )

      s.connect( s.lane_req[i],  s.lane[i].req        )
      s.connect( s.lane_resp[i], s.lane[i].resp       )


