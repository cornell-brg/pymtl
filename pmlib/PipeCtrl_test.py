#=========================================================================
# PipeCtrl Unit Test
#=========================================================================
# We create a incrementer pipeline (IncrPipe) to test the PipeCtrl unit by
# instantiating it in the control unit of the IncrPipe model. The pipeline
# has 5 stages: A, B, C, D, E. Frontend of the pipeline is attached to a
# TestSource model and Backend is attached to a TestSink. Datapath has an
# incrementer in C,D,E stages. We assume that we can never originate a
# stall in B stage. B stage sends the control word to the control unit
# based on the transaction it is currently processing. TestSource contains
# the transaction as below:
#
#  Transaction Format:
#
#  16          14 13          11 10           8 7         0
#  +-------------+--------------+--------------+-----------+
#  | stall_stage | stall_cycles | squash_stage | value     |
#  +-------------+--------------+--------------+-----------+
#
# stall_stage  : indicates the stage where we want to originate a stall
# stall_cycles : number of cycles we want to stall for
# squash_stage : indicates the stage where we want to originate a squash
# value        : 8-bit value which the datapath increments
#
# TestSink merely holds the expected value based on the increments

from pymtl import *
import pmlib

# Constants

TRANSACTION_NBITS = 17

STAGE_A           = 0
STAGE_B           = 1
STAGE_C           = 2
STAGE_D           = 3
STAGE_E           = 4

VALUE             = slice(  0, 8  )
CW                = slice(  8, 17 )
SQUASH_STAGE      = slice(  8, 11 )
STALL_CYCLES      = slice( 11, 14 )
STALL_STAGE       = slice( 14, 17 )
CW_SQUASH_STAGE   = slice(  0, 3  )
CW_STALL_CYCLES   = slice(  3, 6  )
CW_STALL_STAGE    = slice(  6, 9  )

#-------------------------------------------------------------------------
# 5-stage Incrementer Pipeline Datapath
#-------------------------------------------------------------------------

class IncrPipeDpath (Model):

  def __init__( self, nbits ):

    # Interface Ports

    self.in_msg    = InPort  ( TRANSACTION_NBITS )
    self.out_msg   = OutPort ( nbits )

    # Ctrl Signals (ctrl -> dpath)

    self.a_reg_en  = InPort  ( 1 )
    self.b_reg_en  = InPort  ( 1 )
    self.c_reg_en  = InPort  ( 1 )
    self.d_reg_en  = InPort  ( 1 )
    self.e_reg_en  = InPort  ( 1 )

    # Status Signals (ctrl <- dpath)

    self.inst_b    = OutPort ( 9 )

    #---------------------------------------------------------------------
    # A Stage
    #---------------------------------------------------------------------

    self.a_reg  = pmlib.regs.RegEn( TRANSACTION_NBITS )

    # input msg coming from the TestSource

    connect( self.a_reg.in_, self.in_msg    )
    connect( self.a_reg.en,  self.a_reg_en  )

    #---------------------------------------------------------------------
    # B Stage
    #---------------------------------------------------------------------

    self.b_reg  = pmlib.regs.RegEn( TRANSACTION_NBITS )

    connect( self.b_reg.in_,     self.a_reg.out )
    connect( self.b_reg.en,      self.b_reg_en  )

    # send the control word for the tranaction

    connect( self.b_reg.out[CW], self.inst_b    )

    #---------------------------------------------------------------------
    # C Stage
    #---------------------------------------------------------------------

    self.c_reg  = pmlib.regs.RegEn( nbits )

    connect( self.c_reg.in_, self.b_reg.out[VALUE] )
    connect( self.c_reg.en,  self.c_reg_en         )

    self.c_incr = pmlib.arith.Incrementer( nbits, increment_amount = 1 )

    connect( self.c_incr.in_, self.c_reg.out )

    #---------------------------------------------------------------------
    # D Stage
    #---------------------------------------------------------------------

    self.d_reg  = pmlib.regs.RegEn( nbits )

    connect( self.d_reg.in_, self.c_incr.out )
    connect( self.d_reg.en,  self.d_reg_en   )

    self.d_incr = pmlib.arith.Incrementer( nbits, increment_amount = 1 )

    connect( self.d_incr.in_, self.d_reg.out )

    #---------------------------------------------------------------------
    # E Stage
    #---------------------------------------------------------------------

    self.e_reg  = pmlib.regs.RegEn( nbits )

    connect( self.e_reg.in_, self.d_incr.out )
    connect( self.e_reg.en,  self.e_reg_en   )

    self.e_incr = pmlib.arith.Incrementer( nbits, increment_amount = 1 )

    connect( self.e_incr.in_, self.e_reg.out )

    # value we write to the Sink

    connect( self.e_incr.out, self.out_msg   )

