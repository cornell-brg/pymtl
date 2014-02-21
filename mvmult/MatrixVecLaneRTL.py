#==============================================================================
# MatrixVecLaneRTL
#==============================================================================

from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle

#------------------------------------------------------------------------------
# MatrixVecLaneRTL
#------------------------------------------------------------------------------
class MatrixVecLaneRTL( Model ):

  @capture_args
  def __init__( s, lane_id, memreq_params, memresp_params ):

    s.m_baseaddr = InPort( 32 )
    s.v_baseaddr = InPort( 32 )
    s.d_baseaddr = InPort( 32 )
    s.size       = InPort( 32 )

    s.go         = InPort ( 1 )
    s.done       = OutPort( 1 )

    s.req        = OutValRdyBundle( memreq_params.nbits  )
    s.resp       = InValRdyBundle ( memresp_params.nbits )

    s.lane_id        = lane_id
    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

  def elaborate_logic( s ):

    s.dpath = MatrixVecLaneDpath( s.lane_id, s.memreq_params, s.memresp_params )
    s.ctrl  = MatrixVecLaneCtrl ( s.lane_id, s.memreq_params, s.memresp_params )

    s.connect( s.dpath.c2d, s.ctrl.c2d )

    s.connect( s.m_baseaddr, s.dpath.m_baseaddr )
    s.connect( s.v_baseaddr, s.dpath.v_baseaddr )
    s.connect( s.d_baseaddr, s.dpath.d_baseaddr )
    s.connect( s.size,       s.dpath.size       )

    s.connect( s.go,         s.ctrl.go          )
    s.connect( s.done,       s.ctrl.done        )

    s.connect( s.req.msg,    s.dpath.req.msg    )
    s.connect( s.req.val,    s.ctrl .req.val    )
    s.connect( s.req.rdy,    s.ctrl .req.rdy    )

    s.connect( s.resp.msg,   s.dpath.resp.msg   )
    s.connect( s.resp.val,   s.ctrl .resp.val   )
    s.connect( s.resp.rdy,   s.ctrl .resp.rdy   )

  def line_trace( s ):
    #return "{} {:014b} {:014b} {:014b}".format( s.ctrl.state,
    #                      s.ctrl.ctrl_signals_M0.uint(),
    #                      s.ctrl.ctrl_signals_M1.uint(),
    #                      s.ctrl.ctrl_signals_X .uint(),
    #                     )
    return "{} {} {} {}{}{} > {}{}{}{}".format( s.ctrl.state,
                               s.dpath.count,
                               'L' if s.ctrl.c2d.last_item else ' ',
                               'W' if s.ctrl.pause    else ' ',
                               'V' if s.ctrl.stall_M0 else ' ',
                               'R' if s.ctrl.stall_M1 else ' ',
                               s.ctrl.ctrl_signals_M0[0:2],
                               s.ctrl.ctrl_signals_M1[0:2],
                               s.ctrl.ctrl_signals_X [0:2],
                               s.ctrl.ctrl_signals_A [0:2],
                             )

