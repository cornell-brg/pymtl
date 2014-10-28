#=========================================================================
# IntDivBL_test.py
#=========================================================================

from pymtl  import *
from pclib  import TestSource, TestSink
from muldiv_msg import BitStructIndex, createMulDivMessage
from IntDivBL   import IntDivBL

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

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, model, src_msgs, sink_msgs, src_delay, sink_delay ):

    s.src  = TestSource( idx.length, src_msgs,  src_delay  )
    s.idiv = model
    s.sink = TestSink  ( 32, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    s.connect( s.src.out,  s.idiv.in_ )
    s.connect( s.idiv.out, s.sink.in_ )

  def done( s ):
    return s.src.done.value and s.sink.done.value

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.idiv.line_trace() + " > " + \
           s.sink.line_trace()

#-----------------------------------------------------------------------
# run_idivrem_test
#-----------------------------------------------------------------------
def run_idivrem_test( dump_vcd, vcd_file_name, model,
                      src_delay, sink_delay, test_msgs ):

  src_msgs  = test_msgs[::2]
  sink_msgs = test_msgs[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( model, src_msgs, sink_msgs, src_delay, sink_delay )
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
# div unit test for small positive / positive
#-----------------------------------------------------------------------

div_test_msgs_small_pp = [
  createMulDivMessage( idx.DIV_OP,   6,  3 ), B(  2 ),
  createMulDivMessage( idx.DIV_OP,  20,  5 ), B(  4 ),
  createMulDivMessage( idx.DIV_OP,   6,  2 ), B(  3 ),
  createMulDivMessage( idx.DIV_OP, 130, 10 ), B( 13 ),
  createMulDivMessage( idx.DIV_OP,  56,  7 ), B(  8 ),
  createMulDivMessage( idx.DIV_OP,  83,  6 ), B( 13 ),
  createMulDivMessage( idx.DIV_OP,  43, 17 ), B(  2 ),
  createMulDivMessage( idx.DIV_OP,  99, 12 ), B(  8 ),
  createMulDivMessage( idx.DIV_OP,  37, 40 ), B(  0 ),
  createMulDivMessage( idx.DIV_OP,  51,  9 ), B(  5 ),

]

test_msgs_all.extend( div_test_msgs_small_pp )

def test_small_pp( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_pp.vcd",
                    model, 0, 0, div_test_msgs_small_pp )

#-----------------------------------------------------------------------
# div unit test for small negative / positive
#-----------------------------------------------------------------------

div_test_msgs_small_np = [
  createMulDivMessage( idx.DIV_OP,   -6,  3 ), B(  -2 ),
  createMulDivMessage( idx.DIV_OP,  -20,  5 ), B(  -4 ),
  createMulDivMessage( idx.DIV_OP,   -6,  2 ), B(  -3 ),
  createMulDivMessage( idx.DIV_OP, -130, 10 ), B( -13 ),
  createMulDivMessage( idx.DIV_OP,  -56,  7 ), B(  -8 ),
  createMulDivMessage( idx.DIV_OP,  -83,  6 ), B( -13 ),
  createMulDivMessage( idx.DIV_OP,  -43, 17 ), B(  -2 ),
  createMulDivMessage( idx.DIV_OP,  -99, 12 ), B(  -8 ),
  createMulDivMessage( idx.DIV_OP,  -37, 40 ), B(   0 ),
  createMulDivMessage( idx.DIV_OP,  -51,  9 ), B(  -5 ),
]

test_msgs_all.extend( div_test_msgs_small_np )

def test_small_np( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_np.vcd",
                    model, 0, 0, div_test_msgs_small_np )

#-----------------------------------------------------------------------
# div unit test for small positive / negative
#-----------------------------------------------------------------------

div_test_msgs_small_pn = [
  createMulDivMessage( idx.DIV_OP,    6,  -2 ), B(  -3 ),
  createMulDivMessage( idx.DIV_OP,   20,  -4 ), B(  -5 ),
  createMulDivMessage( idx.DIV_OP,    6,  -3 ), B(  -2 ),
  createMulDivMessage( idx.DIV_OP,  130, -10 ), B( -13 ),
  createMulDivMessage( idx.DIV_OP,   56,  -8 ), B(  -7 ),
  createMulDivMessage( idx.DIV_OP,   83,  -6 ), B( -13 ),
  createMulDivMessage( idx.DIV_OP,   43, -17 ), B(  -2 ),
  createMulDivMessage( idx.DIV_OP,   99, -12 ), B(  -8 ),
  createMulDivMessage( idx.DIV_OP,   37, -40 ), B(   0 ),
  createMulDivMessage( idx.DIV_OP,   51,  -9 ), B(  -5 ),
]

test_msgs_all.extend( div_test_msgs_small_pn )

def test_small_pn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_pn.vcd",
                    model, 0, 0, div_test_msgs_small_pn )

#-----------------------------------------------------------------------
# div unit test for small negative / negative
#-----------------------------------------------------------------------

div_test_msgs_small_nn = [
  createMulDivMessage( idx.DIV_OP,   -6,  -2 ), B(   3 ),
  createMulDivMessage( idx.DIV_OP,  -20,  -4 ), B(   5 ),
  createMulDivMessage( idx.DIV_OP,   -6,  -3 ), B(   2 ),
  createMulDivMessage( idx.DIV_OP, -130, -10 ), B(  13 ),
  createMulDivMessage( idx.DIV_OP,  -56,  -8 ), B(   7 ),
  createMulDivMessage( idx.DIV_OP,  -83,  -6 ), B(  13 ),
  createMulDivMessage( idx.DIV_OP,  -43, -17 ), B(   2 ),
  createMulDivMessage( idx.DIV_OP,  -99, -12 ), B(   8 ),
  createMulDivMessage( idx.DIV_OP,  -37, -40 ), B(   0 ),
  createMulDivMessage( idx.DIV_OP,  -51,  -9 ), B(   5 ),
]

test_msgs_all.extend( div_test_msgs_small_nn )

def test_small_nn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_nn.vcd",
                    model, 0, 0, div_test_msgs_small_nn )


