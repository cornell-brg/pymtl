#=======================================================================
# PipeCtrl_test.py
#=======================================================================
'''We create a incrementer pipeline (IncrPipe) to test the PipeCtrl unit
by instantiating it in the control unit of the IncrPipe model. The
pipeline has 5 stages: A, B, C, D, E. Frontend of the pipeline is
attached to a TestSource model and Backend is attached to a TestSink.
Datapath has an incrementer in C,D,E stages. We assume that we can never
originate a stall in B stage. B stage sends the control word to the
control unit based on the transaction it is currently processing.
TestSource contains the transaction as below:

  Transaction Format:

  16          14 13          11 10           8 7         0
  +-------------+--------------+--------------+-----------+
  | stall_stage | stall_cycles | squash_stage | value     |
  +-------------+--------------+--------------+-----------+

 stall_stage  : indicates the stage where we want to originate a stall
 stall_cycles : number of cycles we want to stall for
 squash_stage : indicates the stage where we want to originate a squash
 value        : 8-bit value which the datapath increments

TestSink merely holds the expected value based on the increments.
'''

import pytest

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test import TestSource, TestSink
from PipeCtrl   import PipeCtrl

import regs
import arith

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

#-----------------------------------------------------------------------
# IncrPipeDpath
#-----------------------------------------------------------------------
class IncrPipeDpath( Model ):
  '''5-stage Incrementer Pipeline Datapath.'''

  def __init__( s, dtype ):

    s.in_msg    = InPort  ( TRANSACTION_NBITS )
    s.out_msg   = OutPort ( dtype )

    # Ctrl Signals (ctrl -> dpath)
    s.a_reg_en  = InPort  ( 1 )
    s.b_reg_en  = InPort  ( 1 )
    s.c_reg_en  = InPort  ( 1 )
    s.d_reg_en  = InPort  ( 1 )
    s.e_reg_en  = InPort  ( 1 )

    # Status Signals (ctrl <- dpath)
    s.inst_b    = OutPort ( 9 )

    #-------------------------------------------------------------------
    # A Stage
    #-------------------------------------------------------------------

    s.a_reg  = regs.RegEn( TRANSACTION_NBITS )

    # input msg coming from the TestSource

    s.connect( s.a_reg.in_, s.in_msg    )
    s.connect( s.a_reg.en,  s.a_reg_en  )

    #-------------------------------------------------------------------
    # B Stage
    #-------------------------------------------------------------------

    s.b_reg  = regs.RegEn( TRANSACTION_NBITS )

    s.connect( s.b_reg.in_,     s.a_reg.out )
    s.connect( s.b_reg.en,      s.b_reg_en  )

    # send the control word for the tranaction

    s.connect( s.b_reg.out[CW], s.inst_b    )

    #-------------------------------------------------------------------
    # C Stage
    #-------------------------------------------------------------------

    s.c_reg  = regs.RegEn( dtype )

    s.connect( s.c_reg.in_, s.b_reg.out[VALUE] )
    s.connect( s.c_reg.en,  s.c_reg_en         )

    s.c_incr = arith.Incrementer( dtype, increment_amount = 1 )

    s.connect( s.c_incr.in_, s.c_reg.out )

    #-------------------------------------------------------------------
    # D Stage
    #-------------------------------------------------------------------

    s.d_reg  = regs.RegEn( dtype )

    s.connect( s.d_reg.in_, s.c_incr.out )
    s.connect( s.d_reg.en,  s.d_reg_en   )

    s.d_incr = arith.Incrementer( dtype, increment_amount = 1 )

    s.connect( s.d_incr.in_, s.d_reg.out )

    #-------------------------------------------------------------------
    # E Stage
    #-------------------------------------------------------------------

    s.e_reg  = regs.RegEn( dtype )

    s.connect( s.e_reg.in_, s.d_incr.out )
    s.connect( s.e_reg.en,  s.e_reg_en   )

    s.e_incr = arith.Incrementer( dtype, increment_amount = 1 )

    s.connect( s.e_incr.in_, s.e_reg.out )

    # value we write to the Sink

    s.connect( s.e_incr.out, s.out_msg   )