#------------------------------------------------------------------------------
# MatrixVecLaneDpath
#------------------------------------------------------------------------------
class MatrixVecLaneDpath( Model ):

  def __init__( s, lane_id, memreq_params, memresp_params ):

    s.m_baseaddr = InPort( 32 )
    s.v_baseaddr = InPort( 32 )
    s.d_baseaddr = InPort( 32 )
    s.size       = InPort( 32 )

    s.req        = OutValRdyBundle( memreq_params.nbits  )
    s.resp       = InValRdyBundle ( memresp_params.nbits )

    s.c2d        = DpathBundle()

    s.lane_id        = lane_id
    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

  def elaborate_logic( s ):

    #--------------------------------------------------------------------------
    # Stage M0
    #--------------------------------------------------------------------------

    s.count      = Wire( 32 )
    s.base_addr  = Wire( 32 )
    s.offset     = Wire( 32 )
    s.store_data = Wire( 32 )

    s.row_addr   = Wire( 32 )
    s.vec_addr   = Wire( 32 )
    s.dst_addr   = Wire( 32 )

    s.accum_out  = Wire(32)

    m = s.memreq_params
    addr0, addrN = m.addr_slice.start, m.addr_slice.stop
    data0, dataN = m.data_slice.start, m.data_slice.stop
    len0,  lenN  = m.len_slice.start,  m.len_slice.stop
    type0, typeN = m.type_slice.start, m.type_slice.stop

    @s.combinational
    def stage_M0_comb():

      s.row_addr.value = s.m_baseaddr + (s.lane_id * s.size * 4)
      s.vec_addr.value = s.v_baseaddr
      s.dst_addr.value = s.d_baseaddr + (s.lane_id * 4)

      # base_addr mux
      if   s.c2d.baddr_sel == 0: s.base_addr.value = s.row_addr
      elif s.c2d.baddr_sel == 1: s.base_addr.value = s.vec_addr
      elif s.c2d.baddr_sel == 2: s.base_addr.value = s.dst_addr

      # offset mux
      if   s.c2d.offset_sel == 0: s.offset.value = 0
      elif s.c2d.offset_sel == 1: s.offset.value = s.count << 2

      # data mux
      if   s.c2d.data_sel == 0: s.store_data.value = 0
      elif s.c2d.data_sel == 1: s.store_data.value = s.accum_out

      # memory request
      s.req.msg[addr0:addrN].value = s.base_addr + s.offset
      s.req.msg[data0:dataN].value = s.store_data
      s.req.msg[ len0: lenN].value = 0
      s.req.msg[type0:typeN].value = s.c2d.mem_type[1]

      # last item status signal
      s.c2d.last_item.value = s.count == (s.size - 1)

    @s.posedge_clk
    def stage_M0_seq():
      if   s.c2d.count_reset: s.count.next = 0
      elif s.c2d.count_en:    s.count.next = s.count + 1

    #--------------------------------------------------------------------------
    # Stage M1
    #--------------------------------------------------------------------------

    s.reg_a = Wire( 32 )
    s.reg_b = Wire( 32 )

    @s.posedge_clk
    def stage_M1():

      if s.c2d.reg_a_en: s.reg_a.next = s.resp.msg[data0:dataN]
      if s.c2d.reg_b_en: s.reg_b.next = s.resp.msg[data0:dataN]

    #--------------------------------------------------------------------------
    # Stage X
    #--------------------------------------------------------------------------

    s.mul_out = Wire(32)
    s.mul_reg = Wire(32)

    @s.combinational
    def stage_X_comb():
      s.mul_out.value = s.reg_a * s.reg_b

    @s.posedge_clk
    def stage_X_seq():
      if s.c2d.mul_reg_en: s.mul_reg.next = s.mul_out.value

    #--------------------------------------------------------------------------
    # Stage A
    #--------------------------------------------------------------------------

    s.accum_out = Wire(32)
    s.accum_reg = Wire(32)

    @s.combinational
    def stage_A_comb():
      s.accum_out.value = s.mul_reg + s.accum_reg

    @s.posedge_clk
    def stage_X_seq():
      if s.c2d.accum_reg_en: s.accum_reg.next = s.accum_out