#-----------------------------------------------------------------------
# div legacy test
#-----------------------------------------------------------------------

div_test_msgs_legacy = [
  createMulDivMessage( idx.DIV_OP, 0x00000000, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.DIV_OP, 0x00000001, 0x00000001 ), B( 0x00000001 ),
  createMulDivMessage( idx.DIV_OP, 0x00000000, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.DIV_OP, 0xffffffff, 0xffffffff ), B( 0x00000001 ),
  createMulDivMessage( idx.DIV_OP, 0x00000222, 0x0000002a ), B( 0x0000000d ),
  createMulDivMessage( idx.DIV_OP, 0x0a01b044, 0xffffb146 ), B( 0xffffdf76 ),
  createMulDivMessage( idx.DIV_OP, 0x00000032, 0x00000222 ), B( 0x00000000 ),
  createMulDivMessage( idx.DIV_OP, 0x00000222, 0x00000032 ), B( 0x0000000a ),
  createMulDivMessage( idx.DIV_OP, 0x0a01b044, 0xffffb14a ), B( 0xffffdf75 ),
  createMulDivMessage( idx.DIV_OP, 0xdeadbeef, 0x0000beef ), B( 0xffffd353 ),
  createMulDivMessage( idx.DIV_OP, 0xf5fe4fbc, 0x00004eb6 ), B( 0xffffdf75 ),
  createMulDivMessage( idx.DIV_OP, 0xf5fe4fbc, 0xffffb14a ), B( 0x0000208b ),
]

test_msgs_all.extend( div_test_msgs_legacy )

def test_div_legacy( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-legacy-IntDivBL_test.vcd",
                    model, 0, 0, div_test_msgs_legacy )


#-----------------------------------------------------------------------
# rem legacy test
#-----------------------------------------------------------------------

rem_test_msgs_legacy = [
  createMulDivMessage( idx.REM_OP, 0x00000000, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0x00000001, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0x00000000, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0xffffffff, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0x00000222, 0x0000002a ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0x0a01b044, 0xffffb146 ), B( 0x00000000 ),
  createMulDivMessage( idx.REM_OP, 0x00000032, 0x00000222 ), B( 0x00000032 ),
  createMulDivMessage( idx.REM_OP, 0x00000222, 0x00000032 ), B( 0x0000002e ),
  createMulDivMessage( idx.REM_OP, 0x0a01b044, 0xffffb14a ), B( 0x00003372 ),
  createMulDivMessage( idx.REM_OP, 0xdeadbeef, 0x0000beef ), B( 0xffffda72 ),
  createMulDivMessage( idx.REM_OP, 0xf5fe4fbc, 0x00004eb6 ), B( 0xffffcc8e ),
  createMulDivMessage( idx.REM_OP, 0xf5fe4fbc, 0xffffb14a ), B( 0xffffcc8e ),
]

