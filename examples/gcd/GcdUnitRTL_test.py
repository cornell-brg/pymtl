#=========================================================================
# GcdUnitRTL Test Suite
#=========================================================================

import pytest

from pymtl import *

from GcdUnitRTL import GcdUnitRTL

# We can use the same test harness from the behavioral-level model

from GcdUnitBL_test import run_gcd_test

#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  (  0,  0),
  ( 10,  5),
  (  5, 10),
])
def test( dump_vcd, src_delay, sink_delay ):
  run_gcd_test( dump_vcd, False, GcdUnitRTL, src_delay, sink_delay )
