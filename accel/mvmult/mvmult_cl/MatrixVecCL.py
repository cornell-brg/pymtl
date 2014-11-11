#=========================================================================
# MatrixVecCL
#=========================================================================

import collections

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle, mem_msgs
from pclib.fl     import Queue
from ..mvmult_fl  import InMatrixVecBundle, OutMatrixVecBundle

class MatrixVecCL (Model):

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

    # Shorter names

    s.mk_req         = s.mreq_p.mk_req
    s.mk_resp        = s.mresp_p.mk_resp
    s.rd             = s.mreq_p.type_read
    s.wr             = s.mresp_p.type_write
    s.data_slice     = s.mresp_p.data_slice
    s.data_nbytes    = s.mreq_p.data_nbits/8

    # COP interface

    s.from_cpu  = InValRdyBundle( s.addr_nbits + s.data_nbits )
    s.to_cpu    = OutMatrixVecBundle()

    # Memory request/response ports

    s.memreq  = InValRdyBundle  ( s.mreq_p.nbits  )
    s.memresp = OutValRdyBundle ( s.mresp_p.nbits )

    # Internal state

    s.size      = 0
    s.src0_addr = 0
    s.src1_addr = 0
    s.dest_addr = 0

    # Pipeline state

    s.src0_X1        = 0
    s.accumulator_X1 = 0
    s.token_X1       = False

    # State for X0 stage

    s.STATE_CMD   = 0
    s.STATE_L0    = 1
    s.STATE_L1    = 2
    s.STATE_TK    = 3
    s.STATE_WAIT1 = 4
    s.STATE_SD    = 5
    s.STATE_WAIT2 = 6
    s.STATE_DONE  = 7
    s.state       = s.STATE_CMD

    # Types of transactions that can go down the pipeline

    s.XACT_TYPE_NONE = "  "
    s.XACT_TYPE_L0   = "L0"
    s.XACT_TYPE_L1   = "L1"
    s.XACT_TYPE_TK   = "TK"
    s.XACT_TYPE_SD   = "SD"
    s.XACT_TYPE_DONE = "D "

    s.memreq_queue    = Queue(1)
    s.pipe_queue_X0X1 = Queue(4)

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    # Currently we can never really stall the response port

    s.connect( s.memresp.rdy, 1 )

    @s.tick
    def logic():

      # Toggle done bit

      if s.to_cpu.done:
        s.to_cpu.done.next = 0

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Check memreq
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # If memory request was accepted then pop it off memreq queue

      if s.memreq.val and s.memreq.rdy:
        s.memreq_queue.deq()

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Pipeline stage: X1
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.to_cpu.done.next = 0

      s.trace_X1 = "  "
      if not s.pipe_queue_X0X1.empty():

        if s.pipe_queue_X0X1.front() == s.XACT_TYPE_L0:
          if s.memresp.val:
            s.pipe_queue_X0X1.deq()
            s.src0_X1 = s.memresp.msg[0:32]
            s.trace_X1 = "L0"
          else:
            s.trace_X1 = "# "

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_L1:
          if s.memresp.val:
            s.pipe_queue_X0X1.deq()
            s.accumulator_X1 += ( s.src0_X1 * s.memresp.msg[0:32] )
            s.trace_X1 = "L1"
          else:
            s.trace_X1 = "# "

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_TK:
          s.pipe_queue_X0X1.deq()
          s.token_X1 = True
          s.trace_X1 = "TK"

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_SD:
          if s.memresp.val:
            s.pipe_queue_X0X1.deq()
            s.token_X1 = True
            s.trace_X1 = "SD"
          else:
            s.trace_X1 = "# "

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_DONE:
          s.pipe_queue_X0X1.deq()
          s.to_cpu.done.next = 1
          s.trace_X1 = "D "

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Pipeline stage: X0
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_X0 = "  "

      s.from_cpu.rdy.next = 0
      s.memreq.val.next   = 0

      # STATE: CMD

      if s.state == s.STATE_CMD:

        # Set output signals

        s.from_cpu.rdy.next = 1

        # Send a none transaction down the pipeline

        s.xact_type_X0X1 = s.XACT_TYPE_NONE

        # Process command

        if s.from_cpu.val and s.from_cpu.rdy:

          addr = s.from_cpu.msg[s.data_nbits:s.from_cpu.msg.nbits]
          data = s.from_cpu.msg[0:s.data_nbits]

          if   addr == 1:
            s.size = data
            s.trace_X0 = "ws"

          elif addr == 2:
            s.src0_addr = data
            s.trace_X0 = "w0"

          elif addr == 3:
            s.src1_addr = data
            s.trace_X0 = "w1"

          elif addr == 4:
            s.dest_addr = data
            s.trace_X0 = "wd"

          elif addr == 0 and data == 1:
            s.state    = s.STATE_L0
            s.counter  = s.size
            s.trace_X0 = "go"
            s.token_X1 = False
            s.accumulator_X1 = 0

      # STATE: L0

      elif s.state == s.STATE_L0:

        if s.memreq_queue.full() and s.pipe_queue_X0X1.full():
          s.trace_X0 = "#X"
        elif s.memreq_queue.full():
          s.trace_X0 = "#m"
        elif s.pipe_queue_X0X1.full():
          s.trace_X0 = "#x"
        else:

          s.memreq_queue.enq( s.mk_req( s.rd, s.src0_addr, 0, 0 ) )
          s.pipe_queue_X0X1.enq( s.XACT_TYPE_L0 )
          s.src0_addr += 4
          s.state     = s.STATE_L1
          s.trace_X0  = "L0"

      # STATE: L1

      elif s.state == s.STATE_L1:

        if s.memreq_queue.full() and s.pipe_queue_X0X1.full():
          s.trace_X0 = "#X"
        elif s.memreq_queue.full():
          s.trace_X0 = "#m"
        elif s.pipe_queue_X0X1.full():
          s.trace_X0 = "#x"
        else:

          s.memreq_queue.enq( s.mk_req( s.rd, s.src1_addr, 0, 0 ) )
          s.pipe_queue_X0X1.enq( s.XACT_TYPE_L1 )

          s.src1_addr += 4
          s.counter   -= 1
          s.state     = s.STATE_L0
          s.trace_X0  = "L1"

        # Move to SD state if we have finished

        if s.counter == 0:
          s.state = s.STATE_TK

      # STATE: SEND_TK

      elif s.state == s.STATE_TK:

        if s.pipe_queue_X0X1.full():
          s.trace_X0 = "#x"
        else:
          s.pipe_queue_X0X1.enq( s.XACT_TYPE_TK )
          s.state    = s.STATE_WAIT1
          s.trace_X0 = "TK"

      # STATE: WAIT1

      elif s.state == s.STATE_WAIT1:
        s.trace_X0 = "W "
        if s.token_X1:
          s.token_X1 = False
          s.state    = s.STATE_SD

      # STATE: SD

      elif s.state == s.STATE_SD:

        if s.memreq_queue.full() and s.pipe_queue_X0X1.full():
          s.trace_X0 = "#X"
        elif s.memreq_queue.full():
          s.trace_X0 = "#m"
        elif s.pipe_queue_X0X1.full():
          s.trace_X0 = "#x"
        else:

          data = Bits( 32, s.accumulator_X1, trunc=True )
          s.memreq_queue.enq( s.mk_req( s.wr, s.dest_addr, 0, data ) )
          s.pipe_queue_X0X1.enq( s.XACT_TYPE_SD )

          s.state     = s.STATE_WAIT2
          s.trace_X0  = "SD"

      # STATE: WAIT2

      elif s.state == s.STATE_WAIT2:
        s.trace_X0 = "W "
        if s.token_X1:
          s.token_X1 = False
          s.state = s.STATE_DONE

      # STATE: DONE

      elif s.state == s.STATE_DONE:

        if s.pipe_queue_X0X1.full():
          s.trace_X0 = "#x"
        else:
          s.pipe_queue_X0X1.enq( s.XACT_TYPE_DONE )
          s.state    = s.STATE_CMD
          s.trace_X0 = "D "

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Send out memreq
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      if not s.memreq_queue.empty():
        s.memreq.val.next = 1
        s.memreq.msg.next = s.memreq_queue.front()
      else:
        s.memreq.val.next = 0

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.to_cpu.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.trace_X0 + "|" \
               + s.trace_X1 + ")"