test_msgs_all.extend( rem_test_msgs_legacy )

def test_rem_legacy( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-legacy-IntDivBL_test.vcd",
                    model, 0, 0, rem_test_msgs_legacy )


#-----------------------------------------------------------------------
# divu legacy test
#-----------------------------------------------------------------------

divu_test_msgs_legacy = [
  createMulDivMessage( idx.DIVU_OP, 0x00000000, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.DIVU_OP, 0x00000001, 0x00000001 ), B( 0x00000001 ),
  createMulDivMessage( idx.DIVU_OP, 0x00000000, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.DIVU_OP, 0xffffffff, 0xffffffff ), B( 0x00000001 ),
  createMulDivMessage( idx.DIVU_OP, 0x00000222, 0x0000002a ), B( 0x0000000d ),
  createMulDivMessage( idx.DIVU_OP, 0x0a01b044, 0x00004eba ), B( 0x0000208a ),
  createMulDivMessage( idx.DIVU_OP, 0x00000032, 0x00000222 ), B( 0x00000000 ),
  createMulDivMessage( idx.DIVU_OP, 0x00000222, 0x00000032 ), B( 0x0000000a ),
  createMulDivMessage( idx.DIVU_OP, 0x0a01b044, 0xffffb14a ), B( 0x00000000 ),
  createMulDivMessage( idx.DIVU_OP, 0xdeadbeef, 0x0000beef ), B( 0x00012a90 ),
  createMulDivMessage( idx.DIVU_OP, 0xf5fe4fbc, 0x00004eb6 ), B( 0x00032012 ),
  createMulDivMessage( idx.DIVU_OP, 0xf5fe4fbc, 0xffffb14a ), B( 0x00000000 ),
]

test_msgs_all.extend( divu_test_msgs_legacy )

def test_divu_legacy( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idivu-legacy-IntDivBL_test.vcd",
                    model, 0, 0, divu_test_msgs_legacy )


#-----------------------------------------------------------------------
# remu legacy test
#-----------------------------------------------------------------------

remu_test_msgs_legacy = [
  createMulDivMessage( idx.REMU_OP, 0x00000000, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0x00000001, 0x00000001 ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0x00000000, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0xffffffff, 0xffffffff ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0x00000222, 0x0000002a ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0x0a01b044, 0x00004eba ), B( 0x00000000 ),
  createMulDivMessage( idx.REMU_OP, 0x00000032, 0x00000222 ), B( 0x00000032 ),
  createMulDivMessage( idx.REMU_OP, 0x00000222, 0x00000032 ), B( 0x0000002e ),
  createMulDivMessage( idx.REMU_OP, 0x0a01b044, 0xffffb14a ), B( 0x0a01b044 ),
  createMulDivMessage( idx.REMU_OP, 0xdeadbeef, 0x0000beef ), B( 0x0000227f ),
  createMulDivMessage( idx.REMU_OP, 0xf5fe4fbc, 0x00004eb6 ), B( 0x000006f0 ),
  createMulDivMessage( idx.REMU_OP, 0xf5fe4fbc, 0xffffb14a ), B( 0xf5fe4fbc ),
]

test_msgs_all.extend( remu_test_msgs_legacy )

def test_remu_legacy( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-iremu-legacy-IntDivBL_test.vcd",
                    model, 0, 0, remu_test_msgs_legacy )



#-----------------------------------------------------------------------
# div unit test for large positive / positive
#-----------------------------------------------------------------------

div_test_msgs_large_pp = [
  createMulDivMessage( idx.DIV_OP,  0x1fffaaaa,  0x00006faf ), B( 0x00004958 ),
  createMulDivMessage( idx.DIV_OP,  0x6a8f2222,  0x04120000 ), B( 0x0000001A ),
  createMulDivMessage( idx.DIV_OP,  0x1aff2121,  0x0000a21f ), B( 0x00002AA1 ),
  createMulDivMessage( idx.DIV_OP,  0x00afcdc2,  0x000afc28 ), B( 0x00000010 ),
]

test_msgs_all.extend( div_test_msgs_large_pp )

def test_large_pp( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_large_pp.vcd",
                    model, 0, 0, div_test_msgs_large_pp )

#-----------------------------------------------------------------------
# div unit test for large negative / negative
#-----------------------------------------------------------------------