#-----------------------------------------------------------------------
# IncrPipeCtrl
#-----------------------------------------------------------------------
class IncrPipeCtrl (Model):
  """5-stage Incrementer Pipeline Control."""

  def __init__( s ):

    s.in_val    = InPort  ( 1 )
    s.in_rdy    = OutPort ( 1 )

    s.out_val   = OutPort ( 1 )
    s.out_rdy   = InPort  ( 1 )

    # Ctrl Signals (ctrl -> dpath )
    s.a_reg_en  = OutPort  ( 1 )
    s.b_reg_en  = OutPort  ( 1 )
    s.c_reg_en  = OutPort  ( 1 )
    s.d_reg_en  = OutPort  ( 1 )
    s.e_reg_en  = OutPort  ( 1 )

    # Status Signals (ctrl <- dpath)
    s.inst_b    = InPort   ( 9 )

    #-------------------------------------------------------------------
    # Stage A
    #-------------------------------------------------------------------

    s.pipe_a = PipeCtrl()

    # TestSource valid s.connected to pvalid for pipe_a stage control logic

    s.connect( s.pipe_a.pvalid,      s.in_val         )
    s.connect( s.pipe_a.pipereg_en,  s.a_reg_en       )

    #-------------------------------------------------------------------
    # Stage B
    #-------------------------------------------------------------------

    s.pipe_b = PipeCtrl()

    s.connect( s.pipe_b.pvalid,      s.pipe_a.nvalid  )
    s.connect( s.pipe_b.pstall,      s.pipe_a.nstall  )
    s.connect( s.pipe_b.psquash,     s.pipe_a.nsquash )
    s.connect( s.pipe_b.pipereg_en,  s.b_reg_en       )

    #-------------------------------------------------------------------
    # Stage C
    #-------------------------------------------------------------------

    s.pipe_c = PipeCtrl()

    s.connect( s.pipe_c.pvalid,      s.pipe_b.nvalid  )
    s.connect( s.pipe_c.pstall,      s.pipe_b.nstall  )
    s.connect( s.pipe_c.psquash,     s.pipe_b.nsquash )
    s.connect( s.pipe_c.pipereg_en,  s.c_reg_en       )

    # control word and stall count in pipe_c stage

    s.inst_c        = Wire( 9 )
    s.stall_count_c = Wire( 3 )

    #-------------------------------------------------------------------
    # Stage D
    #-------------------------------------------------------------------

    s.pipe_d = PipeCtrl()

    s.connect( s.pipe_d.pvalid,      s.pipe_c.nvalid  )
    s.connect( s.pipe_d.pstall,      s.pipe_c.nstall  )
    s.connect( s.pipe_d.psquash,     s.pipe_c.nsquash )
    s.connect( s.pipe_d.pipereg_en,  s.d_reg_en       )

    # control word and stall count in pipe_c stage

    s.inst_d        = Wire( 9 )
    s.stall_count_d = Wire( 3 )

    #-------------------------------------------------------------------
    # Stage E
    #-------------------------------------------------------------------

    s.pipe_e = PipeCtrl()

    s.connect( s.pipe_e.pvalid,      s.pipe_d.nvalid  )
    s.connect( s.pipe_e.pstall,      s.pipe_d.nstall  )
    s.connect( s.pipe_e.psquash,     s.pipe_d.nsquash )
    s.connect( s.pipe_e.pipereg_en,  s.e_reg_en       )

    # control word and stall count in pipe_c stage

    s.inst_e        = Wire( 9 )
    s.stall_count_e = Wire( 3 )

    #-------------------------------------------------------------------
    # A stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_a():

      # pipe_a ostall & o_squash

      s.pipe_a.ostall.value  = 0
      s.pipe_a.osquash.value = 0

      # stall the source if aggregate signal from a stage is asserted
      # otherwise we can drain the source

      s.in_rdy.value = ~s.pipe_a.pstall.value

      # process transaction

      # no modifications to architectural state or val/rdy calculations

    #-------------------------------------------------------------------
    # B stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_b():

      # pipe_b ostall & o_squash

      s.pipe_b.ostall.value  = 0
      s.pipe_b.osquash.value = 0

      # process transaction

      # no modifications to architectural state or val/rdy calculations

    #-------------------------------------------------------------------
    # B->C
    #-------------------------------------------------------------------
    # Registers at the start of C stage

    @s.posedge_clk
    def seq_bc():

      # copy control word if enabled

      if s.pipe_c.pipereg_en.value:
        s.inst_c.next = s.inst_b.value

      # If current stage originates a stall and is not stalled because of the
      # next stage then decrement the count of stall cycles. Else if the
      # current stage is enabled copy the count from the control word of
      # previous stage

      if ( s.pipe_c.ostall.value and s.pipe_c.pipereg_val.value
           and not s.pipe_c.nstall.value ):
        s.stall_count_c.next = s.stall_count_c.value - 1
      elif s.pipe_c.pipereg_en.value:
        s.stall_count_c.next = s.inst_b[CW_STALL_CYCLES].value

    #-------------------------------------------------------------------
    # C stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_c():

      # ostall in c

      # originate the stall if valid and the stall_stage matches to the
      # current state and the stall cycles count of the current stage is not
      # zero

      s.pipe_c.ostall.value = ( s.pipe_c.pipereg_val.value
        and  ( s.inst_c[CW_STALL_STAGE].value  == STAGE_C )
        and  ( s.stall_count_c.value != 0 ) )

      # osquash in c

      # originate the squash signal if the current stage is valid and matches
      # the squash_stage of the control word

      s.pipe_c.osquash.value = ( s.pipe_c.pipereg_val.value
        and ( s.inst_c[CW_SQUASH_STAGE].value == STAGE_C ) )

      # process transaction

      # no modifications to architectural state or val/rdy calculations

    #-------------------------------------------------------------------
    # C->D
    #-------------------------------------------------------------------
    # Registers at the start of D stage

    @s.posedge_clk
    def seq_cd():

      # copy control word if enabled

      if s.pipe_d.pipereg_en.value:
        s.inst_d.next = s.inst_c.value

      # If current stage originates a stall and is not stalled because of the
      # next stage then decrement the count of stall cycles. Else if the
      # current stage is enabled copy the count from the control word of
      # previous stage

      if ( s.pipe_d.ostall.value and s.pipe_d.pipereg_val.value
           and not s.pipe_d.nstall.value ):
        s.stall_count_d.next = s.stall_count_d.value - 1
      elif s.pipe_d.pipereg_en.value:
        s.stall_count_d.next = s.inst_c[CW_STALL_CYCLES].value

    #-------------------------------------------------------------------
    # D stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_d():

      # ostall in d

      # originate the stall if valid and the stall_stage matches to the
      # current state and the stall cycles count of the current stage is not
      # zero

      s.pipe_d.ostall.value = ( s.pipe_d.pipereg_val.value
        and  ( s.inst_d[CW_STALL_STAGE].value  == STAGE_D )
        and  ( s.stall_count_d.value !=  0 ) )

      # osquash in d

      # originate the squash signal if the current stage is valid and matches
      # the squash_stage of the control word

      s.pipe_d.osquash.value = ( s.pipe_d.pipereg_val.value
        and ( s.inst_d[CW_SQUASH_STAGE].value == STAGE_D ) )

      # process transaction

      # no modifications to architectural state or val/rdy calculations

    #-------------------------------------------------------------------
    # D->E
    #-------------------------------------------------------------------
    # Registers at the start of E stage

    @s.posedge_clk
    def seq_de():

      # copy control word if enabled

      if s.pipe_e.pipereg_en.value:
        s.inst_e.next = s.inst_d.value

      # If current stage originates a stall and is not stalled because of the
      # next stage then decrement the count of stall cycles. Else if the
      # current stage is enabled copy the count from the control word of
      # previous stage

      if ( s.pipe_e.ostall.value and s.pipe_e.pipereg_val.value
           and not s.pipe_e.nstall.value ):
        s.stall_count_e.next = s.stall_count_e.value - 1
      elif s.pipe_e.pipereg_en.value:
        s.stall_count_e.next = s.inst_d[CW_STALL_CYCLES].value

    #-------------------------------------------------------------------
    # E stage
    #-------------------------------------------------------------------

    @s.combinational
    def comb_e():

      # stall pipe_e stage if the sink is not ready

      s.pipe_e.nstall.value =   ~s.out_rdy.value

      # ostall in e

      # originate the stall if valid and the stall_stage matches to the
      # current state and the stall cycles count of the current stage is not
      # zero

      s.pipe_e.ostall.value = ( s.pipe_e.pipereg_val.value
       and ( s.inst_e[CW_STALL_STAGE].value  == STAGE_E )
       and ( s.stall_count_e.value !=  0 )  )

      # osquash in e

      # originate the squash signal if the current stage is valid and matches
      # the squash_stage of the control word

      s.pipe_e.osquash.value = ( s.pipe_e.pipereg_val.value
       and ( s.inst_e[CW_SQUASH_STAGE].value == STAGE_E ) )

      # process transaction

      # modify architectural stage (TestSink) only if the transaction go is
      # set else make no changes

      if  s.pipe_e.pipe_go.value:
        s.out_val.value = 1
      else:
        s.out_val.value = 0