#-------------------------------------------------------------------------
# 5-stage Incrementer Pipeline Control
#-------------------------------------------------------------------------

class IncrPipeCtrl (Model):

  def __init__( self ):

    # Interface Ports

    self.in_val    = InPort  ( 1 )
    self.in_rdy    = OutPort ( 1 )

    self.out_val   = OutPort ( 1 )
    self.out_rdy   = InPort  ( 1 )

    # Ctrl Signals (ctrl -> dpath )

    self.a_reg_en  = OutPort  ( 1 )
    self.b_reg_en  = OutPort  ( 1 )
    self.c_reg_en  = OutPort  ( 1 )
    self.d_reg_en  = OutPort  ( 1 )
    self.e_reg_en  = OutPort  ( 1 )

    # Status Signals (ctrl <- dpath)

    self.inst_b    = InPort   ( 9 )

    #---------------------------------------------------------------------
    # Stage A
    #---------------------------------------------------------------------

    self.pipe_a = pmlib.PipeCtrl()

    # TestSource valid connected to pvalid for pipe_a stage control logic

    connect( self.pipe_a.pvalid,      self.in_val         )
    connect( self.pipe_a.pipereg_en,  self.a_reg_en       )

    #---------------------------------------------------------------------
    # Stage B
    #---------------------------------------------------------------------

    self.pipe_b = pmlib.PipeCtrl()

    connect( self.pipe_b.pvalid,      self.pipe_a.nvalid  )
    connect( self.pipe_b.pstall,      self.pipe_a.nstall  )
    connect( self.pipe_b.psquash,     self.pipe_a.nsquash )
    connect( self.pipe_b.pipereg_en,  self.b_reg_en       )

    #---------------------------------------------------------------------
    # Stage C
    #---------------------------------------------------------------------

    self.pipe_c = pmlib.PipeCtrl()

    connect( self.pipe_c.pvalid,      self.pipe_b.nvalid  )
    connect( self.pipe_c.pstall,      self.pipe_b.nstall  )
    connect( self.pipe_c.psquash,     self.pipe_b.nsquash )
    connect( self.pipe_c.pipereg_en,  self.c_reg_en       )

    # control word and stall count in pipe_c stage

    self.inst_c        = Wire( 9 )
    self.stall_count_c = Wire( 3 )

    #---------------------------------------------------------------------
    # Stage D
    #---------------------------------------------------------------------

    self.pipe_d = pmlib.PipeCtrl()

    connect( self.pipe_d.pvalid,      self.pipe_c.nvalid  )
    connect( self.pipe_d.pstall,      self.pipe_c.nstall  )
    connect( self.pipe_d.psquash,     self.pipe_c.nsquash )
    connect( self.pipe_d.pipereg_en,  self.d_reg_en       )

    # control word and stall count in pipe_c stage

    self.inst_d        = Wire( 9 )
    self.stall_count_d = Wire( 3 )

    #---------------------------------------------------------------------
    # Stage E
    #---------------------------------------------------------------------

    self.pipe_e = pmlib.PipeCtrl()

    connect( self.pipe_e.pvalid,      self.pipe_d.nvalid  )
    connect( self.pipe_e.pstall,      self.pipe_d.nstall  )
    connect( self.pipe_e.psquash,     self.pipe_d.nsquash )
    connect( self.pipe_e.pipereg_en,  self.e_reg_en       )

    # control word and stall count in pipe_c stage

    self.inst_e        = Wire( 9 )
    self.stall_count_e = Wire( 3 )

  #---------------------------------------------------------------------
  # A stage
  #---------------------------------------------------------------------

  @combinational
  def comb_a ( self ):

    # pipe_a ostall & o_squash

    self.pipe_a.ostall.value  = 0
    self.pipe_a.osquash.value = 0

    # stall the source if aggregate signal from a stage is asserted
    # otherwise we can drain the source

    self.in_rdy.value = ~self.pipe_a.pstall.value

    # process transaction

    # no modifications to architectural state or val/rdy calculations

  #---------------------------------------------------------------------
  # B stage
  #---------------------------------------------------------------------

  @combinational
  def comb_b ( self ):

    # pipe_b ostall & o_squash

    self.pipe_b.ostall.value  = 0
    self.pipe_b.osquash.value = 0

    # process transaction

    # no modifications to architectural state or val/rdy calculations

  #---------------------------------------------------------------------
  # B->C
  #---------------------------------------------------------------------
  # Registers at the start of C stage

  @posedge_clk
  def seq_bc ( self ):

    # copy control word if enabled

    if self.pipe_c.pipereg_en.value:
      self.inst_c.next = self.inst_b.value

    # If current stage originates a stall and is not stalled because of the
    # next stage then decrement the count of stall cycles. Else if the
    # current stage is enabled copy the count from the control word of
    # previous stage

    if ( self.pipe_c.ostall.value and self.pipe_c.pipereg_val.value
         and not self.pipe_c.nstall.value ):
      self.stall_count_c.next = self.stall_count_c.value - 1
    elif self.pipe_c.pipereg_en.value:
      self.stall_count_c.next = self.inst_b[CW_STALL_CYCLES].value

  #---------------------------------------------------------------------
  # C stage
  #---------------------------------------------------------------------

  @combinational
  def comb_c ( self ):

    # ostall in c

    # originate the stall if valid and the stall_stage matches to the
    # current state and the stall cycles count of the current stage is not
    # zero

    self.pipe_c.ostall.value = ( self.pipe_c.pipereg_val.value
      and  ( self.inst_c[CW_STALL_STAGE].value  == STAGE_C )
      and  ( self.stall_count_c.value != 0 ) )

    # osquash in c

    # originate the squash signal if the current stage is valid and matches
    # the squash_stage of the control word

    self.pipe_c.osquash.value = ( self.pipe_c.pipereg_val.value
      and ( self.inst_c[CW_SQUASH_STAGE].value == STAGE_C ) )

    # process transaction

    # no modifications to architectural state or val/rdy calculations

  #---------------------------------------------------------------------
  # C->D
  #---------------------------------------------------------------------
  # Registers at the start of D stage

  @posedge_clk
  def seq_cd ( self ):

    # copy control word if enabled

    if self.pipe_d.pipereg_en.value:
      self.inst_d.next = self.inst_c.value

    # If current stage originates a stall and is not stalled because of the
    # next stage then decrement the count of stall cycles. Else if the
    # current stage is enabled copy the count from the control word of
    # previous stage

    if ( self.pipe_d.ostall.value and self.pipe_d.pipereg_val.value
         and not self.pipe_d.nstall.value ):
      self.stall_count_d.next = self.stall_count_d.value - 1
    elif self.pipe_d.pipereg_en.value:
      self.stall_count_d.next = self.inst_c[CW_STALL_CYCLES].value

  #---------------------------------------------------------------------
  # D stage
  #---------------------------------------------------------------------

  @combinational
  def comb_d ( self ):

    # ostall in d

    # originate the stall if valid and the stall_stage matches to the
    # current state and the stall cycles count of the current stage is not
    # zero

    self.pipe_d.ostall.value = ( self.pipe_d.pipereg_val.value
      and  ( self.inst_d[CW_STALL_STAGE].value  == STAGE_D )
      and  ( self.stall_count_d.value !=  0 ) )

    # osquash in d

    # originate the squash signal if the current stage is valid and matches
    # the squash_stage of the control word

    self.pipe_d.osquash.value = ( self.pipe_d.pipereg_val.value
      and ( self.inst_d[CW_SQUASH_STAGE].value == STAGE_D ) )

    # process transaction

    # no modifications to architectural state or val/rdy calculations

  #---------------------------------------------------------------------
  # D->E
  #---------------------------------------------------------------------
  # Registers at the start of E stage

  @posedge_clk
  def seq_de ( self ):

    # copy control word if enabled

    if self.pipe_e.pipereg_en.value:
      self.inst_e.next = self.inst_d.value

    # If current stage originates a stall and is not stalled because of the
    # next stage then decrement the count of stall cycles. Else if the
    # current stage is enabled copy the count from the control word of
    # previous stage

    if ( self.pipe_e.ostall.value and self.pipe_e.pipereg_val.value
         and not self.pipe_e.nstall.value ):
      self.stall_count_e.next = self.stall_count_e.value - 1
    elif self.pipe_e.pipereg_en.value:
      self.stall_count_e.next = self.inst_d[CW_STALL_CYCLES].value

  #---------------------------------------------------------------------
  # E stage
  #---------------------------------------------------------------------

  @combinational
  def comb_e ( self ):

    # stall pipe_e stage if the sink is not ready

    self.pipe_e.nstall.value =   ~self.out_rdy.value

    # ostall in e

    # originate the stall if valid and the stall_stage matches to the
    # current state and the stall cycles count of the current stage is not
    # zero

    self.pipe_e.ostall.value = ( self.pipe_e.pipereg_val.value
     and ( self.inst_e[CW_STALL_STAGE].value  == STAGE_E )
     and ( self.stall_count_e.value !=  0 )  )

    # osquash in e

    # originate the squash signal if the current stage is valid and matches
    # the squash_stage of the control word

    self.pipe_e.osquash.value = ( self.pipe_e.pipereg_val.value
     and ( self.inst_e[CW_SQUASH_STAGE].value == STAGE_E ) )

    # process transaction

    # modify architectural stage (TestSink) only if the transaction go is
    # set else make no changes

    if  self.pipe_e.pipe_go.value:
      self.out_val.value = 1
    else:
      self.out_val.value = 0

