#=========================================================================
# ParcProcFL
#=========================================================================

from __future__ import print_function

import greenlet
import types

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import XcelReqMsg, XcelRespMsg
from pclib.ifcs import MemMsg, MemReqMsg, MemRespMsg
from pclib.fl   import InValRdyQueueAdapter, OutValRdyQueueAdapter
from pclib.fl   import BytesMemPortAdapter

from pisa import PisaSemantics
from pisa import PisaInst

class ParcProcFL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, reset_vector=0, test_en=True ):

    s.reset_vector = reset_vector
    s.test_en      = test_en

    # Proc/Mngr Interface

    s.mngr2proc  = InValRdyBundle  ( 32 )
    s.proc2mngr  = OutValRdyBundle ( 32 )

    # Instruction Memory Request/Response Interface

    s.imemreq    = OutValRdyBundle ( MemReqMsg(32,32) )
    s.imemresp   = InValRdyBundle  ( MemRespMsg(32)   )

    # Data Memory Request/Response Interface

    s.dmemreq    = OutValRdyBundle ( MemReqMsg(32,32) )
    s.dmemresp   = InValRdyBundle  ( MemRespMsg(32)   )

    # Accelerator Interface

    s.xcelreq    = OutValRdyBundle ( XcelReqMsg()  )
    s.xcelresp   = InValRdyBundle  ( XcelRespMsg() )

    # Memory Proxy

    s.imem = BytesMemPortAdapter( s.imemreq, s.imemresp )
    s.dmem = BytesMemPortAdapter( s.dmemreq, s.dmemresp )

    # Proc/Mngr Queue Adapters

    s.mngr2proc_q  = InValRdyQueueAdapter  ( s.mngr2proc )
    s.proc2mngr_q  = OutValRdyQueueAdapter ( s.proc2mngr )

    # Accelerator Queue Adapters

    s.xcelreq_q    = OutValRdyQueueAdapter ( s.xcelreq  )
    s.xcelresp_q   = InValRdyQueueAdapter  ( s.xcelresp )

    # Extra Interfaces

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Construct the ISA semantics object

    s.isa = PisaSemantics( s.dmem, s.mngr2proc_q, s.proc2mngr_q )

    # We "monkey patch" the mtx/mfx execution functions so that they
    # interact with the above queue adapters

    def execute_mtx( s_, inst ):
      s.xcelreq_q.append( XcelReqMsg().mk_wr( inst.rs, s_.R[inst.rt] ) )
      xcelresp_msg = s.xcelresp_q.popleft()
      s_.PC += 4

    def execute_mfx( s_, inst ):
      s.xcelreq_q.append( XcelReqMsg().mk_rd( inst.rs ) )
      xcelresp_msg = s.xcelresp_q.popleft()
      s_.R[inst.rt] = xcelresp_msg.data
      s_.PC += 4

    s.isa.execute_mtx = execute_mtx
    s.isa.execute_mfx = execute_mfx
    s.isa.execute_dispatch['mtx'] = s.isa.execute_mtx
    s.isa.execute_dispatch['mfx'] = s.isa.execute_mfx

    # Reset

    s.reset_proc()

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset_proc( s ):

    # Copies of pc and inst

    s.pc   = Bits( 32, 0x00000400 )
    s.inst = Bits( 32, 0x00000000 )

    # Stats

    s.num_total_inst = 0
    s.num_inst       = 0

    s.trace = " "*29

    s.isa.reset()

  #-----------------------------------------------------------------------
  # Elaboration
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    @s.tick_fl
    def logic():

      # Wait for the go signal

      if not s.go and not s.test_en:
        return

      try:

        # Update instruction counts

        s.num_total_inst += 1
        if s.isa.stats_en:
          s.num_inst += 1

        # Set trace string in case the fetch yields

        s.trace = " "*29

        # Fetch instruction

        s.pc   = s.isa.PC.uint()
        s.inst = PisaInst( s.imem[ s.pc : s.pc+4 ] )

        # Set trace string in case the execution function yeilds

        s.trace = "#".ljust(29)

        # Execute instruction

        s.isa.execute( s.inst )

        # Ensure that the stats_en and status ports are current

        if not s.test_en:
          s.stats_en.next = s.isa.stats_en
          s.status.next   = s.isa.status

        # Trace instruction

        s.trace = "{:0>8x} {:<20}".format( s.pc, s.inst )

      except:
        print( "Unexpected error at PC={:0>8x}!".format(s.pc) )
        raise

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

