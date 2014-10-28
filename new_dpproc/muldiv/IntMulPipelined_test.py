#=======================================================================
# IntMulPipelined_test.py
#=======================================================================

from pymtl              import *
from IntMulPipelined        import IntMulPipelined as IntMulIterVarLat

from new_imul.IntMulBL_test import run_imul_test
from new_imul.IntMulBL_test import B
from new_imul.muldiv_msg    import BitStructIndex
from new_imul.muldiv_msg    import createMulDivMessage

idx = BitStructIndex()

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for small positive * positive
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_small_pp

def test_small_pp( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_small_pp.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_small_pp,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for small negative * positive
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_small_np

def test_small_np( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_small_np.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_small_np,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for small positive * negative
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_small_pn

def test_small_pn( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_small_pn.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_small_pn,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for small negative * negative
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_small_nn

def test_small_nn( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_small_nn.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_small_nn,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for large positive * positive
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_large_pp

def test_large_pp( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_large_pp.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_large_pp,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test for large negative * negative
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_large_nn

def test_large_nn( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_large_nn.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_large_nn,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat unit test with delay
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import test_msgs_all

def test_delay5x10( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_delay50x50.vcd",
                 IntMulIterVarLat, 5, 10, test_msgs_all,
                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat random testing
#-------------------------------------------------------------------------

from new_imul.IntMulBL_test import mul_test_msgs_random

def test_random( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_random.vcd",
                 IntMulIterVarLat, 0, 0, mul_test_msgs_random,
                 test_verilog )

def test_random_delay5x10( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_random_delay5x10.vcd",
                 IntMulIterVarLat, 5, 10, mul_test_msgs_random,
                 test_verilog )

#-------------------------------------------------------------------------
# Extra tests specifically for variable latency multiplier
#-------------------------------------------------------------------------
# You need to add tests here which effectively test the details of your
# variable latency implementation (i.e., gray box testing). Think
# critically about what each test really tests. Feel free to add extra
# test cases or just put all your tests here in this one test case.

#-------------------------------------------------------------------------
# IntMulIterVarLat trailing zores (TZ) testing
#-------------------------------------------------------------------------

test_msgs_var_lat_tz = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP, 0x00000000, 0x00000000), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000000), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000000), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000001), B( 0x00000002 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000001), B( 0xffffffff ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000002), B( 0x00000004 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000002), B( 0xfffffffe ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000003), B( 0x00000006 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000003), B( 0xfffffffd ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000004), B( 0x00000008 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000004), B( 0xfffffffc ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000005), B( 0x0000000a ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000005), B( 0xfffffffb ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x00000007), B( 0x0000000e ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000007), B( 0xfffffff9 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x0000000f), B( 0x0000001e ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x0000000f), B( 0xfffffff1 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x000000ff), B( 0x000001fe ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x000000ff), B( 0xffffff01 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x0000ffff), B( 0x0001fffe ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x0000ffff), B( 0xffff0001 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x3fffffff), B( 0x7ffffffe ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x3fffffff), B( 0xC0000001 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x7fffffff), B( 0xfffffffe ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x7fffffff), B( 0x80000001 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x7aaaaaaa), B( 0xf5555554 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x7aaaaaaa), B( 0x85555556 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xffffffff), B( 0xfffffffe ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xffffffff), B( 0x00000001 ),
]

def test_var_lat_tz( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_tz.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_tz,
                 test_verilog )

#def test_var_lat_tz_delay5x10( dump_vcd, test_verilog ):
#  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_tz_delay5x10.vcd",
#                 IntMulIterVarLat, 50, 50, test_msgs_var_lat_tz,
#                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat leading zores (LZ) testing
#-------------------------------------------------------------------------

test_msgs_var_lat_lz = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xfffffffe), B( 0xfffffffc ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xfffffffe), B( 0x00000002 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xfffffffc), B( 0xfffffff8 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xfffffffc), B( 0x00000004 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xfffffff8), B( 0xfffffff0 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xfffffff8), B( 0x00000008 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xfffffff0), B( 0xffffffe0 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xfffffff0), B( 0x00000010 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xffffff00), B( 0xfffffe00 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xffffff00), B( 0x00000100 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xff00ff00), B( 0xfe01fe00 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xff00ff00), B( 0x00ff0100 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xff000000), B( 0xfe000000 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xff000000), B( 0x01000000 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x80000000), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x80000000), B( 0x80000000 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x80000001), B( 0x00000002 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x80000001), B( 0x7fffffff ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x80010001), B( 0x00020002 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x80010001), B( 0x7ffeffff ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0xaaaaaaaa), B( 0x55555554 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0xaaaaaaaa), B( 0x55555556 ),
  createMulDivMessage( idx.MUL_OP, 0x00000002, 0x99999999), B( 0x33333332 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x99999999), B( 0x66666667 ),
]

def test_var_lat_lz( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lz.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_lz,
                 test_verilog )

#def test_var_lat_lz_delay5x10( dump_vcd, test_verilog ):
#  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lz_delay5x10.vcd",
#                 IntMulIterVarLat, 50, 50, test_msgs_var_lat_lz,
#                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat input swap (IS) testing
#-------------------------------------------------------------------------

