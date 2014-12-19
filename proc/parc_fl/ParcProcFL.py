#=========================================================================
# ParcProcFL
#=========================================================================

import greenlet

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle, mem_msgs

from pclib.fl import (
    GreenletWrapper,  BytesMemPortProxy,
    InQueuePortProxy, OutQueuePortProxy
)

from pisa import PisaSemantics
from pisa import PisaInst

from accel.mvmult.mvmult_fl import (
     MatrixVecProxy,
     InMatrixVecBundle,
     OutMatrixVecBundle
)

class ParcProcFL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, reset_vector=0, test_en=True ):

    s.reset_vector = reset_vector
    s.test_en      = test_en

    mreq_p  = mem_msgs.MemReqParams ( 32, 32 )
    mresp_p = mem_msgs.MemRespParams( 32 )

    # TestProcManager Interface (only used when test_en=False)

    s.go        = InPort   ( 1  )
    s.status    = OutPort  ( 32 )
    s.stats_en  = OutPort  ( 1  )
    s.num_insts = OutPort  ( 32 )

    # Proc/Mngr Interface

    s.mngr2proc  = OutValRdyBundle( 32 )
    s.proc2mngr  = InValRdyBundle( 32 )

    # Instruction Memory Request/Response Interface

    s.imemreq    = OutValRdyBundle( mreq_p.nbits )
    s.imemresp   = InValRdyBundle( mresp_p.nbits )

    # Data Memory Request/Response Interface

    s.dmemreq    = OutValRdyBundle( mreq_p.nbits )
    s.dmemresp   = InValRdyBundle( mresp_p.nbits )

    # Coprocessor Interface

    s.to_cp2   = OutValRdyBundle( 5+32 )
    s.from_cp2 = InMatrixVecBundle()

    # Memory Proxy

    s.imem = BytesMemPortProxy( mreq_p, mresp_p, s.imemreq, s.imemresp )
    s.dmem = BytesMemPortProxy( mreq_p, mresp_p, s.dmemreq, s.dmemresp )

    # Queue Proxies

    s.mngr2proc_queue = InQueuePortProxy  ( s.mngr2proc )
    s.proc2mngr_queue = OutQueuePortProxy ( s.proc2mngr )

    # Accelerator Proxy

    s.xcel_mvmult = MatrixVecProxy( s.to_cp2, s.from_cp2 )

    # Construct the ISA semantics object

    s.isa = PisaSemantics( s.dmem,
                           s.mngr2proc_queue,
                           s.proc2mngr_queue,
                           s.xcel_mvmult )

    # Reset

    s.reset()

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset( s ):

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

    @s.pausable_tick
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
        print "Unexpected error at PC={:0>8x}!".format(s.pc)
        raise

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace + " " + s.xcel_mvmult.line_trace()

