#=========================================================================
# MatrixVecCL
#=========================================================================

import collections

from new_pymtl import *
from new_pmlib import *
from new_pmlib import InValRdyBundle, OutValRdyBundle
from new_pmlib import ParentReqRespBundle, ChildReqRespBundle

from mvmult_fl   import InMatrixVecBundle,OutMatrixVecBundle
from pmlib_extra import Queue

class DotProduct (Model):

  def elaborate_logic( s ):
    pass
  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem_ifc_types, cpu_ifc_types ):

    # Interfaces

    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    # Internal state

    s.size      = 0
    s.src0_addr = 0
    s.src1_addr = 0
    s.dest_addr = 0
    s.valid     = [False] * 3

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

    # Shorter names

    s.mk_req         = s.mem_ifc.req.mk_msg
    s.rd             = 0
    s.wr             = 1
    s.data_nbytes    = s.mem_ifc.req_msg.data.nbits/8

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

    # Currently we can never really stall the response port

    s.connect( s.mem_ifc.resp_rdy, 1 )

    @s.tick
    def logic():

      # Toggle done bit

      if s.cpu_ifc.resp_val and s.cpu_ifc.resp_rdy:
        s.cpu_ifc.resp_val.next = 0
        s.valid = [False] * 3

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Check memreq
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # If memory request was accepted then pop it off memreq queue

      if s.mem_ifc.req_val and s.mem_ifc.req_rdy:
        s.memreq_queue.deq()

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Pipeline stage: X1
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_X1 = "  "
      if not s.pipe_queue_X0X1.empty():

        if s.pipe_queue_X0X1.front() == s.XACT_TYPE_L0:
          if s.mem_ifc.resp_val:
            s.pipe_queue_X0X1.deq()
            s.src0_X1 = s.mem_ifc.resp_msg.data
            s.trace_X1 = "L0"
          else:
            s.trace_X1 = "# "

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_L1:
          if s.mem_ifc.resp_val:
            s.pipe_queue_X0X1.deq()
            s.accumulator_X1 += ( s.src0_X1 * s.mem_ifc.resp_msg.data )
            s.trace_X1 = "L1"
          else:
            s.trace_X1 = "# "

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_TK:
          s.pipe_queue_X0X1.deq()
          s.token_X1 = True
          s.trace_X1 = "TK"

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_SD:
            s.pipe_queue_X0X1.deq()
            s.token_X1 = True
            s.trace_X1 = "SD"

        elif s.pipe_queue_X0X1.front() == s.XACT_TYPE_DONE:
          s.pipe_queue_X0X1.deq()
          s.cpu_ifc.resp_val.next = 1
          s.trace_X1 = "D "

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Pipeline stage: X0
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      s.trace_X0 = "  "

      s.cpu_ifc.req_rdy.next = 0
      s.mem_ifc.req_val.next   = 0

      # STATE: CMD

      if s.state == s.STATE_CMD:

        # Set output signals

        s.cpu_ifc.req_rdy.next = 1

        # Send a none transaction down the pipeline

        s.xact_type_X0X1 = s.XACT_TYPE_NONE

        # Process command

        if s.cpu_ifc.req_val and s.cpu_ifc.req_rdy:

          creg = s.cpu_ifc.req_msg.creg
          data = s.cpu_ifc.req_msg.data

          if   creg == 1:
            s.size = data
            s.valid[0] = True
            s.trace_X0 = "ws"

          elif creg == 2:
            s.src0_addr = data
            s.valid[1] = True
            s.trace_X0 = "w0"

          elif creg == 3:
            s.src1_addr = data
            s.valid[2] = True
            s.trace_X0 = "w1"

          if s.valid[0] and s.valid[1] and s.valid[2]:
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
          s.cpu_ifc.resp_msg.next = s.accumulator_X1
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
        s.mem_ifc.req_val.next = 1
        s.mem_ifc.req_msg.next = s.memreq_queue.front()
      else:
        s.mem_ifc.req_val.next = 0

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.cpu_ifc.resp_val

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.trace_X0 + "|" \
               + s.trace_X1 + ")"

