#=========================================================================
# MatrixVecFL
#=========================================================================

import greenlet

from new_pymtl import *
from new_pmlib import *
from MatrixVec import MatrixVec

import numpy

from pmlib_extra import GreenletWrapper,BytesMemPortProxy
from new_pmlib.queues import ChildReqRespQueueAdapter
from pmlib_extra import ListMemPortAdapter

class DotProductFL( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cpu  = ChildReqRespQueueAdapter( s.cpu_ifc )
    s.src0 = ListMemPortAdapter      ( s.mem_ifc )
    s.src1 = ListMemPortAdapter      ( s.mem_ifc )

    @s.tick_fl
    def logic():
      s.cpu.xtick()
      if not s.cpu.req_q.empty() and not s.cpu.resp_q.full():
        req = s.cpu.get_req()
        if req.ctrl_msg == 1:
          s.src0.set_size( req.data )
          s.src1.set_size( req.data )
        elif req.ctrl_msg == 2: s.src0.set_base( req.data )
        elif req.ctrl_msg == 3: s.src1.set_base( req.data )
        elif req.ctrl_msg == 0:
          result = numpy.dot( s.src0, s.src1 )
          s.cpu.push_resp( result )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  #def line_trace( s ):
  #  return "(" + str(s.cpu.req_q.empty()) + ")"

  def elaborate_logic( s ):
    pass