div_test_msgs_large_nn = [
  createMulDivMessage( idx.DIV_OP,  -2000000000,  -1987654321 ), B(     1 ),
  createMulDivMessage( idx.DIV_OP,  -1283824847,   -138283848 ), B(     9 ),
  createMulDivMessage( idx.DIV_OP,  -2000293472,       -42938 ), B( 46585 ),
  createMulDivMessage( idx.DIV_OP,  -2002942987,      -838238 ), B(  2389 ),
]

test_msgs_all.extend( div_test_msgs_large_nn )

def test_large_nn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_large_pp.vcd",
                    model, 0, 0, div_test_msgs_large_nn )


#-----------------------------------------------------------------------
# div unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_delay5x10.vcd",
                    model, 5, 10, test_msgs_all )

#-----------------------------------------------------------------------
# div unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_delay10x5.vcd",
                    model, 10, 5, test_msgs_all )

#-----------------------------------------------------------------------
# div random testing
#-----------------------------------------------------------------------
# Create random inputs with reference outputs.

div_test_msgs_random = []

for i in xrange( 50 ):

  # Create two random numbers

  a = Bits( 32, random.randint(0,2**32-1) ).int()
  b = Bits( 32, random.randint(0,2**32-1) ).int()

  if   a < 0 and b < 0: result1 = Bits( 32, a / b, trunc=True )
  elif a > 0 and b > 0: result1 = Bits( 32, a / b, trunc=True )
  else:                 result1 = - ( abs( a ) / abs( b ) )

  result = Bits( 32, result1, trunc=True )

  # Add this to our test messages

  div_test_msgs_random.append( createMulDivMessage(idx.DIV_OP, a, b) )
  div_test_msgs_random.append( result )

def test_random( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_random.vcd",
                    model, 0, 0, div_test_msgs_random )

def test_random_delay5x10( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_random_delay5x10.vcd",
                    model, 5, 10, div_test_msgs_random )

test_msgs_all = []

#-----------------------------------------------------------------------
# rem unit test for small positive % positive
#-----------------------------------------------------------------------

rem_test_msgs_small_pp = [
  createMulDivMessage( idx.REM_OP,   7,  3 ), B(  1 ),
  createMulDivMessage( idx.REM_OP,  10,  7 ), B(  3 ),
  createMulDivMessage( idx.REM_OP,  14,  4 ), B(  2 ),
  createMulDivMessage( idx.REM_OP, 130, 12 ), B( 10 ),
  createMulDivMessage( idx.REM_OP,  56,  9 ), B(  2 ),
  createMulDivMessage( idx.REM_OP, 140, 14 ), B(  0 ),
  createMulDivMessage( idx.REM_OP,  99,  9 ), B(  0 ),
]

test_msgs_all.extend( rem_test_msgs_small_pp )

def test_remainder_small_pp( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_pp.vcd",
                    model, 0, 0, rem_test_msgs_small_pp )

#-----------------------------------------------------------------------
# rem unit test for small negative % negative
#-----------------------------------------------------------------------

rem_test_msgs_small_nn = [
  createMulDivMessage( idx.REM_OP,   -7,  -3 ), B(  -1 ),
  createMulDivMessage( idx.REM_OP,  -10,  -7 ), B(  -3 ),
  createMulDivMessage( idx.REM_OP,  -14,  -4 ), B(  -2 ),
  createMulDivMessage( idx.REM_OP, -130, -12 ), B( -10 ),
  createMulDivMessage( idx.REM_OP,  -56,  -9 ), B(  -2 ),
  createMulDivMessage( idx.REM_OP, -140, -14 ), B(   0 ),
  createMulDivMessage( idx.REM_OP,  -99,  -9 ), B(   0 ),
]

test_msgs_all.extend( rem_test_msgs_small_nn )

def test_remainder_small_nn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_nn.vcd",
                    model, 0, 0, rem_test_msgs_small_nn )

#-----------------------------------------------------------------------
# IntDivBL unit test for small negative % positive
#-----------------------------------------------------------------------

rem_test_msgs_small_np = [
  createMulDivMessage( idx.REM_OP,   -7,  3 ), B(  -1 ),
  createMulDivMessage( idx.REM_OP,  -10,  7 ), B(  -3 ),
  createMulDivMessage( idx.REM_OP,  -14,  4 ), B(  -2 ),
  createMulDivMessage( idx.REM_OP, -130, 12 ), B( -10 ),
  createMulDivMessage( idx.REM_OP,  -56,  9 ), B(  -2 ),
  createMulDivMessage( idx.REM_OP, -140, 14 ), B(   0 ),
  createMulDivMessage( idx.REM_OP,  -99,  9 ), B(   0 ),
]