test_msgs_var_lat_is = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP, 0x00000000, 0xffffffff), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000000), B( 0x00000000 ),
  createMulDivMessage( idx.MUL_OP, 0x00000001, 0xffffffff), B( 0xffffffff ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x00000001), B( 0xffffffff ),
  createMulDivMessage( idx.MUL_OP, 0x000000ff, 0xffffffff), B( 0xffffff01 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x000000ff), B( 0xffffff01 ),
  createMulDivMessage( idx.MUL_OP, 0x0000ffff, 0xffffffff), B( 0xffff0001 ),
  createMulDivMessage( idx.MUL_OP, 0xffffffff, 0x0000ffff), B( 0xffff0001 ),
  createMulDivMessage( idx.MUL_OP, 0x0000ffff, 0x0001ffff), B( 0xfffd0001 ),
  createMulDivMessage( idx.MUL_OP, 0x0001ffff, 0x0000ffff), B( 0xfffd0001 ),
]

def test_var_lat_is( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_is.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_is,
                 test_verilog )

#def test_var_lat_is_delay5x10( dump_vcd, test_verilog ):
#  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_is_delay5x10.vcd",
#                 IntMulIterVarLat, 50, 50, test_msgs_var_lat_is,
#                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat leading ones (LO) testing
#-------------------------------------------------------------------------

test_msgs_var_lat_lo = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000001), B( 0x0fffffff ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000003), B( 0x2ffffffd ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000007), B( 0x6ffffff9 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0000000f), B( 0xeffffff1 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0000ffff), B( 0xefff0001 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00ffffff), B( 0xef000001 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000010), B( 0xfffffff0 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000030), B( 0xffffffd0 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000070), B( 0xffffff90 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x000000f0), B( 0xffffff10 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000ff0), B( 0xfffff010 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x000ffff0), B( 0xfff00010 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0f0f0f0f), B( 0xe0f0f0f1 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x07777777), B( 0x68888889 ),
]

def test_var_lat_lo( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lo.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_lo,
                 test_verilog )

#def test_var_lat_lo_delay5x10( dump_vcd, test_verilog ):
#  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lo_delay5x10.vcd",
#                 IntMulIterVarLat, 50, 50, test_msgs_var_lat_lo )
#                 test_verilog )

#-------------------------------------------------------------------------
# IntMulIterVarLat left bound swap (LB) testing
#-------------------------------------------------------------------------

test_msgs_var_lat_lb = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP, 0x00000010, 0x00000001), B( 0x00000010 ),
  createMulDivMessage( idx.MUL_OP, 0x00000001, 0x00000010), B( 0x00000010 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x00000001), B( 0x0fffffff ),
  createMulDivMessage( idx.MUL_OP, 0x00000001, 0x0fffffff), B( 0x0fffffff ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0000ffff), B( 0xefff0001 ),
  createMulDivMessage( idx.MUL_OP, 0x0000ffff, 0x00ffffff), B( 0xfeff0001 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0aaaaaaa), B( 0x95555556 ),
  createMulDivMessage( idx.MUL_OP, 0x0aaaaaaa, 0x00ffffff), B( 0x9f555556 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x0f0f0f0f), B( 0xe0f0f0f1 ),
  createMulDivMessage( idx.MUL_OP, 0x0fffffff, 0x07777777), B( 0x68888889 ),
  createMulDivMessage( idx.MUL_OP, 0x07777777, 0x0fffffff), B( 0x68888889 ),
  createMulDivMessage( idx.MUL_OP, 0x0aaaaaaa, 0x07777777), B( 0x45B05B06 ),
  createMulDivMessage( idx.MUL_OP, 0x07777777, 0x0aaaaaaa), B( 0x45B05B06 ),
  createMulDivMessage( idx.MUL_OP, 0x0ccccccc, 0x03333333), B( 0x8A3D70A4 ),
  createMulDivMessage( idx.MUL_OP, 0x03333333, 0x0ccccccc), B( 0x8A3D70A4 ),
  createMulDivMessage( idx.MUL_OP, 0x8ccccccc, 0x03333333), B( 0x0A3D70A4 ),
  createMulDivMessage( idx.MUL_OP, 0x83333333, 0x0ccccccc), B( 0x8A3D70A4 ),
]

def test_var_lat_lb( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lb.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_lb,
                 test_verilog )

#def test_var_lat_lb_delay5x10( dump_vcd, test_verilog ):
#  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_lb_delay5x10.vcd",
#                 IntMulIterVarLat, 50, 50, test_msgs_var_lat_lb,
#                 test_verilog )





#-------------------------------------------------------------------------
# Sign bit test
#-------------------------------------------------------------------------

test_msgs_var_lat_sb = [
  #                                operand A   operand B    result
  createMulDivMessage( idx.MUL_OP,         1,          1),  B(     1 ),
  createMulDivMessage( idx.MUL_OP,        -1,          4),  B(    -4 ),
  createMulDivMessage( idx.MUL_OP,       -16,          5),  B(   -80 ),
  createMulDivMessage( idx.MUL_OP,         5,         21),  B(   105 ),
  createMulDivMessage( idx.MUL_OP,         5,        -21),  B(  -105 ),
  createMulDivMessage( idx.MUL_OP,      1231,         -1),  B( -1231 ),
  createMulDivMessage( idx.MUL_OP,     -1231,         -1),  B(  1231 ),
  createMulDivMessage( idx.MUL_OP,     22222,          2),  B( 44444 ),
]

def test_var_lat_sb( dump_vcd, test_verilog ):
  run_imul_test( dump_vcd, "pex-imul-IntMulIterVarLat_test_var_lat_sb.vcd",
                 IntMulIterVarLat, 0, 0, test_msgs_var_lat_sb,
                 test_verilog )
