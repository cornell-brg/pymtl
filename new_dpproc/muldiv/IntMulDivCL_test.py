#=======================================================================
# IntMulDivCL_test.py
#=======================================================================

from pymtl              import *
from pclib              import TestSource, TestSink
from new_imul.IntMulBL_test import createMulDivMessage
from new_imul.IntMulBL_test import B
from new_imul.IntMulBL_test import idx
from muldiv_msg             import BitStructIndex
from IntMulDivCL            import IntMulDivCL

import random

#-----------------------------------------------------------------------
# Helpers
#-----------------------------------------------------------------------

idx = BitStructIndex()

# Helper function to create 32b Bits objects
def B( num ):
  return Bits( 32, num )

# Accumulate all test messages for use when doing random delay testing
test_msgs_all = []

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

# Import test data
from new_imul.IntMulBL_test import mul_test_msgs_small_pp
from new_imul.IntMulBL_test import mul_test_msgs_small_np
from new_imul.IntMulBL_test import mul_test_msgs_small_pn
from new_imul.IntMulBL_test import mul_test_msgs_small_nn
from new_imul.IntMulBL_test import mul_test_msgs_large_pp
from new_imul.IntMulBL_test import mul_test_msgs_large_nn
from new_imul.IntMulBL_test import mul_test_msgs_random
from IntDivBL_test          import div_test_msgs_small_pp
from IntDivBL_test          import div_test_msgs_small_np
from IntDivBL_test          import div_test_msgs_small_pn
from IntDivBL_test          import div_test_msgs_small_nn
from IntDivBL_test          import div_test_msgs_large_pp
from IntDivBL_test          import div_test_msgs_large_nn
from IntDivBL_test          import div_test_msgs_random
from IntDivBL_test          import rem_test_msgs_small_pp
from IntDivBL_test          import rem_test_msgs_small_nn
from IntDivBL_test          import rem_test_msgs_small_np
from IntDivBL_test          import rem_test_msgs_small_pn
from IntDivBL_test          import rem_test_msgs_large_pp
from IntDivBL_test          import rem_test_msgs_large_nn
from IntDivBL_test          import rem_test_msgs_random
from IntDivBL_test          import div_test_msgs_legacy
from IntDivBL_test          import rem_test_msgs_legacy
from IntDivBL_test          import divu_test_msgs_legacy
from IntDivBL_test          import remu_test_msgs_legacy

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs, sink_msgs, src_delay, sink_delay ):

    s.src  = TestSource( 67, src_msgs,  src_delay  )
    s.idiv = ModelType ()
    s.sink = TestSink  ( 32, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    s.connect( s.src.out,  s.idiv.in_ )
    s.connect( s.idiv.out, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.idiv.line_trace() + " > " + \
           s.sink.line_trace()

#-----------------------------------------------------------------------
# run_imuldiv_test
#-----------------------------------------------------------------------
def run_imuldiv_test( dump_vcd, vcd_file_name, ModelType,
                      src_delay, sink_delay, test_msgs ):

  src_msgs  = test_msgs[::2]
  sink_msgs = test_msgs[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs, src_delay, sink_delay )
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

#-----------------------------------------------------------------------
# mul unit test for small positive * positive
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_small_pp )

def test_mul_small_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_small_pp.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_small_pp )

#-----------------------------------------------------------------------
# mul unit test for small negative * positive
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_small_np )

def test_mul_small_np( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_small_np.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_small_np )

#-----------------------------------------------------------------------
# mul unit test for small positive * negative
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_small_pn )

def test_mul_small_pn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_small_pn.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_small_pn )

#-----------------------------------------------------------------------
# mul unit test for small negative * negative
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_small_nn )

def test_mul_small_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_small_nn.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_small_nn )

#-----------------------------------------------------------------------
# mul unit test for large positive * positive
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_large_pp )

def test_mul_large_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_large_pp.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_large_pp )

#-----------------------------------------------------------------------
# mul unit test for large negative * negative
#-----------------------------------------------------------------------

test_msgs_all.extend( mul_test_msgs_large_nn )

def test_mul_large_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_large_nn.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_large_nn )

#-----------------------------------------------------------------------
# mul unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_mul_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_delay5x10.vcd",
                    IntMulDivCL, 5, 10, mul_test_msgs_small_pp )

#-----------------------------------------------------------------------
# mul unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_mul_delay10x5( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_delay10x5.vcd",
                    IntMulDivCL, 10, 5, mul_test_msgs_small_pp )

#-----------------------------------------------------------------------
# mul random testing
#-----------------------------------------------------------------------

# Create random inputs with reference outputs. Notice how we have to skew
# the reference outputs by two cycles since we are testing a cycle-level
# model with a two-cycle latency.

def test_mul_random( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_random.vcd",
                    IntMulDivCL, 0, 0, mul_test_msgs_random )

def test_mul_random_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-imul-IntMulDivCL_test_random_delay5x10.vcd",
                    IntMulDivCL, 5, 10, mul_test_msgs_random )



test_msgs_all = []

#-----------------------------------------------------------------------
# div unit test for small positive / positive
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_pp )

def test_div_small_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_pp.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_small_pp )

#-----------------------------------------------------------------------
# div unit test for small negative / positive
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_np )