test_msgs_all.extend( rem_test_msgs_small_np )

def test_remainder_small_np( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivBL_test_small_np.vcd",
                    model, 0, 0, rem_test_msgs_small_np )

#-----------------------------------------------------------------------
# rem unit test for small positive % negative
#-----------------------------------------------------------------------

rem_test_msgs_small_pn = [
  createMulDivMessage( idx.REM_OP,   7,  -3 ), B(  1 ),
  createMulDivMessage( idx.REM_OP,  10,  -7 ), B(  3 ),
  createMulDivMessage( idx.REM_OP,  14,  -4 ), B(  2 ),
  createMulDivMessage( idx.REM_OP, 130, -12 ), B( 10 ),
  createMulDivMessage( idx.REM_OP,  56,  -9 ), B(  2 ),
  createMulDivMessage( idx.REM_OP, 140, -14 ), B(  0 ),
  createMulDivMessage( idx.REM_OP,  99,  -9 ), B(  0 ),
]

test_msgs_all.extend( rem_test_msgs_small_pn )

def test_remainder_small_pn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_small_pn.vcd",
                    model, 0, 0, rem_test_msgs_small_pn )

#-----------------------------------------------------------------------
# rem unit test for large positive / positive
#-----------------------------------------------------------------------

rem_test_msgs_large_pp = [
  createMulDivMessage( idx.REM_OP,  0x1fffaaaa,  0x00006faf ), B( 0x00005F82 ),
  createMulDivMessage( idx.REM_OP,  0x6a8f2222,  0x04120000 ), B( 0x00BB2222 ),
  createMulDivMessage( idx.REM_OP,  0x1aff2121,  0x0000a21f ), B( 0x000015A2 ),
  createMulDivMessage( idx.REM_OP,  0x00afcdc2,  0x000afc28 ), B( 0x00000B42 ),
]

test_msgs_all.extend( rem_test_msgs_large_pp )

def test_remainder_large_pp( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_large_pp.vcd",
                    model, 0, 0, rem_test_msgs_large_pp )

#-----------------------------------------------------------------------
# rem unit test for large negative / negative
#-----------------------------------------------------------------------

rem_test_msgs_large_nn = [
  createMulDivMessage( idx.REM_OP,  -2000000000,  -1987654321 ), B(  -12345679  ),
  createMulDivMessage( idx.REM_OP,  -1283824847,   -138283848 ), B(  -39270215  ),
  createMulDivMessage( idx.REM_OP,  -2000293472,       -42938 ), B(     -26742  ),
  createMulDivMessage( idx.REM_OP,  -2002942987,      -838238 ), B(    -392405  ),
]

test_msgs_all.extend( rem_test_msgs_large_nn )

def test_remainder_large_nn( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_large_nn.vcd",
                    model, 0, 0, rem_test_msgs_large_nn )


#-----------------------------------------------------------------------
# rem unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_delay5x10.vcd",
                    model, 5, 10, test_msgs_all )

#-----------------------------------------------------------------------
# rem unit test with delay = 10 x 5
#-----------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_delay10x5.vcd",
                    model, 10, 5, test_msgs_all )

#-----------------------------------------------------------------------
# rem random testing
#-----------------------------------------------------------------------
# Create random inputs with reference outputs.

rem_test_msgs_random = []

for i in xrange(50):

  # Create two random numbers

  a = Bits( 32, random.randint(0, 2**32-1) ).int()
  b = Bits( 32, random.randint(0, 2**32-1) ).int()

  if   a < 0 and b < 0: result1 = Bits( 32, a % b, trunc=True )
  elif a > 0 and b > 0: result1 = Bits( 32, a % b, trunc=True )
  elif a < 0 and b > 0: result1 = - ( abs( a ) % abs( b ) )
  else:                 result1 =   ( abs( a ) % abs( b ) )

  result = Bits( 32, result1, trunc=True )

  # Add this to our test messages

  rem_test_msgs_random.append( createMulDivMessage(idx.REM_OP, a, b) )
  rem_test_msgs_random.append( result )

def test_remainder_random( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_random.vcd",
                    model, 0, 0, rem_test_msgs_random )

def test_remainder_random_delay5x10( dump_vcd ):
  model = IntDivBL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivBL_test_random_delay5x10.vcd",
                    model, 5, 10, rem_test_msgs_random )

