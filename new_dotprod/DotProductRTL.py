from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle
from new_pmlib import MemReqMsg, MemRespMsg

class DotProduct( Model ):

  def __init__( s, nmul_stages,
                cop_addr_nbits=5,  cop_data_nbits=32,
                mem_addr_nbits=32, mem_data_nbits=32 ):

    s.from_cpu = InValRdyBundle(cop_addr_nbits + cop_data_nbits)
    s.to_cpu   = OutValRdyBundle(cop_data_nbits)

    s.memreq  = MemReqMsg ( mem_addr_nbits, mem_data_nbits )
    s.memresp = MemRespMsg( mem_data_nbits                 )
    s.req     = OutValRdyBundle( s.memreq  )
    s.resp    = InValRdyBundle ( s.memresp )

    s.nmul_stages = nmul_stages

    s.dpath = DotProductDpath( s.nmul_stages, s.memreq, s.memresp )
    s.ctrl  = DotProductCtrl ( s.nmul_stages, s.memreq, s.memresp )

    s.connect( s.dpath.c2d,  s.ctrl.c2d )

    s.connect( s.from_cpu.rdy, s.ctrl.from_cpu.rdy  )
    s.connect( s.from_cpu.val, s.ctrl.from_cpu.val  )
    s.connect( s.from_cpu.msg, s.dpath.from_cpu.msg )

    s.connect( s.to_cpu.rdy,   s.ctrl.to_cpu.rdy    )
    s.connect( s.to_cpu.val,   s.ctrl.to_cpu.val    )
    s.connect( s.to_cpu.msg,   s.dpath.to_cpu.msg   )

    s.connect( s.req.msg,      s.dpath.req.msg      )
    s.connect( s.req.val,      s.ctrl .req.val      )
    s.connect( s.req.rdy,      s.ctrl .req.rdy      )

    s.connect( s.resp.msg,     s.dpath.resp.msg     )
    s.connect( s.resp.val,     s.ctrl .resp.val     )
    s.connect( s.resp.rdy,     s.ctrl .resp.rdy     )

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

# data_sel
#zer = Bits( 1, 0 )
acm = Bits( 1, 1 )

# offset_sel
zro = Bits( 1, 0 )
cnt = Bits( 1, 1 )

# baddr_sel
xxx = Bits( 2, 0 )
row = Bits( 2, 0 )
vec = Bits( 2, 1 )
dst = Bits( 2, 2 )

#------------------------------------------------------------------------------
# MatrixVecLaneDpath
#------------------------------------------------------------------------------
class DotProductDpath( Model ):

  def elaborate_logic( s ):
    pass

  def __init__( s, nmul_stages, memreq, memresp,
                data_nbits=32, addr_nbits=5 ):

    s.req        = OutValRdyBundle( memreq  )
    s.resp       = InValRdyBundle ( memresp )

    s.from_cpu = InValRdyBundle ( data_nbits + addr_nbits )
    s.to_cpu   = OutValRdyBundle( data_nbits )

    s.c2d = DpathBundle( nmul_stages )

    s.lane_id        = 0
    s.nmul_stages    = nmul_stages

    s.data_slice = slice( 0, data_nbits )
    s.addr_slice = slice( data_nbits, data_nbits + addr_nbits )

    s.memreq  = memreq
    s.memresp = memresp


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


    @s.combinational
    def stage_M0_comb():

      # base_addr mux
      if   s.c2d.baddr_sel == row: s.base_addr.value = s.row_addr
      elif s.c2d.baddr_sel == vec: s.base_addr.value = s.vec_addr
      elif s.c2d.baddr_sel == dst: s.base_addr.value = s.dst_addr

      # offset mux
      if   s.c2d.offset_sel == zro: s.offset.value = 0
      elif s.c2d.offset_sel == cnt: s.offset.value = s.count << 2

      # memory request
      mem_addr = s.base_addr + s.offset
      s.req.msg.value = s.memreq.mk_msg(s.c2d.mem_type[1], mem_addr,0, 0)

      # last item status signal
      s.c2d.last_item.value = s.count == (s.size - 1)

    @s.posedge_clk
    def stage_M0_seq():
      data = [s.c2d.go, s.size, s.row_addr, s.vec_addr]
      addr_t = s.from_cpu.msg[ s.addr_slice ] # this will be removed
      data_t = s.from_cpu.msg[ s.data_slice ] # same here

      if s.reset:
        for wire in data: wire.next = 0

      elif s.c2d.update:
        data[addr_t].next = data_t

      else:
        s.c2d.go.next = 0

      if   s.c2d.count_reset: s.count.next = 0
      elif s.c2d.count_en:    s.count.next = s.count + 1

    #--------------------------------------------------------------------------
    # Stage M1
    #--------------------------------------------------------------------------

    s.reg_a = Wire( 32 )
    s.reg_b = Wire( 32 )

    @s.posedge_clk
    def stage_M1():
      mem_resp = s.memresp.unpck(s.resp.msg)
      if s.c2d.reg_a_en: s.reg_a.next = mem_resp.data
      if s.c2d.reg_b_en: s.reg_b.next = mem_resp.data

    #--------------------------------------------------------------------------
    # Stage X
    #--------------------------------------------------------------------------

    s.mul_out = Wire(32)

    s.mul = MatrixVecCOP_mul( nbits=32, nstages=s.nmul_stages )
    s.connect_dict( {
     s.mul.a       : s.reg_a,
     s.mul.b       : s.reg_b,
     s.mul.product : s.mul_out,
    })
    for i in range( s.nmul_stages ):
      s.connect( s.mul.enables[i], s.c2d.mul_reg_en[i] )

    #--------------------------------------------------------------------------
    # Stage A
    #--------------------------------------------------------------------------

    s.accum_out = Wire(32)
    s.accum_reg = Wire(32)

    @s.combinational
    def stage_A_comb():
      s.accum_out.value = s.mul_out + s.accum_reg
      s.to_cpu.msg.value = s.accum_reg

    @s.posedge_clk
    def stage_A_seq():
      if   s.reset or s.c2d.count_reset: s.accum_reg.next = 0
      elif s.c2d.accum_reg_en:           s.accum_reg.next = s.accum_out
    