def test_div_small_np( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_np.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_small_np )

#-----------------------------------------------------------------------
# div unit test for small positive / negative
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_pn )

def test_div_small_pn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_pn.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_small_pn )

#-----------------------------------------------------------------------
# div unit test for small negative / negative
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_nn )

def test_div_small_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_nn.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_small_nn )

#-----------------------------------------------------------------------
# div unit test for large positive / positive
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_large_pp )

def test_div_large_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_large_pp.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_large_pp )

#-----------------------------------------------------------------------
# div unit test for large negative / negative
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_large_nn )

def test_div_large_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_large_nn.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_large_nn )

#-----------------------------------------------------------------------
# div unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_div_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_delay5x10.vcd",
                    IntMulDivCL, 5, 10, div_test_msgs_small_pp )

#-----------------------------------------------------------------------
# div unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_div_delay10x5( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_delay10x5.vcd",
                    IntMulDivCL, 10, 5, div_test_msgs_small_pp )

#-----------------------------------------------------------------------
# div unit random testing
#-----------------------------------------------------------------------
# Create random inputs with reference outputs.

def test_div_random( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_random.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_random )

def test_div_random_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_random_delay5x10.vcd",
                    IntMulDivCL, 5, 10, div_test_msgs_random )

test_msgs_all = []

#-----------------------------------------------------------------------
# rem unit test for small positive % positive
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_pp )

def test_remainder_small_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_pp.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_small_pp )

#-----------------------------------------------------------------------
# rem unit test for small negative % negative
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_nn )

def test_remainder_small_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_nn.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_small_nn )

#-----------------------------------------------------------------------
# rem unit test for small negative % positive
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_np )

def test_remainder_small_np( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-IntMulDivCL_test_small_np.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_small_np )

#-----------------------------------------------------------------------
# rem unit test for small positive % positive
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_pn )

def test_remainder_small_pn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_small_pn.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_small_pn )

#-----------------------------------------------------------------------
# rem unit test for large positive / positive
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_large_pp )

def test_remainder_large_pp( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_large_pp.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_large_pp )

#-----------------------------------------------------------------------
# rem unit test for large negative / negative
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_large_nn )

def test_remainder_large_nn( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_large_nn.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_large_nn )

#-----------------------------------------------------------------------
# rem unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_remainder_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_delay5x10.vcd",
                    IntMulDivCL, 5, 10, test_msgs_all )

#-----------------------------------------------------------------------
# rem unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_remainder_delay10x5( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_delay10x5.vcd",
                    IntMulDivCL, 10, 5, test_msgs_all )


#-----------------------------------------------------------------------
# rem random testing
#-----------------------------------------------------------------------
# Create random inputs with reference outputs.

def test_remainder_random( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_random.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_random )

def test_remainder_random_delay5x10( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_random_delay5x10.vcd",
                    IntMulDivCL, 5, 10, rem_test_msgs_random )

#-----------------------------------------------------------------------
# mul/div/rem ops together
#-----------------------------------------------------------------------

test_muldivrem_msgs_combined = [
  createMulDivMessage( idx.DIV_OP,  56,   7 ), B(    8 ),
  createMulDivMessage( idx.MUL_OP,  10,  13 ), B(  130 ),
  createMulDivMessage( idx.MUL_OP,  13, -10 ), B( -130 ),
  createMulDivMessage( idx.REM_OP, 130,  12 ), B(   10 ),
  createMulDivMessage( idx.MUL_OP,   3,   2 ), B(    6 ),
  createMulDivMessage( idx.DIV_OP,  43,  17 ), B(    2 ),
  createMulDivMessage( idx.DIV_OP,  99,  12 ), B(    8 ),
  createMulDivMessage( idx.REM_OP, -99,   9 ), B(    0 ),
]
test_msgs_all.extend( test_muldivrem_msgs_combined )

def test_muldivrem_combined( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-IntMulDivCL_test_combined.vcd",
                    IntMulDivCL, 0, 0, test_muldivrem_msgs_combined )

#-----------------------------------------------------------------------
# div legacy test
#-----------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_legacy )

def test_div_legacy( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idiv-legacy-IntDivBL_test.vcd",
                    IntMulDivCL, 0, 0, div_test_msgs_legacy )

#-----------------------------------------------------------------------
# rem legacy test
#-----------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_legacy )

def test_rem_legacy( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-irem-legacy-IntDivBL_test.vcd",
                    IntMulDivCL, 0, 0, rem_test_msgs_legacy )

#-----------------------------------------------------------------------
# divu legacy test
#-----------------------------------------------------------------------

test_msgs_all.extend( divu_test_msgs_legacy )

def test_divu_legacy( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-idivu-legacy-IntDivBL_test.vcd",
                    IntMulDivCL, 0, 0, divu_test_msgs_legacy )

#-----------------------------------------------------------------------
# remu legacy test
#-----------------------------------------------------------------------

test_msgs_all.extend( remu_test_msgs_legacy )

def test_remu_legacy( dump_vcd ):
  run_imuldiv_test( dump_vcd, "pex-iremu-legacy-IntDivBL_test.vcd",
                    IntMulDivCL, 0, 0, remu_test_msgs_legacy )

