#=========================================================================
# DotProductCL
#=========================================================================

import greenlet
import numpy

from pymtl        import *
from pclib.fl     import ListMemPortAdapter
from pclib.cl     import ChildReqRespQueueAdapter, ParentReqRespQueueAdapter
from pclib.ifcs import ChildReqRespBundle, ParentReqRespBundle, MemMsg

#-------------------------------------------------------------------------
# helpers
#-------------------------------------------------------------------------

def mreq( a ):
  return MemMsg( 32, 32 ).req.mk_msg( 0, a, 0, 0 )

def gen_addresses( size, a, b ):
  x = []
  for i in range( size ):
    x.append( a+i*4 )
    x.append( b+i*4 )
  return list(reversed(x))

#-------------------------------------------------------------------------
# DotProductCL
#-------------------------------------------------------------------------
class DotProductCL( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cpu     = ChildReqRespQueueAdapter ( s.cpu_ifc )
    s.mem     = ParentReqRespQueueAdapter( s.mem_ifc )

    s.go    = False
    s.size  = 0
    s.src0  = 0
    s.src1  = 0
    s.data  = []

    @s.tick_fl
    def logic():
      s.cpu.xtick()
      s.mem.xtick()

      if s.go:

        if s.addrs and not s.mem.req_q.full():
          s.mem.push_req( mreq( s.addrs.pop() ) )
        if not s.mem.resp_q.empty():
          s.data.append( s.mem.get_resp() )

        if len( s.data ) == s.size*2:
          result = numpy.dot( s.data[0::2], s.data[1::2] )
          s.cpu.push_resp( result )
          s.go = False

      elif not s.cpu.req_q.empty() and not s.cpu.resp_q.full():
        req = s.cpu.get_req()
        if req.ctrl_msg   == 1: s.size = req.data
        elif req.ctrl_msg == 2: s.src0 = req.data
        elif req.ctrl_msg == 3: s.src1 = req.data
        elif req.ctrl_msg == 0:
          s.addrs = gen_addresses( s.size, s.src0, s.src1 )
          s.go    = True

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return '{} {}'.format(
        s.cpu.req_q.in_,
        s.mem.req_q.out, )

  def elaborate_logic( s ):
    pass