#-----------------------------------------------------------------------
# IncrPipe
#-----------------------------------------------------------------------
class IncrPipe( Model ):
  """5-stage Incrementer Pipeline toplevel."""

  def __init__( s, dtype ):

    s.in_ = InValRdyBundle( TRANSACTION_NBITS )
    s.out = OutValRdyBundle( dtype )

    # Static Elaboration

    s.ctrl  = IncrPipeCtrl()
    s.dpath = IncrPipeDpath( dtype )

    # s.connect ctrl

    s.connect( s.ctrl.in_val,  s.in_.val  )
    s.connect( s.ctrl.in_rdy,  s.in_.rdy  )
    s.connect( s.ctrl.out_val, s.out.val )
    s.connect( s.ctrl.out_rdy, s.out.rdy )

    # s.connect dpath

    s.connect( s.dpath.in_msg,  s.in_.msg  )
    s.connect( s.dpath.out_msg, s.out.msg )

    # s.connect ctrl signals (ctrl -> dpath )

    s.connect( s.ctrl.a_reg_en, s.dpath.a_reg_en )
    s.connect( s.ctrl.b_reg_en, s.dpath.b_reg_en )
    s.connect( s.ctrl.c_reg_en, s.dpath.c_reg_en )
    s.connect( s.ctrl.d_reg_en, s.dpath.d_reg_en )
    s.connect( s.ctrl.e_reg_en, s.dpath.e_reg_en )

    # s.connect status signals (ctrl <- dpath )

    s.connect( s.ctrl.inst_b,   s.dpath.inst_b   )

  #---------------------------------------------------------------------
  # Line Tracing
  #---------------------------------------------------------------------

  def line_trace( s ):

    # Stage A

    if not s.ctrl.pipe_a.pipereg_val.value:
      pipe_a_str = "{:^3s}".format( ' ' )
    elif s.ctrl.pipe_a.nsquash.value:
      pipe_a_str = "{:^3s}".format( '-' )
    elif s.ctrl.pipe_a.pstall.value:
      pipe_a_str = "{:^3s}".format( '#' )
    elif s.ctrl.pipe_a.pipereg_val.value:
      pipe_a_str = "{:^3d}".format( s.dpath.a_reg.out[VALUE].value.uint() )

    # Stage B

    if not s.ctrl.pipe_b.pipereg_val.value:
      pipe_b_str = "{:^3s}".format( ' ' )
    elif s.ctrl.pipe_b.nsquash.value:
      pipe_b_str = "{:^3s}".format( '-' )
    elif s.ctrl.pipe_b.pstall.value:
      pipe_b_str = "{:^3s}".format( '#' )
    elif s.ctrl.pipe_b.pipereg_val.value:
      pipe_b_str = "{:^3d}".format( s.dpath.b_reg.out[VALUE].value.uint() )

    # Stage C

    if not s.ctrl.pipe_c.pipereg_val.value:
      pipe_c_str = "{:^3s}".format( ' ' )
    elif s.ctrl.pipe_c.nsquash.value:
      pipe_c_str = "{:^3s}".format( '-' )
    elif s.ctrl.pipe_c.pstall.value:
      pipe_c_str = "{:^3s}".format( '#' )
    elif s.ctrl.pipe_c.pipereg_val.value:
      pipe_c_str = "{:^3d}".format( s.dpath.c_reg.out[VALUE].value.uint() )

    # Stage D

    if not s.ctrl.pipe_d.pipereg_val.value:
      pipe_d_str = "{:^3s}".format( ' ' )
    elif s.ctrl.pipe_d.nsquash.value:
      pipe_d_str = "{:^3s}".format( '-' )
    elif s.ctrl.pipe_d.pstall.value:
      pipe_d_str = "{:^3s}".format( '#' )
    elif s.ctrl.pipe_d.pipereg_val.value:
      pipe_d_str = "{:^3d}".format( s.dpath.d_reg.out[VALUE].value.uint() )

    # Stage E

    if not s.ctrl.pipe_e.pipereg_val.value:
      pipe_e_str = "{:^3s}".format( ' ' )
    elif s.ctrl.pipe_e.nsquash.value:
      pipe_e_str = "{:^3s}".format( '-' )
    elif s.ctrl.pipe_e.pstall.value:
      pipe_e_str = "{:^3s}".format( '#' )
    elif s.ctrl.pipe_e.pipereg_val.value:
      pipe_e_str = "{:^3d}".format( s.dpath.e_reg.out[VALUE].value.uint() )

    out_str = "{} | {} | {} | {} | {}".format( pipe_a_str, pipe_b_str,
        pipe_c_str, pipe_d_str, pipe_e_str )

    return out_str

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay, test_verilog, dump_vcd ):

    # Instantiate models

    s.src        = TestSource ( 17, src_msgs,  src_delay  )
    s.incr_pipe  = ModelType  ( 8 )
    s.sink       = TestSink   ( 8, sink_msgs, sink_delay )

    s.vcd_file           = dump_vcd
    s.incr_pipe.vcd_file = dump_vcd

    if test_verilog:
      s.incr_pipe = TranslationTool( s.incr_pipe )

    s.connect( s.incr_pipe.in_ , s.src.out )
    s.connect( s.incr_pipe.out , s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.incr_pipe.line_trace() \
           + " > " + s.sink.line_trace()

#-----------------------------------------------------------------------
# run_incr_pipe_test
#-----------------------------------------------------------------------
def run_incr_pipe_test( dump_vcd, src_msgs, sink_msgs,
                        ModelType, src_delay, sink_delay, test_verilog ):

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs,
                       src_delay, sink_delay, test_verilog, dump_vcd
                     )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

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

