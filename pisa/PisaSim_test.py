#=========================================================================
# PisaSim_test.py
#=========================================================================

from PisaSim import PisaSim
import pisa_encoding

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_fields_reg():

  # Create the memory image

  mem_image = pisa_encoding.assemble(
  """
    mfc0 r2, mngr2proc < 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mtc0 r2, proc2mngr > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """)

  sim = PisaSim()
  sim.load( mem_image )
  sim.run()