#-------------------------------------------------------------------------
# 5-stage Incrementer Pipeline
#-------------------------------------------------------------------------

class IncrPipe (Model):

  def __init__( self, nbits ):

    # Interface Ports

    self.in_msg  = InPort  ( TRANSACTION_NBITS )
    self.in_val  = InPort  ( 1 )
    self.in_rdy  = OutPort ( 1 )

    self.out_msg = OutPort ( nbits )
    self.out_val = OutPort ( 1 )
    self.out_rdy = InPort  ( 1 )

    # Static Elaboration

    self.ctrl  = IncrPipeCtrl()
    self.dpath = IncrPipeDpath( nbits )

    # connect ctrl

    connect( self.ctrl.in_val,  self.in_val  )
    connect( self.ctrl.in_rdy,  self.in_rdy  )
    connect( self.ctrl.out_val, self.out_val )
    connect( self.ctrl.out_rdy, self.out_rdy )

    # connect dpath

    connect( self.dpath.in_msg,  self.in_msg  )
    connect( self.dpath.out_msg, self.out_msg )

    # connect ctrl signals (ctrl -> dpath )

    connect( self.ctrl.a_reg_en, self.dpath.a_reg_en )
    connect( self.ctrl.b_reg_en, self.dpath.b_reg_en )
    connect( self.ctrl.c_reg_en, self.dpath.c_reg_en )
    connect( self.ctrl.d_reg_en, self.dpath.d_reg_en )
    connect( self.ctrl.e_reg_en, self.dpath.e_reg_en )

    # connect status signals (ctrl <- dpath )

    connect( self.ctrl.inst_b,   self.dpath.inst_b   )

  #---------------------------------------------------------------------
  # Line Tracing
  #---------------------------------------------------------------------

  def line_trace( self ):

    # Stage A

    if self.ctrl.pipe_a.pipereg_val.value:
      pipe_a_str = "{:^3d}".format( self.dpath.a_reg.out[VALUE].value.uint )
    else:
      pipe_a_str = " - "

    # Stage B

    if self.ctrl.pipe_b.pipereg_val.value:
      pipe_b_str = "{:^3d}".format( self.dpath.b_reg.out[VALUE].value.uint )
    else:
      pipe_b_str = " - "

    # Stage C

    if self.ctrl.pipe_c.pipereg_val.value:
      pipe_c_str = "{:^3d}".format( self.dpath.c_incr.out.value.uint )
    else:
      pipe_c_str = " - "

    # Stage D

    if self.ctrl.pipe_d.pipereg_val.value:
      pipe_d_str = "{:^3d}".format( self.dpath.d_incr.out.value.uint )
    else:
      pipe_d_str = " - "

    # Stage E

    if self.ctrl.pipe_e.pipereg_val.value:
      pipe_e_str = "{:^3d}".format( self.dpath.e_incr.out.value.uint )
    else:
      pipe_e_str = " - "


    out_str = "{} | {} | {} | {} | {}".format( pipe_a_str, pipe_b_str,
        pipe_c_str, pipe_d_str, pipe_e_str )

    return out_str

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    self.src        = pmlib.TestSource ( 17, src_msgs,  src_delay  )
    self.incr_pipe  = ModelType        ( 8 )
    self.sink       = pmlib.TestSink   ( 8, sink_msgs, sink_delay )

    # Connect

    connect( self.incr_pipe.in_msg, self.src.out_msg )
    connect( self.incr_pipe.in_val, self.src.out_val )
    connect( self.incr_pipe.in_rdy, self.src.out_rdy )

    connect( self.incr_pipe.out_msg, self.sink.in_msg )
    connect( self.incr_pipe.out_val, self.sink.in_val )
    connect( self.incr_pipe.out_rdy, self.sink.in_rdy )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + self.incr_pipe.line_trace() \
           + " > " + self.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_incr_pipe_test( dump_vcd, vcd_file_name, src_msgs, sink_msgs,
                        ModelType, src_delay, sink_delay ):

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# mk_req helper function
#-------------------------------------------------------------------------