#------------------------------------------------------------------------------
# DotProductCtrl
#------------------------------------------------------------------------------

IDLE        = 0
SEND_OP_LDA = 1
SEND_OP_LDB = 2
SEND_OP_ST  = 3
DONE        = 4

class DotProductCtrl( Model ):

  def elaborate_logic( s ):
    pass

  def __init__( s, nmul_stages, memreq, memresp,
                data_nbits=32, addr_nbits=5 ):

    s.req  = OutValRdyBundle( memreq  )
    s.resp = InValRdyBundle ( memresp )

    s.from_cpu = InValRdyBundle ( data_nbits + addr_nbits )
    s.to_cpu   = OutValRdyBundle( data_nbits              )

    s.c2d = CtrlBundle( nmul_stages )

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
    def state_update():
      if   s.reset:    s.state.next = IDLE
      elif s.stall_M0: s.state.next = s.state
      else:            s.state.next = s.state_next

    @s.combinational
    def state_transition():

      send_req  = s.req .val and s.req .rdy
      recv_resp = s.resp.val and s.resp.rdy

      s.state_next.value = s.state

      if   s.state == IDLE        and s.c2d.go:
        s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_LDA and send_req:
        s.state_next.value = SEND_OP_LDB

      elif s.state == SEND_OP_LDB and send_req:
        if s.c2d.last_item:
          s.state_next.value = SEND_OP_ST
        else:
          s.state_next.value = SEND_OP_LDA

      elif s.state == SEND_OP_ST and not s.any_stall:
        s.state_next.value = DONE

      elif s.state == DONE and s.to_cpu.rdy:
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
      s.L = s.c2d.last_item

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

      s.from_cpu.rdy.value = s.state == IDLE
      s.to_cpu.val.value = s.state == DONE

    @s.combinational
    def ctrl_to_dpath():

      # Stall conditions

      s.pause.value = s.state == SEND_OP_ST and not s.ctrl_signals_A[10]
      req_en        = s.ctrl_signals_M0[4:6] > 0
      resp_en       = s.ctrl_signals_M1[4:6] > 0

      s.stall_M0.value = (req_en  and not s.req .rdy) or s.pause
      s.stall_M1.value = (resp_en and not s.resp.val)

      s.any_stall.value = s.stall_M0 or s.stall_M1

      # M0 Stage

      s.c2d.baddr_sel   .value = s.ctrl_signals_M0[0:2]
      s.c2d.offset_sel  .value = s.ctrl_signals_M0[  2]
      s.c2d.data_sel    .value = s.ctrl_signals_M0[  3]
      s.c2d.count_reset .value = s.ctrl_signals_M0[ 11]
      s.c2d.count_en    .value = s.ctrl_signals_M0[ 12] and not s.any_stall
      s.c2d.mem_type    .value = s.ctrl_signals_M0[4:6]
      s.c2d.update      .value = s.ctrl_signals_M0[ 13] and s.from_cpu.val
      s.req.val         .value = req_en and not s.any_stall

      # M1 Stage

      s.c2d.reg_a_en    .value = s.ctrl_signals_M1[  6]
      s.c2d.reg_b_en    .value = s.ctrl_signals_M1[  7]
      s.resp.rdy        .value = resp_en and not s.stall_M1

      # X  Stage

      for i in range( s.nmul_stages ):
        s.c2d.mul_reg_en[i].value = s.ctrl_signals_X[i][8]

      # A Stage

      s.c2d.accum_reg_en.value = s.ctrl_signals_A[9]


#------------------------------------------------------------------------------
# CtrlDpathBundle
#------------------------------------------------------------------------------
class CtrlDpathBundle( PortBundle ):
  def __init__( s, nmul_stages ):

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

    s.mul_reg_en     = OutPort (nmul_stages)

    # A Stage Signals

    s.accum_reg_en   = OutPort (1)

    #IDLE State Signals
    s.update         = OutPort (1)
    s.go             = InPort  (1)

CtrlBundle, DpathBundle = create_PortBundles( CtrlDpathBundle )

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

