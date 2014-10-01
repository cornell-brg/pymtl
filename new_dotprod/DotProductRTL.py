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
    return "| {} {} {} {}|".format(s.ctrl.state, s.dpath.count, s.dpath.accum_reg_A, s.ctrl.pause)

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

# offset_sel_M0
zro = Bits( 1, 0 )
cnt = Bits( 1, 1 )

# baddr_sel_M0
xxx = Bits( 2, 0 )
row = Bits( 2, 0 )
vec = Bits( 2, 1 )
dst = Bits( 2, 2 )

size = Bits(2, 0)
src0 = Bits(2, 1)
src1 = Bits(2, 2)

#------------------------------------------------------------------------------
# MatrixVecLaneDpath
#------------------------------------------------------------------------------
class DotProductDpath( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):
    s.cpu_ifc = ChildReqRespBundle ( cpu_ifc_types )
    s.mem_ifc = ParentReqRespBundle( mem_ifc_types )

    s.cs = InPort ( CtrlSignals()   )
    s.ss = OutPort( StatusSignals() )

    #--- Stage M --------------------------------------------------------

    s.count       = Wire ( cpu_ifc_types.req.data.nbits  )
    s.size        = Wire ( cpu_ifc_types.req.data.nbits  )
    s.scr0_addr_M = Wire ( mem_ifc_types.req.addr.nbits  )
    s.src1_addr_M = Wire ( mem_ifc_types.req.addr.nbits  )
    s.src0_data_M = Wire ( mem_ifc_types.resp.data.nbits )
    s.src1_data_M = Wire ( mem_ifc_types.resp.data.nbits )

    @s.posedge_clk
    def stage_M0_seq():
      creg = s.cpu_ifc.req_msg.creg
      if s.cs.update_M0:
        if   creg == 1: s.size       .next = s.cpu_ifc.req_msg.data
        elif creg == 2: s.scr0_addr_M.next = s.cpu_ifc.req_msg.data
        elif creg == 3: s.src1_addr_M.next = s.cpu_ifc.req_msg.data
        elif creg == 0: s.ss.go      .next = True

      if   s.cs.count_reset_M0: s.count.next = 0
      elif s.cs.count_en_M0:    s.count.next = s.count + 1

      if s.cs.src0_en_M1: s.src0_data_M.next = s.mem_ifc.resp_msg.data
      if s.cs.src1_en_M1: s.src1_data_M.next = s.mem_ifc.resp_msg.data

    @s.combinational
    def stage_M0_comb():
      # base_addr mux
      if   s.cs.baddr_sel_M0 == row: base_addr_M = s.scr0_addr_M
      else:                          base_addr_M = s.src1_addr_M

      # memory request
      s.mem_ifc.req_msg.value = 0
      s.mem_ifc.req_msg.addr.value = base_addr_M + (s.count << 2)

      # last item status signal
      s.ss.last_item_M0.value = s.count == (s.size - 1)

    #--- Stage X ---------------------------------------------------------

    s.result_X = Wire( cpu_ifc_types.req.data.nbits )

    s.mul = IntPipelinedMultiplier( nbits=cpu_ifc_types.req.data.nbits,
                                    nstages=4 )
    s.connect_dict( { s.mul.op_a       : s.src0_data_M,
                      s.mul.op_b       : s.src1_data_M,
                      s.mul.product    : s.result_X } )

    #--- Stage A ----------------------------------------------------------

    s.accum_out   = Wire( cpu_ifc_types.resp.data.nbits )
    s.accum_reg_A = Wire( cpu_ifc_types.resp.data.nbits )

    @s.posedge_clk
    def stage_A_seq():
      if   s.reset or s.cs.count_reset_A:  s.accum_reg_A.next = 0
      elif s.cs.accum_reg_en_A:            s.accum_reg_A.next = s.accum_out

    @s.combinational
    def stage_A_comb():
      s.accum_out.value = s.result_X + s.accum_reg_A
      s.cpu_ifc.resp_msg.value = s.accum_reg_A

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
    s.stall_M0   = Wire( 1 )
    s.stall_M1   = Wire( 1 )
    s.any_stall  = Wire( 1 )
    s.valid      = Wire( 3 )

    #--------------------------------------------------------------------------
    # State Machine
    #--------------------------------------------------------------------------

    @s.posedge_clk
    def state_update_M0():
      if   s.reset:    s.state.next = IDLE
      elif s.stall_M0: s.state.next = s.state
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
        if s.ss.last_item_M0:
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

    s.ctrl_signals_M0 = Wire( 14 )
    s.ctrl_signals_M1 = Wire( 14 )
    s.ctrl_signals_X  = [Wire( 14 ) for x in range(s.nmul_stages)]
    s.ctrl_signals_A  = Wire( 14 )

    @s.posedge_clk
    def ctrl_regs():

      if   s.stall_M1: s.ctrl_signals_M1.next = s.ctrl_signals_M1
      elif s.stall_M0: s.ctrl_signals_M1.next = 0
      else:            s.ctrl_signals_M1.next = s.ctrl_signals_M0

      if   s.stall_M1: s.ctrl_signals_X[0].next = 0
      else:            s.ctrl_signals_X[0].next = s.ctrl_signals_M1

      for i in range( 1, s.nmul_stages ):
        s.ctrl_signals_X[i].next = s.ctrl_signals_X[i-1]

      s.ctrl_signals_A.next = s.ctrl_signals_X[s.nmul_stages-1]

    s.L = Wire( 1 )

    @s.combinational
    def state_to_ctrl():

      # TODO: cannot infer temporaries when an inferred temporary on the RHS!
      s.L = s.ss.last_item_M0

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

      s.ctrl_signals_M0.value = cs

      s.cpu_ifc.req_rdy.value = s.state == IDLE
      s.cpu_ifc.resp_val.value = s.state == DONE

      if s.state == DONE or s.reset:
        s.valid.value = 0

    @s.combinational
    def ctrl_to_dpath():

      # Stall conditions

      s.pause.value = s.state == SEND_OP_ST and not s.ctrl_signals_A[10]
      req_en        = s.ctrl_signals_M0[4:6] > 0
      resp_en       = s.ctrl_signals_M1[4:6] > 0

      s.stall_M0.value = (req_en  and not s.mem_ifc.req_rdy) or s.pause
      s.stall_M1.value = (resp_en and not s.mem_ifc.resp_val)

      s.any_stall.value = s.stall_M0 or s.stall_M1

      # M0 Stage

      s.cs.baddr_sel_M0   .value = s.ctrl_signals_M0[0:2]
      s.cs.offset_sel_M0  .value = s.ctrl_signals_M0[  2]
      s.cs.count_reset_M0 .value = s.ctrl_signals_M0[ 11]
      s.cs.count_reset_A  .value = s.cs.count_reset_M0
      s.cs.count_en_M0    .value = s.ctrl_signals_M0[ 12] and not s.any_stall
      s.cs.update_M0      .value = s.ctrl_signals_M0[ 13] and s.cpu_ifc.req_val
      s.mem_ifc.req_val.value = req_en and not s.any_stall

      # M1 Stage

      s.cs.src0_en_M1    .value = s.ctrl_signals_M1[  6]
      s.cs.src1_en_M1    .value = s.ctrl_signals_M1[  7]
      s.mem_ifc.resp_rdy.value = resp_en and not s.stall_M1

      # X  Stage

      for i in range( s.nmul_stages ):
        s.cs.mul_reg_en_M1[i].value = s.ctrl_signals_X[i][8]

      # A Stage

      s.cs.accum_reg_en_A.value = s.ctrl_signals_A[9]

  def elaborate_logic( s ):
    pass

#------------------------------------------------------------------------------
# CtrlDpathBundle
#------------------------------------------------------------------------------
class CtrlSignals( BitStructDefinition ):
  def __init__( s ):

    # M0 Stage Signals

    s.baddr_sel_M0   = BitField (2)
    s.offset_sel_M0  = BitField (1)
    s.count_reset_M0 = BitField (1)
    s.count_en_M0    = BitField (1)

    # M1 Stage Signals

    s.src0_en_M1    = BitField (1)
    s.src1_en_M1    = BitField (1)

    # X Stage Signals

    s.mul_reg_en_M1  = BitField (nmul_stages)

    # A Stage Signals

    s.accum_reg_en_A = BitField (1)
    s.count_reset_A  = BitField (1)


    #IDLE State Signals
    s.update_M0         = BitField (1)

class StatusSignals( BitStructDefinition ):

  def __init__(s):
    s.last_item_M0      = BitField (1)
    s.go                = BitField (1)
    

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

