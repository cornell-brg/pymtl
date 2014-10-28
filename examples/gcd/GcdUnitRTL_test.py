#=========================================================================
# GcdUnitRTL Test Suite
#=========================================================================

from pymtl import *

from GcdUnitRTL import GcdUnitRTL

# We can use the same test harness from the behavioral-level model

from GcdUnitBL_test import run_gcd_test

#-------------------------------------------------------------------------
# GcdUnitRTL unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd, test_verilog ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitRTL_test_delay0x0.vcd",
                test_verilog, GcdUnitRTL, 0, 0 )

#-------------------------------------------------------------------------
# GcdUnitRTL unit test with delay = 10 x 5
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd, test_verilog ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitRTL_test_delay10x5.vcd",
                test_verilog, GcdUnitRTL, 10, 5 )

#-------------------------------------------------------------------------
# GcdUnitRTL unit test with delay = 5 x 10
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd, test_verilog ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitRTL_test_delay5x10.vcd",
                test_verilog, GcdUnitRTL, 5, 10 )