def mk_req( st_stage, st_cycles, sq_stage, value ):
  bits = Bits( TRANSACTION_NBITS )
  bits[STALL_STAGE]  = st_stage
  bits[STALL_CYCLES] = st_cycles
  bits[SQUASH_STAGE] = sq_stage
  bits[VALUE]        = value
  return bits

#-------------------------------------------------------------------------
# Simple Pipeline Test - No stalls or squashes
#-------------------------------------------------------------------------
#
# Modeling;
#
# t0 A B C D E
# t1   A B C D E
# t2     A B C D E
# t3       A B C D E
# t4         A B C D E

src_simple_msgs = [
    mk_req( 0, 0, 0, 1 ),
    mk_req( 0, 0, 0, 2 ),
    mk_req( 0, 0, 0, 3 ),
    mk_req( 0, 0, 0, 4 ),
    mk_req( 0, 0, 0, 5 ),
  ]

sink_simple_msgs = [
    4,
    5,
    6,
    7,
    8,
  ]

def test_simple_pipe_delay_0x0( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_simple_pipe_delay_0x0.vcd",
                      src_simple_msgs, sink_simple_msgs,
                      IncrPipe, 0, 0 )

def test_simple_pipe_delay_5x0( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_simple_pipe_delay_5x0.vcd",
                      src_simple_msgs, sink_simple_msgs,
                      IncrPipe, 5, 0 )

