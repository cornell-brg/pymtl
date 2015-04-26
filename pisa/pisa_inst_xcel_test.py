#=========================================================================
# pisa_inst_xcel_test.py
#=========================================================================

import pytest
import random
import pisa_encoding

from pymtl   import Bits
from PisaSim import PisaSim

from pisa_inst_test_utils import *

#-------------------------------------------------------------------------
# gen_basic_asm_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    mfc0 r2, mngr2proc < 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtx  r2, r0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mfx  r3, r0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtc0 r3, proc2mngr > 1
  """

#-------------------------------------------------------------------------
# gen_bypass_mtx_test
#-------------------------------------------------------------------------

def gen_bypass_mtx_test():
  return """

    mfc0 r2, mngr2proc < 0xdeadbeef
    {nops_3}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_7}
    mtc0 r3, proc2mngr > 0xdeadbeef

    mfc0 r2, mngr2proc < 0x0a0a0a0a
    {nops_2}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_7}
    mtc0 r3, proc2mngr > 0x0a0a0a0a

    mfc0 r2, mngr2proc < 0x0b0b0b0b
    {nops_1}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_7}
    mtc0 r3, proc2mngr > 0x0b0b0b0b

    mfc0 r2, mngr2proc < 0x0c0c0c0c
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_7}
    mtc0 r3, proc2mngr > 0x0c0c0c0c

  """.format(
    nops_7=gen_nops(7),
    nops_3=gen_nops(3),
    nops_2=gen_nops(2),
    nops_1=gen_nops(1)
  )

#-------------------------------------------------------------------------
# gen_bypass_mfx_test
#-------------------------------------------------------------------------

def gen_bypass_mfx_test():
  return """

    mfc0 r2, mngr2proc < 0xdeadbeef
    {nops_7}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_3}
    mtc0 r3, proc2mngr > 0xdeadbeef

    mfc0 r2, mngr2proc < 0x0a0a0a0a
    {nops_7}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_2}
    mtc0 r3, proc2mngr > 0x0a0a0a0a

    mfc0 r2, mngr2proc < 0x0b0b0b0b
    {nops_7}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    {nops_1}
    mtc0 r3, proc2mngr > 0x0b0b0b0b

    mfc0 r2, mngr2proc < 0x0c0c0c0c
    {nops_7}
    mtx  r2, r0
    {nops_7}
    mfx  r3, r0
    mtc0 r3, proc2mngr > 0x0c0c0c0c

  """.format(
    nops_7=gen_nops(7),
    nops_3=gen_nops(3),
    nops_2=gen_nops(2),
    nops_1=gen_nops(1)
  )

#-------------------------------------------------------------------------
# gen_bypass_test
#-------------------------------------------------------------------------

def gen_bypass_test():
  return """

    mfc0 r2, mngr2proc < 0xdeadbeef
    mtx  r2, r0
    {nops_3}
    mfx  r3, r0
    mtc0 r3, proc2mngr > 0xdeadbeef

    mfc0 r2, mngr2proc < 0x0a0a0a0a
    mtx  r2, r0
    {nops_2}
    mfx  r3, r0
    mtc0 r3, proc2mngr > 0x0a0a0a0a

    mfc0 r2, mngr2proc < 0x0b0b0b0b
    mtx  r2, r0
    {nops_1}
    mfx  r3, r0
    mtc0 r3, proc2mngr > 0x0b0b0b0b

    mfc0 r2, mngr2proc < 0x0c0c0c0c
    mtx  r2, r0
    mfx  r3, r0
    mtc0 r3, proc2mngr > 0x0c0c0c0c

  """.format(
    nops_3=gen_nops(3),
    nops_2=gen_nops(2),
    nops_1=gen_nops(1)
  )

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test      ),
  asm_test( gen_bypass_mtx_test ),
  asm_test( gen_bypass_mfx_test ),
  asm_test( gen_bypass_test ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

