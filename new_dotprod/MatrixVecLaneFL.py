#==============================================================================
# MatrixVecLaneFL
#==============================================================================

from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle

LD_REQ_MATRIX = 0
LD_RSP_MATRIX = 1
LD_REQ_VECTOR = 2
LD_RSP_VECTOR = 3
DO_MAC_OP     = 4
ST_REQ_VECTOR = 5
ST_RSP_VECTOR = 6
IDLE          = 7

class MatrixVecLaneFL( Model ):

  def __init__( s, lane_id, memreq_params, memresp_params ):

    s.m_baseaddr = InPort( 32 )
    s.v_baseaddr = InPort( 32 )
    s.d_baseaddr = InPort( 32 )
    s.size       = InPort( 32 )

    s.go         = InPort ( 1 )
    s.done       = OutPort( 1 )

    s.req        = InValRdyBundle ( memreq_params.nbits  )
    s.resp       = OutValRdyBundle( memresp_params.nbits )

    s.lane_id        = lane_id
    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

  def elaborate_logic( s ):

    mk_req  = s.memreq_params.mk_req
    mk_resp = s.memresp_params.mk_resp
    rd      = s.memreq_params.type_read
    wr      = s.memresp_params.type_write
    data    = s.memresp_params.data_slice

    s.counter = 0
    s.state   = IDLE
    s.reg_a   = Bits( 32 )
    s.reg_b   = Bits( 32 )
    s.result  = Bits( 32 )

    @s.tick
    def logic():

      # Reset

      if s.reset:
        s.counter = 0
        s.state   = IDLE
        s.result  = Bits( 64 )
        return

      # States

      if   s.state == IDLE and not s.go:
        s.counter = 0
        s.result  = Bits( 64 )

      elif (s.state == IDLE and s.go) or s.state == LD_REQ_MATRIX:
        r_addr = s.m_baseaddr + (s.lane_id * 4 * (s.size+1)) + s.counter
        s.req.msg .next = mk_req( rd, r_addr, 0, 0 )
        s.req.val .next = 1
        s.resp.rdy.next = 1
        s.state = LD_RSP_MATRIX

      elif s.state == LD_RSP_MATRIX:
        s.req.val.next = 0
        if s.resp.val and s.resp.rdy:
          s.reg_a = s.resp.msg[ data ]
          s.state = LD_REQ_VECTOR
          s.resp.rdy.next = 0

      elif s.state == LD_REQ_VECTOR:
        v_addr = s.v_baseaddr + s.counter
        s.req .msg.next = mk_req( rd, v_addr, 0, 0 )
        s.req .val.next = 1
        s.resp.rdy.next = 1
        s.state = LD_RSP_VECTOR

      elif s.state == LD_RSP_VECTOR:
        s.req.val.next = 0
        if s.resp.val and s.resp.rdy:
          s.reg_b = s.resp.msg[ data ]
          s.state = DO_MAC_OP
          s.resp.rdy.next = 0

      elif s.state == DO_MAC_OP:
        s.result  += s.reg_a * s.reg_b
        s.counter += 4
        if s.counter == s.size * 4:
          s.state = ST_REQ_VECTOR
        else:
          s.state = LD_REQ_MATRIX

      elif s.state == ST_REQ_VECTOR:
        d_addr = s.d_baseaddr + (s.lane_id * 4)
        s.req .msg.next = mk_req( wr, d_addr, 0, s.result )
        s.req .val.next = 1
        s.resp.rdy.next = 1
        s.state = ST_RSP_VECTOR

      elif s.state == ST_RSP_VECTOR:
        s.req.val.next = 0
        if s.resp.val and s.resp.rdy:
          s.state = IDLE
          s.resp.rdy.next = 0
          s.done    .next = 1

  def line_trace( s ):
    return "{} {}".format([ 'LD_REQ_MATRIX',
                            'LD_RSP_MATRIX',
                            'LD_REQ_VECTOR',
                            'LD_RSP_VECTOR',
                            'DO_MAC_OP    ',
                            'ST_REQ_VECTOR',
                            'ST_RSP_VECTOR',
                            'IDLE',
                           ][ s.state ], s.result )


