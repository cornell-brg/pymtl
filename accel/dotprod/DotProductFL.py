#=========================================================================
# DotProductFL
#=========================================================================

import greenlet

from pymtl      import *
from pclib.fl   import ListMemPortAdapterOld
from pclib.cl   import ChildReqRespQueueAdapter
from pclib.ifcs import ChildReqRespBundle, ParentReqRespBundle

#-------------------------------------------------------------------------
# dot
#-------------------------------------------------------------------------
# Simple dot product function. One could also use the dot product
# function from numpy.

def dot( src0, src1 ):
  sum = 0
  for elm0,elm1 in zip( src0, src1 ):
    sum += elm0 * elm1
  return sum

#-------------------------------------------------------------------------
# DotProductFL
#-------------------------------------------------------------------------

class DotProductFL( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):

    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cpu  = ChildReqRespQueueAdapter( s.cpu_ifc )
    s.src0 = ListMemPortAdapterOld   ( s.mem_ifc )
    s.src1 = ListMemPortAdapterOld   ( s.mem_ifc )

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
          result = dot( s.src0, s.src1 )
          s.cpu.push_resp( result )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + str(s.cpu_ifc.resp_val) + str(s.cpu_ifc.resp_rdy) + ")"

  def elaborate_logic( s ):
    pass

