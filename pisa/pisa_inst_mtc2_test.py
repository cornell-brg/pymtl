#=========================================================================
# pisa_mtc2_test.py
#=========================================================================

import pytest
import random
import pisa_encoding

from pymtl import Bits
from PisaSim   import PisaSim

from pisa_inst_test_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    #---------------------------------------------------------------------
    # First use of accelerator
    #---------------------------------------------------------------------

    # Get configuration values from manager

    mfc0  r1, mngr2proc < 4      # size
    mfc0  r2, mngr2proc < 0x2000 # src0_addr
    mfc0  r3, mngr2proc < 0x2010 # src1_addr
    mfc0  r4, mngr2proc < 0x2020 # dest

    # Configure the accelerator

    mtc2  r1, r1
    mtc2  r2, r2
    mtc2  r3, r3
    mtc2  r4, r4

    # Start the accelerator

    addiu r1, r0, 1
    mtc2  r1, r0

    # Retrieve the result

    lw    r5, 0(r4)
    mtc0  r5, proc2mngr > 6664

    #---------------------------------------------------------------------
    # Second use of accelerator
    #---------------------------------------------------------------------

    # Get configuration values from manager

    mfc0  r1, mngr2proc < 4      # size
    mfc0  r2, mngr2proc < 0x2030 # src0_addr
    mfc0  r3, mngr2proc < 0x2040 # src1_addr
    mfc0  r4, mngr2proc < 0x2050 # dest

    # Configure the accelerator

    mtc2  r1, r1
    mtc2  r2, r2
    mtc2  r3, r3
    mtc2  r4, r4

    # Start the accelerator

    addiu r1, r0, 1
    mtc2  r1, r0

    # Retrieve the result

    lw    r5, 0(r4)
    mtc0  r5, proc2mngr > 9941

    #---------------------------------------------------------------------
    # data
    #---------------------------------------------------------------------

    .data

    # src0 array
    .word 07
    .word 36
    .word 30
    .word 93

    # src1 array
    .word 58
    .word 88
    .word 41
    .word 20

    # destination
    .word 0xdeadbeef
    .word 0
    .word 0
    .word 0

    # src0 array
    .word 07
    .word 36
    .word 57
    .word 93

    # src1 array
    .word  2
    .word 88
    .word 99
    .word 12

    # destination
    .word 0xdeadbeef
    .word 0
    .word 0
    .word 0

  """

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( gen_basic_test     ),
])
def test( name, test ):
  sim = PisaSim( trace_en=True )
  sim.load( pisa_encoding.assemble( test() ) )
  sim.run()