def test_simple_pipe_delay_0x5( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_simple_pipe_delay_0x5.vcd",
                      src_simple_msgs, sink_simple_msgs,
                      IncrPipe, 0, 5 )

def test_simple_pipe_delay_4x9( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_simple_pipe_delay_4x9.vcd",
                      src_simple_msgs, sink_simple_msgs,
                      IncrPipe, 4, 9 )

#-------------------------------------------------------------------------
# Stall Pipeline Test - no squashes
#-------------------------------------------------------------------------
# Note: For the current microarchitecture, we can't stall in A or B stage
#
# Modeling;
#
# t0 A B C C D E
# t1   A B B C D D D E
# t2     A A B C C C D E E E E
# t3         A B B B C D D D D E E E
# t4           A A A B C C C C C C C D E

src_stall_msgs = [
    mk_req( STAGE_C, 1, 0, 1 ),
    mk_req( STAGE_D, 2, 0, 2 ),
    mk_req( STAGE_E, 3, 0, 3 ),
    mk_req( STAGE_E, 2, 0, 4 ),
    mk_req( STAGE_C, 1, 0, 5 ),
  ]

sink_stall_msgs = [
    4,
    5,
    6,
    7,
    8,
  ]

def test_stall_pipe_delay_0x0( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_stall_pipe_delay_0x0.vcd",
                      src_stall_msgs, sink_stall_msgs,
                      IncrPipe, 0, 0 )

def test_stall_pipe_delay_5x0( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_stall_pipe_delay_5x0.vcd",
                      src_stall_msgs, sink_stall_msgs,
                      IncrPipe, 5, 0 )

def test_stall_pipe_delay_0x5( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_stall_pipe_delay_0x5.vcd",
                      src_stall_msgs, sink_stall_msgs,
                      IncrPipe, 0, 5 )

def test_stall_pipe_delay_4x9( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_stall_pipe_delay_4x9.vcd",
                      src_stall_msgs, sink_stall_msgs,
                      IncrPipe, 4, 9 )

#-------------------------------------------------------------------------
# Squash Pipeline Test - no stalls
#-------------------------------------------------------------------------
# Squash cannot be tested with random delays currently.
#
# Modeling;
#
# t0 A B C D E
# t1   A B - - -
# t2     A - - - -
# t3       A B C D E
# t4         A - - - -

src_squash_msgs = [
    mk_req( 0, 0, STAGE_C, 1 ),
    mk_req( 0, 0, 0, 2 ),
    mk_req( 0, 0, 0, 3 ),
    mk_req( 0, 0, STAGE_B, 4 ),
    mk_req( 0, 0, 0, 5 ),
  ]

sink_squash_msgs = [
    4,
    #5, squashed
    #6, squashed
    7,
    #8, squashed
  ]

def test_squash_pipe_delay_0x0( dump_vcd ):
  run_incr_pipe_test( dump_vcd, "test_squash_pipe_delay_0x0.vcd",
                      src_squash_msgs, sink_squash_msgs,
                      IncrPipe, 0, 0 )
