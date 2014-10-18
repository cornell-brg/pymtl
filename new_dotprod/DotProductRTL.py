from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle
from new_pmlib import ParentReqRespBundle, ChildReqRespBundle

nmul_stages = 4

class DotProductRTL( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.dpath = DotProductDpath( mem_ifc_types, cpu_ifc_types )
    s.ctrl  = DotProductCtrl ( mem_ifc_types, cpu_ifc_types )
    s.connect_auto(s.dpath, s.ctrl)

  def line_trace( s ):
    return "| {} {} {} {}|".format(s.ctrl.state, s.dpath.count, s.dpath.accum_A, s.ctrl.pause)

  def elaborate_logic( s ):
    pass
#------------------------------------------------------------------------------
# Select Constants
#------------------------------------------------------------------------------

y   = Bits( 1, 1 )
n   = Bits( 1, 0 )

# mem_type
na  = Bits( 2, 0 )
ld  = Bits( 2, 1 )
st  = Bits( 2, 2 )

load = Bits( 1, 0 )

# data_sel
#zer = Bits( 1, 0 )
acm = Bits( 1, 1 )

# offset_sel_M
zro = Bits( 1, 0 )
cnt = Bits( 1, 1 )

# baddr_sel_M
xxx = Bits( 2, 0 )
row = Bits( 2, 0 )
vec = Bits( 2, 1 )
dst = Bits( 2, 2 )

src0 = Bits( 2, 0 )

size = Bits(2, 0)
src0 = Bits(2, 1)
src1 = Bits(2, 2)

# TODO: total hack
Model.tick_rtl = Model.posedge_clk

#------------------------------------------------------------------------------
# MatrixVecLaneDpath
#------------------------------------------------------------------------------
class DotProductDpath( Model ):
  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cs      = InPort ( CtrlSignals()   )
    s.ss      = OutPort( StatusSignals() )

    #--- Stage M: Memory Request ------------------------------
    s.count       = Wire( cpu_ifc_types.req .data.nbits )
    s.size        = Wire( cpu_ifc_types.req .data.nbits )
    s.src0_addr_M = Wire( mem_ifc_types.req .addr.nbits )
    s.src1_addr_M = Wire( mem_ifc_types.req .addr.nbits )
    s.src0_data_R = Wire( mem_ifc_types.resp.data.nbits )
    s.src1_data_R = Wire( mem_ifc_types.resp.data.nbits )

    @s.tick_rtl
    def stage_seq_M():
      ctrl_msg = s.cpu_ifc.req_msg .ctrl_msg
      cpu_data = s.cpu_ifc.req_msg .data

      if s.cs.update_M:
        if   ctrl_msg == 1: s.size       .next = cpu_data
        elif ctrl_msg == 2: s.src0_addr_M.next = cpu_data
        elif ctrl_msg == 3: s.src1_addr_M.next = cpu_data
        elif ctrl_msg == 0: s.ss.go      .next = True
      else: s.ss.go.next = False

      if   s.cs.count_clear_M: s.count.next = 0
      elif s.cs.count_en_M:    s.count.next = s.count + 1

    @s.combinational
    def stage_comb_M():
      # base_addr mux
      if s.cs.baddr_sel_M == src0: base_addr_M = s.src0_addr_M
      else:                        base_addr_M = s.src1_addr_M

      # memory request
      s.mem_ifc.req_msg.type.value = 0
      s.mem_ifc.req_msg.addr.value = base_addr_M + (s.count<<2)

      # last item status signal
      s.ss.last_item_M.value = s.count == (s.size - 1)

    #--- Stage R: Memory Response -----------------------------
    @s.tick_rtl
    def stage_seq_M():
      mem_data = s.mem_ifc.resp_msg.data
      if s.cs.src0_en_R: s.src0_data_R.next = mem_data
      if s.cs.src1_en_R: s.src1_data_R.next = mem_data

    #--- Stage X: Execute Multiply ----------------------------
    s.result_X = Wire( cpu_ifc_types.req.data.nbits )

    s.mul = IntPipelinedMultiplier(
              nbits   = cpu_ifc_types.req.data.nbits,
              nstages = 4,
            )
    s.connect_dict( { s.mul.op_a    : s.src0_data_R,
                      s.mul.op_b    : s.src1_data_R,
                      s.mul.product : s.result_X } )

    #--- Stage A: Accumulate ----------------------------------
    s.accum_A   = Wire( cpu_ifc_types.resp.data.nbits )
    s.accum_out = Wire( cpu_ifc_types.resp.data.nbits )

    @s.tick_rtl
    def stage_seq_A():
      if   s.reset or s.cs.accum_clear_A:
        s.accum_A.next = 0
      elif s.cs.accum_en_A:
        s.accum_A.next = s.accum_out

    @s.combinational
    def stage_comb_A():
      s.accum_out.value = s.result_X + s.accum_A
      s.cpu_ifc.resp_msg.value = s.accum_A

  def elaborate_logic( s ):
    pass
#------------------------------------------------------------------------------
# DotProductCtrl
#------------------------------------------------------------------------------

IDLE        = 0
SEND_OP_LDA = 1
SEND_OP_LDB = 2
SEND_OP_ST  = 3
DONE        = 4

class DotProductCtrl( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):

    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cs = OutPort( CtrlSignals()   )
    s.ss = InPort ( StatusSignals() )

    s.nmul_stages = nmul_stages

    s.state      = Wire( 3 )
    s.state_next = Wire( 3 )

    s.pause      = Wire( 1 )
    s.stall_M   = Wire( 1 )
    s.stall_R   = Wire( 1 )
    s.any_stall  = Wire( 1 )
    s.valid      = Wire( 3 )

    #--------------------------------------------------------------------------
    # State Machine
    #--------------------------------------------------------------------------

    @s.posedge_clk
    def state_update_M():
      if   s.reset:    s.state.next = IDLE
      elif s.stall_M: s.state.next = s.state
      else:            s.state.next = s.state_next

    @s.combinational
    def state_transition():

      send_req  = s.mem_ifc.req_val and s.mem_ifc.req_rdy
      recv_resp = s.mem_ifc.resp_val and s.mem_ifc.resp_rdy
      go        = s.ss.go

      s.state_next.value = s.state

      if   s.state == IDLE        and go:
        s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_LDA and send_req:
        s.state_next.value = SEND_OP_LDB

      elif s.state == SEND_OP_LDB and send_req:
        if s.ss.last_item_M:
          s.state_next.value = SEND_OP_ST
        else:
          s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_ST and not s.any_stall:
        s.state_next.value = DONE

      elif s.state == DONE and s.cpu_ifc.resp_rdy:
        s.state_next.value = IDLE

    #--------------------------------------------------------------------------
    # Control Signal Pipeline
    #--------------------------------------------------------------------------

    s.ctrl_signals_M = Wire( 14 )
    s.ctrl_signals_R = Wire( 14 )
    s.ctrl_signals_X  = [Wire( 14 ) for x in range(s.nmul_stages)]
    s.ctrl_signals_A  = Wire( 14 )

    @s.posedge_clk
    def ctrl_regs():

      if   s.stall_R: s.ctrl_signals_R.next = s.ctrl_signals_R
      elif s.stall_M: s.ctrl_signals_R.next = 0
      else:            s.ctrl_signals_R.next = s.ctrl_signals_M

      if   s.stall_R: s.ctrl_signals_X[0].next = 0
      else:            s.ctrl_signals_X[0].next = s.ctrl_signals_R

      for i in range( 1, s.nmul_stages ):
        s.ctrl_signals_X[i].next = s.ctrl_signals_X[i-1]

      s.ctrl_signals_A.next = s.ctrl_signals_X[s.nmul_stages-1]

    s.L = Wire( 1 )

    @s.combinational
    def state_to_ctrl():

      # TODO: cannot infer temporaries when an inferred temporary on the RHS!
      s.L = s.ss.last_item_M

      # TODO: multiple assignments to a temporary results in duplicate decl error!
      # Encode signals sent down the pipeline based on State
      #
      #                                        up count    last acm mul b   a   mem   data  off   baddr
      #                                           en  rst  item en  en  en  en  type  sel   sel   sel
      if   s.state == IDLE:        cs = concat(y, n,  y,   n,   n,  n,  n,  n,  na,   zro,  zro,  xxx)
      elif s.state == SEND_OP_LDA: cs = concat(n, n,  n,   n,   n,  n,  n,  y,  ld,   zro,  cnt,  row)
      elif s.state == SEND_OP_LDB: cs = concat(n, y,  n, s.L,   y,  y,  y,  n,  ld,   zro,  cnt,  vec)
      elif s.state == SEND_OP_ST:  cs = concat(n, y,  n,   n,   n,  n,  n,  n,  na,   acm,  zro,  dst)
      elif s.state == DONE:        cs = concat(n, n,  n,   n,   n,  n,  n,  n,  na,   xxx,  zro,  dst)

      s.ctrl_signals_M.value = cs

      s.cpu_ifc.req_rdy.value = s.state == IDLE
      s.cpu_ifc.resp_val.value = s.state == DONE

      if s.state == DONE or s.reset:
        s.valid.value = 0

    @s.combinational
    def ctrl_to_dpath():

      # Stall conditions

      s.pause.value = s.state == SEND_OP_ST and not s.ctrl_signals_A[10]
      req_en        = s.ctrl_signals_M[4:6] > 0
      resp_en       = s.ctrl_signals_R[4:6] > 0

      s.stall_M.value = (req_en  and not s.mem_ifc.req_rdy) or s.pause
      s.stall_R.value = (resp_en and not s.mem_ifc.resp_val)

      s.any_stall.value = s.stall_M or s.stall_R

      # M Stage

      s.cs.baddr_sel_M   .value = s.ctrl_signals_M[0:2]
      s.cs.offset_sel_M  .value = s.ctrl_signals_M[  2]
      s.cs.count_clear_M .value = s.ctrl_signals_M[ 11]
      s.cs.accum_clear_A .value = s.cs.count_clear_M
      s.cs.count_en_M    .value = s.ctrl_signals_M[ 12] and not s.any_stall
      s.cs.update_M      .value = s.ctrl_signals_M[ 13] and s.cpu_ifc.req_val
      s.mem_ifc.req_val.value = req_en and not s.any_stall

      # R Stage

      s.cs.src0_en_R    .value = s.ctrl_signals_R[  6]
      s.cs.src1_en_R    .value = s.ctrl_signals_R[  7]
      s.mem_ifc.resp_rdy.value = resp_en and not s.stall_R

      # X  Stage

      for i in range( s.nmul_stages ):
        s.cs.mul_reg_en_R[i].value = s.ctrl_signals_X[i][8]

      # A Stage

      s.cs.accum_en_A.value = s.ctrl_signals_A[9]

  def elaborate_logic( s ):
    pass

#------------------------------------------------------------------------------
# CtrlDpathBundle
#------------------------------------------------------------------------------
class CtrlSignals( BitStructDefinition ):
  def __init__( s ):

    # M Stage Signals

    s.baddr_sel_M   = BitField (2)
    s.offset_sel_M  = BitField (1)
    s.count_clear_M = BitField (1)
    s.count_en_M    = BitField (1)

    # R Stage Signals

    s.src0_en_R    = BitField (1)
    s.src1_en_R    = BitField (1)

    # X Stage Signals

    s.mul_reg_en_R  = BitField (nmul_stages)

    # A Stage Signals

    s.accum_en_A    = BitField (1)
    s.accum_clear_A = BitField (1)


    #IDLE State Signals
    s.update_M         = BitField (1)

class StatusSignals( BitStructDefinition ):

  def __init__(s):
    s.last_item_M      = BitField (1)
    s.go               = BitField (1)


#------------------------------------------------------------------------------
# MatrixVecCOP_mul
#------------------------------------------------------------------------------
# A dummy multiplier module, acts as a placeholder for DesignWare components.
class IntPipelinedMultiplier( Model ):
  def __init__( s, nbits, nstages ):
    s.op_a    = InPort ( nbits )
    s.op_b    = InPort ( nbits )

    s.product = OutPort( nbits )

    s.nbits   = nbits
    s.nstages = nstages

  def elaborate_logic( s ):

    s.regs = [ Wire( s.nbits ) for x in range( s.nstages ) ]

    @s.posedge_clk
    def mult_logic():
      if s.reset:
        for i in range( s.nstages ):
          s.regs[i].next = 0
      else:
        s.regs[0].next = s.op_a * s.op_b

        for i in range( 1, s.nstages ):
          s.regs[i].next = s.regs[i-1]

    s.connect( s.product, s.regs[-1] )

