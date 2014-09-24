from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle
from new_pmlib import ParentBundle, ChildBundle

nmul_stages = 5
class DotProduct( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):


    s.cpu_ifc = ChildBundle ( cpu_ifc_types )
    s.mem_ifc = ParentBundle( mem_ifc_types )

    s.dpath = DotProductDpath( mem_ifc_types, cpu_ifc_types )
    s.ctrl  = DotProductCtrl ( mem_ifc_types, cpu_ifc_types )

    s.auto_connect(s.dpath, s.ctrl)

  def line_trace( s ):
    return "| {} {} {} {}|".format(s.ctrl.state, s.dpath.count, s.dpath.accum_reg, s.ctrl.pause)

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

#------------------------------------------------------------------------------
# MatrixVecLaneDpath
#------------------------------------------------------------------------------
class DotProductDpath( Model ):

  def __init__( s, mem_ifc_types, cpu_ifc_types ):

    s.cpu_ifc = ChildBundle ( cpu_ifc_types )
    s.mem_ifc = ParentBundle( mem_ifc_types )

    s.cs = InPort ( CtrlSignals()   )
    s.ss = OutPort( StatusSignals() )

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
    s.size       = Wire( 32 )

    s.accum_out  = Wire( 32 )

    s.mem_addr   = Wire( 32 )


    @s.combinational
    def stage_M0_comb():

      # base_addr mux
      if   s.cs.baddr_sel_M0 == row: s.base_addr.value = s.row_addr
      elif s.cs.baddr_sel_M0 == vec: s.base_addr.value = s.vec_addr

      # offset mux
      if   s.cs.offset_sel_M0 == zro: s.offset.value = 0
      elif s.cs.offset_sel_M0 == cnt: s.offset.value = s.count << 2

      # memory request
      s.mem_addr.value = s.base_addr + s.offset
      s.mem_ifc.p2c_msg.data.value = 0
      s.mem_ifc.p2c_msg.addr.value = s.mem_addr
      s.mem_ifc.p2c_msg.type.value = load
      s.mem_ifc.p2c_msg.len .value = 0

      # last item status signal
      s.ss.last_item_M0.value = s.count == (s.size - 1)

    @s.posedge_clk
    def stage_M0_seq():
      addr = s.cpu_ifc.p2c_msg.addr
      data = s.cpu_ifc.p2c_msg.data

      if s.reset:
        s.ss.go_M0   .next = 0
        s.size    .next = 0
        s.row_addr.next = 0
        s.vec_addr.next = 0

      elif s.cs.update_M0:
        if   addr == 0: s.ss.go_M0   .next = data
        elif addr == 1: s.size    .next = data
        elif addr == 2: s.row_addr.next = data
        elif addr == 3: s.vec_addr.next = data

      else:
        s.ss.go_M0.next = 0

      if   s.cs.count_reset_M0: s.count.next = 0
      elif s.cs.count_en_M0:    s.count.next = s.count + 1

    #--------------------------------------------------------------------------
    # Stage M1
    #--------------------------------------------------------------------------

    s.reg_a = Wire( 32 )
    s.reg_b = Wire( 32 )

    @s.posedge_clk
    def stage_M1():
      if s.cs.reg_a_en_M1: s.reg_a.next = s.mem_ifc.c2p_msg.data
      if s.cs.reg_b_en_M1: s.reg_b.next = s.mem_ifc.c2p_msg.data

    #--------------------------------------------------------------------------
    # Stage X
    #--------------------------------------------------------------------------

    s.mul_out = Wire(32)

    s.mul = MatrixVecCOP_mul( nbits=32, nstages=nmul_stages )
    s.connect_dict( {
     s.mul.a       : s.reg_a,
     s.mul.b       : s.reg_b,
     s.mul.product : s.mul_out,
    })
    for i in range( nmul_stages ):
      s.connect( s.mul.enables[i], s.cs.mul_reg_en_M1[i] )

    #--------------------------------------------------------------------------
    # Stage A
    #--------------------------------------------------------------------------

    s.accum_out = Wire(32)
    s.accum_reg = Wire(32)

    @s.combinational
    def stage_A_comb():
      s.accum_out.value = s.mul_out + s.accum_reg
      s.cpu_ifc.c2p_msg.value = s.accum_reg

    @s.posedge_clk
    def stage_A_seq():
      if   s.reset or s.cs.count_reset_A:  s.accum_reg.next = 0
      elif s.cs.accum_reg_en_A:            s.accum_reg.next = s.accum_out
    

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

    s.cpu_ifc = ChildBundle ( cpu_ifc_types )
    s.mem_ifc = ParentBundle( mem_ifc_types )

    s.cs = OutPort( CtrlSignals()   )
    s.ss = InPort ( StatusSignals() )

    s.nmul_stages = nmul_stages

  

    s.state      = Wire( 3 )
    s.state_next = Wire( 3 )

    s.pause      = Wire( 1 )
    s.stall_M0   = Wire( 1 )
    s.stall_M1   = Wire( 1 )
    s.any_stall  = Wire( 1 )

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

      send_req  = s.mem_ifc.p2c_val and s.mem_ifc.p2c_rdy
      recv_resp = s.mem_ifc.c2p_val and s.mem_ifc.c2p_rdy

      s.state_next.value = s.state

      if   s.state == IDLE        and s.ss.go_M0:
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

      elif s.state == DONE and s.cpu_ifc.c2p_rdy:
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

      s.cpu_ifc.p2c_rdy.value = s.state == IDLE
      s.cpu_ifc.c2p_val.value = s.state == DONE

    @s.combinational
    def ctrl_to_dpath():

      # Stall conditions

      s.pause.value = s.state == SEND_OP_ST and not s.ctrl_signals_A[10]
      req_en        = s.ctrl_signals_M0[4:6] > 0
      resp_en       = s.ctrl_signals_M1[4:6] > 0

      s.stall_M0.value = (req_en  and not s.mem_ifc.p2c_rdy) or s.pause
      s.stall_M1.value = (resp_en and not s.mem_ifc.c2p_val)

      s.any_stall.value = s.stall_M0 or s.stall_M1

      # M0 Stage

      s.cs.baddr_sel_M0   .value = s.ctrl_signals_M0[0:2]
      s.cs.offset_sel_M0  .value = s.ctrl_signals_M0[  2]
      s.cs.count_reset_M0 .value = s.ctrl_signals_M0[ 11]
      s.cs.count_reset_A  .value = s.cs.count_reset_M0
      s.cs.count_en_M0    .value = s.ctrl_signals_M0[ 12] and not s.any_stall
      s.cs.update_M0      .value = s.ctrl_signals_M0[ 13] and s.cpu_ifc.p2c_val
      s.mem_ifc.p2c_val.value = req_en and not s.any_stall

      # M1 Stage

      s.cs.reg_a_en_M1    .value = s.ctrl_signals_M1[  6]
      s.cs.reg_b_en_M1    .value = s.ctrl_signals_M1[  7]
      s.mem_ifc.c2p_rdy.value = resp_en and not s.stall_M1

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

    s.reg_a_en_M1    = BitField (1)
    s.reg_b_en_M1    = BitField (1)

    # X Stage Signals

    s.mul_reg_en_M1  = BitField (nmul_stages)

    # A Stage Signals

    s.accum_reg_en_A = BitField (1)
    s.count_reset_A  = BitField (1)


    #IDLE State Signals
    s.update_M0         = BitField (1)

class StatusSignals( BitStructDefinition ):
  def __init__(s):
    s.go_M0             = BitField (1)
    s.last_item_M0      = BitField (1)
    

#------------------------------------------------------------------------------
# MatrixVecCOP_mul
#------------------------------------------------------------------------------
# A dummy multiplier module, acts as a placeholder for DesignWare components.
class MatrixVecCOP_mul( Model ):
  def __init__( s, nbits, nstages ):
    s.a       = InPort ( nbits )
    s.b       = InPort ( nbits )
    s.enables = InPort ( nstages )
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

        if s.enables[0]:
          s.regs[0].next = s.a * s.b

        for i in range( 1, s.nstages ):
          if s.enables[i]:
            s.regs[i].next = s.regs[i-1]

    s.connect( s.product, s.regs[-1] )

