#=========================================================================
# SorterRTL Test Suite
#=========================================================================

from new_pymtl import *

from SorterRTL import SorterRTL

# We can use the same test harness from the cycle-level model

from SorterCL_test import run_sorter_test

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

from SorterCL_test import test_vectors_basics

def test_basics( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterRTL_test_basics.vcd",
                   SorterRTL, test_vectors_basics )

#-------------------------------------------------------------------------
# Test duplicates
#-------------------------------------------------------------------------

from SorterCL_test import test_vectors_duplicates

def test_duplicates( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterRTL_test_duplicates.vcd",
                   SorterRTL, test_vectors_duplicates )

#-------------------------------------------------------------------------
# Test random
#-------------------------------------------------------------------------

from SorterCL_test import test_vectors_random

def test_random( dump_vcd ):
  run_sorter_test( dump_vcd, "pex-sorter-SorterRTL_test_random.vcd",
                   SorterRTL, test_vectors_random )

