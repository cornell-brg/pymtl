#=========================================================================
# MatrixVecFL
#=========================================================================

import greenlet

from new_pymtl import *
from new_pmlib import *
from MatrixVec import MatrixVec

from pmlib_extra import GreenletWrapper,BytesMemPortProxy

class DotProduct (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.mem = BytesMemPortProxy( s.mem_ifc )
    s.xcel_mvmult = MatrixVec( s.mem )

    @s.pausable_tick
    def logic():

      s.cpu_ifc.p2c_rdy.next = 1

      if s.cpu_ifc.p2c_val and s.cpu_ifc.p2c_rdy:
        addr = s.cpu_ifc.p2c_msg.addr
        data = s.cpu_ifc.p2c_msg.data

        if   addr == 1: s.xcel_mvmult.set_size     ( data )
        elif addr == 2: s.xcel_mvmult.set_src0_addr( data )
        elif addr == 3: s.xcel_mvmult.set_src1_addr( data )

        if s.xcel_mvmult.is_valid():
          s.cpu_ifc.p2c_rdy.next = 0
          result = s.xcel_mvmult.go()
          print "r", result
          s.cpu_ifc.c2p_msg.next = result
          s.cpu_ifc.c2p_val.next = 1

      if s.cpu_ifc.c2p_val and s.cpu_ifc.c2p_rdy:
        s.cpu_ifc.c2p_rdy.next = 0
        s.cpu_ifc.p2c_rdy.next = 1

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + str(s.xcel_mvmult.is_valid()) + " "  + s.mem.line_trace() + ")"

  def elaborate_logic( s ):
    pass
