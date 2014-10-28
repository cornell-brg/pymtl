#=======================================================================
# IntDivIterCL_test.py
#=======================================================================

from pymtl     import *
from new_pmlib     import TestSource, TestSink
from muldiv_msg    import BitStructIndex
from IntDivBL_test import run_idivrem_test
from IntDivIterCL  import IntDivIterCL

import random

#-----------------------------------------------------------------------
# Helpers
#-----------------------------------------------------------------------

idx = BitStructIndex()

# Accumulate all test messages for use when doing random delay testing
test_msgs_all = []

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

# Import test cases
from IntDivBL_test import div_test_msgs_small_pp
from IntDivBL_test import div_test_msgs_small_np
from IntDivBL_test import div_test_msgs_small_pn
from IntDivBL_test import div_test_msgs_small_nn
from IntDivBL_test import div_test_msgs_legacy
from IntDivBL_test import rem_test_msgs_legacy
from IntDivBL_test import divu_test_msgs_legacy
from IntDivBL_test import remu_test_msgs_legacy
from IntDivBL_test import div_test_msgs_large_pp
from IntDivBL_test import div_test_msgs_large_nn
from IntDivBL_test import div_test_msgs_random
from IntDivBL_test import rem_test_msgs_small_pp
from IntDivBL_test import rem_test_msgs_small_pn
from IntDivBL_test import rem_test_msgs_small_np
from IntDivBL_test import rem_test_msgs_small_nn
from IntDivBL_test import rem_test_msgs_large_pp
from IntDivBL_test import rem_test_msgs_large_nn
from IntDivBL_test import rem_test_msgs_random

#-------------------------------------------------------------------------
# div unit test for small positive / positive division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_pp )

def test_small_pp( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_pp.vcd",
                    model, 0, 0, div_test_msgs_small_pp )

#-------------------------------------------------------------------------
# div unit test for small negative / positive division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_np )

def test_small_np( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_np.vcd",
                    model, 0, 0, div_test_msgs_small_np )

#-------------------------------------------------------------------------
# div unit test for small positive / negative division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_pn )

def test_small_pn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_pn.vcd",
                    model, 0, 0, div_test_msgs_small_pn )

#-------------------------------------------------------------------------
# div unit test for small negative / negative division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_small_nn )

def test_small_nn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_nn.vcd",
                    model, 0, 0, div_test_msgs_small_nn )

#-------------------------------------------------------------------------
# div legacy test
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_legacy )

def test_div_legacy( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-legacy-IntDivBL_test.vcd",
                    model, 0, 0, div_test_msgs_legacy )


#-------------------------------------------------------------------------
# rem legacy test
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_legacy )

def test_rem_legacy( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-irem-legacy-IntDivBL_test.vcd",
                    model, 0, 0, rem_test_msgs_legacy )

#-------------------------------------------------------------------------
# divu legacy test
#-------------------------------------------------------------------------

test_msgs_all.extend( divu_test_msgs_legacy )

def test_divu_legacy( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idivu-legacy-IntDivBL_test.vcd",
                    model, 0, 0, divu_test_msgs_legacy )

#-------------------------------------------------------------------------
# remu legacy test
#-------------------------------------------------------------------------

test_msgs_all.extend( remu_test_msgs_legacy )

def test_remu_legacy( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-iremu-legacy-IntDivBL_test.vcd",
                    model, 0, 0, remu_test_msgs_legacy )

#-------------------------------------------------------------------------
# div unit test for large positive / positive division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_large_pp )

def test_large_pp( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_large_pp.vcd",
                    model, 0, 0, div_test_msgs_large_pp )

#-------------------------------------------------------------------------
# div unit test for large negative / negative division
#-------------------------------------------------------------------------

test_msgs_all.extend( div_test_msgs_large_nn )

def test_large_nn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_large_nn.vcd",
                    model, 0, 0, div_test_msgs_large_nn )

#-------------------------------------------------------------------------
# div unit test with delay = 10 x 5 division
#-------------------------------------------------------------------------

def test_delay5x10( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_delay5x10.vcd",
                    model, 5, 10, test_msgs_all )

#-------------------------------------------------------------------------
# div unit test with delay = 10 x 5 division
#-------------------------------------------------------------------------

def test_delay10x5( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_delay10x5.vcd",
                    model, 10, 5, test_msgs_all )

#-------------------------------------------------------------------------
# div random testing
#-------------------------------------------------------------------------
# Create random inputs with reference outputs.

def test_random( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_random.vcd",
                    model, 0, 0, div_test_msgs_random )

def test_random_delay5x10( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_random_delay5x10.vcd",
                    model, 5, 10, div_test_msgs_random )

def test_random_delay10x5( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_random_delay10x5.vcd",
                    model, 10, 5, div_test_msgs_random )

#-------------------------------------------------------------------------
# rem unit test for small positive % positive remainder
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_pp )

def test_remainder_small_pp( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_pp.vcd",
                    model, 0, 0, rem_test_msgs_small_pp )

#-------------------------------------------------------------------------
# rem unit test for small positive % negative remainder
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_pn )

def test_remainder_small_pn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_pn.vcd",
                    model, 0, 0, rem_test_msgs_small_pn )

#-------------------------------------------------------------------------
# rem unit test for small negative % positive remainder
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_np )

def test_remainder_small_np( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_np.vcd",
                    model, 0, 0, rem_test_msgs_small_np )

#-------------------------------------------------------------------------
# rem unit test for small negative % negative remainder
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_small_nn )

def test_remainder_small_nn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_small_nn.vcd",
                    model, 0, 0, rem_test_msgs_small_nn )

#-------------------------------------------------------------------------
# rem unit test for large positive / positive
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_large_pp )

def test_remainder_large_pp( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivIterCL_test_large_pp.vcd",
                    model, 0, 0, rem_test_msgs_large_pp )

#-------------------------------------------------------------------------
# rem unit test for large negative / negative
#-------------------------------------------------------------------------

test_msgs_all.extend( rem_test_msgs_large_nn )

def test_remainder_large_nn( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-irem-IntDivIterCL_test_large_nn.vcd",
                    model, 0, 0, rem_test_msgs_large_nn )

#-------------------------------------------------------------------------
# rem random testing
#-------------------------------------------------------------------------
# Create random inputs with reference outputs.

def test_remainder_random( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_random.vcd",
                    model, 0, 0, rem_test_msgs_random )

def test_remainder_random_delay5x10( dump_vcd ):
  model = IntDivIterCL()
  run_idivrem_test( dump_vcd, "pex-idiv-IntDivIterCL_test_random_delay5x10.vcd",
                    model, 5, 10, rem_test_msgs_random )

