#=========================================================================
# MatrixVecFL
#=========================================================================

import greenlet

from pymtl import *
from new_pmlib import *

from pmlib_extra import GreenletWrapper, BytesMemPortProxy

from MatrixVec       import MatrixVec
from MatrixVecBundle import InMatrixVecBundle,OutMatrixVecBundle

class MatrixVecFL (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, cop_addr_nbits=5,  cop_data_nbits=32,
                   mem_addr_nbits=32, mem_data_nbits=32 ):

    # Config params

    s.addr_nbits = cop_addr_nbits
    s.data_nbits = cop_data_nbits
    s.mreq_p     = mem_msgs.MemReqParams( mem_addr_nbits, mem_data_nbits )
    s.mresp_p    = mem_msgs.MemRespParams( mem_data_nbits)

    # COP interface

    s.from_cpu  = InValRdyBundle( s.addr_nbits + s.data_nbits )
    s.to_cpu    = OutMatrixVecBundle()

    # Memory request/response ports

    s.memreq  = InValRdyBundle  ( s.mreq_p.nbits  )
    s.memresp = OutValRdyBundle ( s.mresp_p.nbits )

    # Internal functional model

    s.mem = BytesMemPortProxy( s.mreq_p, s.mresp_p, s.memreq, s.memresp )
    s.xcel_mvmult = MatrixVec( s.mem )

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    @s.pausable_tick
    def logic():

      s.from_cpu.rdy.next = 1

      # Toggle the to_cpu bit

      if s.to_cpu.done:
        s.to_cpu.done.next = 0

      # Process the command

      s.trace = " "
      if s.from_cpu.val and s.from_cpu.rdy:

        addr = s.from_cpu.msg[s.data_nbits:s.from_cpu.msg.nbits]
        data = s.from_cpu.msg[0:s.data_nbits]

        if   addr == 1:
          s.xcel_mvmult.set_size( data )
          s.from_cpu.rdy.next = 1
          s.trace = "s"

        elif addr == 2:
          s.xcel_mvmult.set_src0_addr( data )
          s.from_cpu.rdy.next = 1
          s.trace = "0"

        elif addr == 3:
          s.xcel_mvmult.set_src1_addr( data )
          s.from_cpu.rdy.next = 1
          s.trace = "1"

        elif addr == 4:
          s.xcel_mvmult.set_dest_addr( data )
          s.from_cpu.rdy.next = 1
          s.trace = "d"

        elif addr == 0 and data == 1:
          s.trace = "g"
          s.from_cpu.rdy.next = 0
          s.xcel_mvmult.go()
          s.from_cpu.rdy.next = 1
          s.to_cpu.done.next = 1

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.to_cpu.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.trace + s.mem.line_trace() + ")"

