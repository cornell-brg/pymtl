#=========================================================================
# VVAddUnitBL
#=========================================================================
# This model implements a hardware unit that does an element-wise sum on
# two vectors in memory, storing the result to a third vector in memory.
# We initialize the model with the base addresses and the length.
# Eventually we could add a message based interface to configure the unit
# and then to read out the result.
#
# We use a finite-state machine to handle the split-phase memory
# request/response interface.

from new_pymtl import *
from new_pmlib import *

# FSM states

SRC0_REQ = 0
SRC0_RSP = 1
SRC1_REQ = 2
SRC1_RSP = 3
DEST_REQ = 4
DEST_RSP = 5
DONE     = 6

class VVAddUnitBL (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params,
                dest_addr, src0_addr, src1_addr, size ):

    # Save parameters

    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params
    s.dest_addr      = dest_addr
    s.src0_addr      = src0_addr
    s.src1_addr      = src1_addr
    s.size           = size

    # Memory request/response ports

    s.memreq  = InValRdyBundle  ( memreq_params.nbits  )
    s.memresp = OutValRdyBundle ( memresp_params.nbits )

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    # Short names

    mk_req     = s.memreq_params.mk_req
    mk_resp    = s.memresp_params.mk_resp
    rd         = s.memreq_params.type_read
    wr         = s.memresp_params.type_write
    data_slice = s.memresp_params.data_slice

    # State

    s.counter  = 0
    s.state    = SRC0_REQ
    s.src0_elm = 0
    s.src1_elm = 0

    @s.tick
    def logic():

      if s.reset:
        s.counter = 0
        s.state   = SRC0_REQ
        return

      # Send out the memory request for the src0 array

      if s.state == SRC0_REQ:
        r_addr = s.src0_addr + (s.counter * 4)
        s.memreq.msg.next  = mk_req( rd, r_addr, 0, 0 )
        s.memreq.val.next  = 1
        s.memresp.rdy.next = 1
        s.state = SRC0_RSP

      # Wait for the memory response for the src0 array

      elif s.state == SRC0_RSP:

        if s.memresp.val and s.memresp.rdy:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 0
          s.src0_elm = s.memresp.msg[ data_slice ].uint()
          s.state = SRC1_REQ

        else:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 1

      # Send out the memory request for the src1 array

      elif s.state == SRC1_REQ:
        r_addr = s.src1_addr + (s.counter * 4)
        s.memreq.msg.next  = mk_req( rd, r_addr, 0, 0 )
        s.memreq.val.next  = 1
        s.memresp.rdy.next = 1
        s.state = SRC1_RSP

      # Wait for the memory response for the src1 array

      elif s.state == SRC1_RSP:

        if s.memresp.val and s.memresp.rdy:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 0
          s.src1_elm = s.memresp.msg[ data_slice ].uint()
          s.state = DEST_REQ

        else:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 1

      # Send out the memory request for the dest array

      elif s.state == DEST_REQ:
        result = s.src0_elm + s.src1_elm
        w_addr = s.dest_addr + (s.counter * 4)
        s.memreq.msg.next  = mk_req( wr, w_addr, 0, result )
        s.memreq.val.next  = 1
        s.memresp.rdy.next = 1
        s.state = DEST_RSP

      # Wait for the memory response for the dest array

      elif s.state == DEST_RSP:

        if s.memresp.val and s.memresp.rdy:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 0

          # If this is the last element then we are done, otherwise
          # increment the counter and go back to requesting the next
          # element of the src0 array.

          if s.counter < s.size:
            s.counter += 1
            s.state = SRC0_REQ
          else:
            s.state = DONE

        else:
          s.memreq.val.next  = 0
          s.memresp.rdy.next = 1

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.state == DONE

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{}" \
      .format( [ 'SRC0_REQ', 'SRC0_RSP',
                 'SRC1_REQ', 'SRC1_RSP',
                 'DEST_REQ', 'DEST_RSP',
                 'DONE    ' ][ s.state ] )