#------------------------------------------------------------------------------
# MatrixVecLaneCtrl
#------------------------------------------------------------------------------
IDLE        = 0
SEND_OP_LDA = 1
SEND_OP_LDB = 2
SEND_OP_ST  = 3
class MatrixVecLaneCtrl( Model ):

  def __init__( s, lane_id, memreq_params, memresp_params ):

    s.go         = InPort ( 1 )
    s.done       = OutPort( 1 )

    s.req        = OutValRdyBundle( memreq_params.nbits  )
    s.resp       = InValRdyBundle ( memresp_params.nbits )

    s.c2d        = CtrlBundle()

    s.lane_id        = lane_id
    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

  def elaborate_logic( s ):

    s.state      = Wire( 3 )
    s.state_next = Wire( 3 )

    s.pause      = Wire(1)
    s.stall_M0   = Wire(1)
    s.stall_M1   = Wire(1)

    #--------------------------------------------------------------------------
    # State Machine
    #--------------------------------------------------------------------------

    @s.posedge_clk
    def state_update():

      if   s.reset:    s.state.next = IDLE
      elif s.stall_M0: s.state.next = s.state
      else:            s.state.next = s.state_next

    @s.combinational
    def state_transition():

      send_req  = s.req .val and s.req .rdy
      recv_resp = s.resp.val and s.resp.rdy

      s.state_next.value = s.state

      if   s.state == IDLE        and s.go:
        s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_LDA and send_req:
        s.state_next.value = SEND_OP_LDB

      elif s.state == SEND_OP_LDB and send_req:
        if s.c2d.last_item:
          s.state_next.value = SEND_OP_ST
        else:
          s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_ST and send_req:
        s.state_next.value = IDLE

    #--------------------------------------------------------------------------
    # Control Signal Pipeline
    #--------------------------------------------------------------------------

    s.ctrl_signals_M0 = Wire( 14 )
    s.ctrl_signals_M1 = Wire( 14 )
    s.ctrl_signals_X  = Wire( 14 )
    s.ctrl_signals_A  = Wire( 14 )

    @s.posedge_clk
    def ctrl_regs():

      if   s.stall_M1: s.ctrl_signals_M1.next = s.ctrl_signals_M1
      elif s.stall_M0: s.ctrl_signals_M1.next = 0
      else:            s.ctrl_signals_M1.next = s.ctrl_signals_M0

      if   s.stall_M1: s.ctrl_signals_X .next = 0
      else:            s.ctrl_signals_X .next = s.ctrl_signals_M1

      s.ctrl_signals_A.next = s.ctrl_signals_X

    @s.combinational
    def state_to_ctrl():

      L = s.c2d.last_item

      # Encode signals sent down the pipeline based on State

      if   s.state == IDLE:
        s.ctrl_signals_M0[0:2].value  = 0  # baddr_sel
        s.ctrl_signals_M0[2:4].value  = 0  # offset_sel
        s.ctrl_signals_M0[  4].value  = 0  # data_sel
        s.ctrl_signals_M0[5:7].value  = 0  # mem_type
        s.ctrl_signals_M0[  7].value  = 0  # reg_a_en
        s.ctrl_signals_M0[  8].value  = 0  # reg_b_en
        s.ctrl_signals_M0[  9].value  = 0  # mul_reg_en
        s.ctrl_signals_M0[ 10].value  = 0  # accum_reg_en
        s.ctrl_signals_M0[ 11].value  = 0  # last_item
        s.ctrl_signals_M0[ 12].value  = 1  # count_reset
        s.ctrl_signals_M0[ 13].value  = 0  # count_en
      elif s.state == SEND_OP_LDA:
        s.ctrl_signals_M0[0:2].value  = 0  # baddr_sel
        s.ctrl_signals_M0[2:4].value  = 1  # offset_sel
        s.ctrl_signals_M0[  4].value  = 0  # data_sel
        s.ctrl_signals_M0[5:7].value  = 1  # mem_type
        s.ctrl_signals_M0[  7].value  = 1  # reg_a_en
        s.ctrl_signals_M0[  8].value  = 0  # reg_b_en
        s.ctrl_signals_M0[  9].value  = 0  # mul_reg_en
        s.ctrl_signals_M0[ 10].value  = 0  # accum_reg_en
        s.ctrl_signals_M0[ 11].value  = 0  # last_item
        s.ctrl_signals_M0[ 12].value  = 0  # count_reset
        s.ctrl_signals_M0[ 13].value  = 0  # count_en
      elif s.state == SEND_OP_LDB:
        s.ctrl_signals_M0[0:2].value  = 1  # baddr_sel
        s.ctrl_signals_M0[2:4].value  = 1  # offset_sel
        s.ctrl_signals_M0[  4].value  = 0  # data_sel
        s.ctrl_signals_M0[5:7].value  = 1  # mem_type
        s.ctrl_signals_M0[  7].value  = 0  # reg_a_en
        s.ctrl_signals_M0[  8].value  = 1  # reg_b_en
        s.ctrl_signals_M0[  9].value  = 1  # mul_reg_en
        s.ctrl_signals_M0[ 10].value  = 1  # accum_reg_en
        s.ctrl_signals_M0[ 11].value  = L  # last_item
        s.ctrl_signals_M0[ 12].value  = 0  # count_reset
        s.ctrl_signals_M0[ 13].value  = 1  # count_en
      elif s.state == SEND_OP_ST:
        s.ctrl_signals_M0[0:2].value  = 2  # baddr_sel
        s.ctrl_signals_M0[2:4].value  = 0  # offset_sel
        s.ctrl_signals_M0[  4].value  = 1  # data_sel
        s.ctrl_signals_M0[5:7].value  = 2  # mem_type
        s.ctrl_signals_M0[  7].value  = 0  # reg_a_en
        s.ctrl_signals_M0[  8].value  = 0  # reg_b_en
        s.ctrl_signals_M0[  9].value  = 0  # mul_reg_en
        s.ctrl_signals_M0[ 10].value  = 0  # accum_reg_en
        s.ctrl_signals_M0[ 11].value  = 0  # last_item
        s.ctrl_signals_M0[ 12].value  = 0  # count_reset
        s.ctrl_signals_M0[ 13].value  = 1  # count_en

    @s.combinational
    def ctrl_to_dpath():

      # Stall conditions

      s.pause.value = s.ctrl_signals_M0[5:7] == 2 and not s.ctrl_signals_A[11]
      req_en        = s.ctrl_signals_M0[5:7] > 0
      resp_en       = s.ctrl_signals_M1[5:7] > 0

      s.stall_M0.value = (req_en  and not s.req .rdy) or s.pause
      s.stall_M1.value = (resp_en and not s.resp.val)

      any_stall = s.stall_M0 or s.stall_M1

      # M0 Stage

      s.c2d.baddr_sel   .value = s.ctrl_signals_M0[0:2]
      s.c2d.offset_sel  .value = s.ctrl_signals_M0[2:4]
      s.c2d.data_sel    .value = s.ctrl_signals_M0[  4]
      s.c2d.count_reset .value = s.ctrl_signals_M0[ 12]
      s.c2d.count_en    .value = s.ctrl_signals_M0[ 13] and not any_stall
      s.c2d.mem_type    .value = s.ctrl_signals_M0[5:7]
      s.req.val         .value = req_en and not any_stall

      # M1 Stage

      s.c2d.reg_a_en    .value = s.ctrl_signals_M1[  7]
      s.c2d.reg_b_en    .value = s.ctrl_signals_M1[  8]
      s.resp.rdy        .value = resp_en and not s.stall_M1
      s.done            .value = s.ctrl_signals_M1[5:7] == 2 and \
                                 not s.stall_M1

      # X  Stage

      s.c2d.mul_reg_en  .value = s.ctrl_signals_X [  9]

      # A  Stage

      s.c2d.accum_reg_en.value = s.ctrl_signals_A [ 10]


#------------------------------------------------------------------------------
# CtrlDpathBundle
#------------------------------------------------------------------------------
class CtrlDpathBundle( PortBundle ):
  def __init__( s ):

    # M0 Stage Signals

    s.baddr_sel      = OutPort(2)
    s.offset_sel     = OutPort(1)
    s.data_sel       = OutPort(1)
    s.count_reset    = OutPort(1)
    s.count_en       = OutPort(1)
    s.mem_type       = OutPort(2)
    s.last_item      = InPort (1)

    # M1 Stage Signals

    s.reg_a_en       = OutPort (1)
    s.reg_b_en       = OutPort (1)

    # X Stage Signals

    s.mul_reg_en     = OutPort (1)

    # A Stage Signals

    s.accum_reg_en   = OutPort (1)

CtrlBundle, DpathBundle = create_PortBundles( CtrlDpathBundle )