#-----------------------------------------------------------------------
# mk_req helper function
#-----------------------------------------------------------------------

def mk_req( st_stage, st_cycles, sq_stage, value ):
  bits = Bits( TRANSACTION_NBITS )
  bits[STALL_STAGE]  = st_stage
  bits[STALL_CYCLES] = st_cycles
  bits[SQUASH_STAGE] = sq_stage
  bits[VALUE]        = value
  return bits

#-----------------------------------------------------------------------
# Simple Pipeline Test - No stalls or squashes
#-----------------------------------------------------------------------
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

@pytest.mark.parametrize( "src_delay,sink_delay", [
  ( 0, 0),
  ( 5, 0),
  ( 0, 5),
  ( 4, 9),
])
def test_simple_pipe( dump_vcd, test_verilog, src_delay, sink_delay ):
  run_incr_pipe_test( dump_vcd, src_simple_msgs, sink_simple_msgs,
                      IncrPipe, src_delay, sink_delay, test_verilog )

#-----------------------------------------------------------------------
# Stall Pipeline Test - no squashes
#-----------------------------------------------------------------------
# Note: For the current microarchitecture, can't stall in A or B stage
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

@pytest.mark.parametrize( "src_delay,sink_delay", [
  ( 0, 0),
  ( 5, 0),
  ( 0, 5),
  ( 4, 9),
])
def test_stall_pipe( dump_vcd, test_verilog, src_delay, sink_delay ):
  run_incr_pipe_test( dump_vcd, src_stall_msgs, sink_stall_msgs,
                      IncrPipe, src_delay, sink_delay, test_verilog )

#-----------------------------------------------------------------------
# Squash Pipeline Test - no stalls
#-----------------------------------------------------------------------
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
    mk_req( 0, 0,       0, 2 ),
    mk_req( 0, 0,       0, 3 ),
    mk_req( 0, 0, STAGE_B, 4 ),
    mk_req( 0, 0,       0, 5 ),
  ]

sink_squash_msgs = [
    4,
    #5, squashed
    #6, squashed
    7,
    #8, squashed
  ]

def test_squash_pipe( dump_vcd, test_verilog ):
  run_incr_pipe_test( dump_vcd, src_squash_msgs, sink_squash_msgs,
                      IncrPipe, 0, 0, test_verilog )
