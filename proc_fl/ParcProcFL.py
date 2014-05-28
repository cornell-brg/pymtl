#=========================================================================
# ParcProcFL
#=========================================================================

from   new_pymtl import *
from   new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle

import new_pmlib
import greenlet

from pisa.PisaSemantics import PisaSemantics
from pisa.PisaInst      import PisaInst

from GreenletWrapper    import GreenletWrapper
from BytesMemPortProxy  import BytesMemPortProxy
from QueuePortProxy     import InQueuePortProxy,OutQueuePortProxy

class ParcProcFL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, reset_vector=0, test_en=True ):

    s.reset_vector = reset_vector
    s.test_en      = test_en

    mreq_p  = new_pmlib.mem_msgs.MemReqParams ( 32, 32 )
    mresp_p = new_pmlib.mem_msgs.MemRespParams( 32 )

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

    # s.to_cp2   = OutValRdyBundle( 5+32 )
    # s.from_cp2 = InPort( 1 )

    # Proxies

    s.mem = BytesMemPortProxy( mreq_p, mresp_p,
                                     s.dmemreq, s.dmemresp )

    s.mngr2proc_queue = InQueuePortProxy  ( s.mngr2proc )
    s.proc2mngr_queue = OutQueuePortProxy ( s.proc2mngr )

    # Construct the ISA semantics object

    s.isa = PisaSemantics( s.mem,
                           s.mngr2proc_queue,
                           s.proc2mngr_queue )

    # Reset

    s.reset()

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset( s ):
    print "resetting"

    # Copies of pc and inst

    s.pc   = Bits( 32, 0x00000400 )
    s.inst = Bits( 32, 0x00000000 )

    # Greenlet wrapper for run function

    s.run_wrapper = GreenletWrapper(s.run)

    # Stats

    s.num_total_inst = 0
    s.num_inst       = 0

    s.trace = " "*29

    s.isa.reset()

  #-----------------------------------------------------------------------
  # Functional implementation
  #-----------------------------------------------------------------------

  def run( s ):

    while True:
      try:

        # Update instruction counts

        s.num_total_inst += 1
        if s.isa.stats_en:
          s.num_inst += 1

        # Set trace string in case the fetch yields

        s.trace = " "*29

        # Fetch instruction

        s.pc   = s.isa.PC.uint()
        s.inst = PisaInst( s.mem[ s.pc : s.pc+4 ] )

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

        # Yield so we always only execute one instruction per cycle

        greenlet.getcurrent().parent.switch(0)

      except:
        print "Unexpected error at PC={:0>8x}!".format(s.pc)
        raise

  #-----------------------------------------------------------------------
  # Elaboration
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    @s.tick
    def logic():
      if s.test_en or s.go:
        s.run_wrapper()

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

