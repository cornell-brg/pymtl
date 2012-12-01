#=========================================================================
# Register Transfer Level Physical Design Example
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# Mux
#-------------------------------------------------------------------------

class Mux( Model ):

  def __init__( s, cell_sz ):
    s.cell_sz = cell_sz

  def physical_elaboration( s ):
    w, h = s.cell_sz
    s._dim.w = w
    s._dim.h = h

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Register( Model ):

  def __init__( s, cell_sz ):
    s.cell_sz = cell_sz

  def physical_elaboration( s ):
    w, h = s.cell_sz
    s._dim.w = w
    s._dim.h = h

#-------------------------------------------------------------------------
# RouterDpath
#-------------------------------------------------------------------------

class RouterDpathRTL( Model ):

  def __init__( s, nary, mux_sz, reg_sz):
    s.nary    = nary
    s.regs    = [ Register( mux_sz ) for x in range( nary ) ]
    s.muxs    = [ Mux( reg_sz )      for x in range( nary ) ]

  def physical_elaboration( s ):
    for x in s.get_submodules():
      x.physical_elaboration()

    row_height = max( s.regs[0]._dim.h, s.muxs[0]._dim.h )
    for i in range( s.nary ):
      reg = s.regs[i]
      mux = s.muxs[i]
      reg._dim.x = 0
      mux._dim.x = s.regs[i]._dim.w
      reg._dim.y = i * row_height
      mux._dim.y = i * row_height
    s._dim.w = reg._dim.w + mux._dim.w
    s._dim.h = row_height * s.nary


#-------------------------------------------------------------------------
# Physical Elaboration
#-------------------------------------------------------------------------

def test_dump():
  model = RouterDpathRTL( 4, (9,14), (5, 10) )
  model.elaborate()
  model.physical_elaboration()
  print
  model.dump_physical_design()

