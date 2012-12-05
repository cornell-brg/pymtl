#=========================================================================
# Gate Level Physical Design Example
#=========================================================================

from pymtl import *

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
# Queue
#-------------------------------------------------------------------------

class QueueGL( Model ):

  def __init__( s, entries=8, nbits=16, cell_sz=(5,10) ):
    s.entries = entries
    s.nbits   = nbits
    s.regs    = [ Register( cell_sz )
                  for x in range( entries * nbits ) ]

  def physical_elaboration( s ):
    for i in range( s.entries ):
      for j in range( s.nbits ):
        reg = s.regs[ i * s.nbits + j ]
        reg.physical_elaboration()
        reg._dim.x = i * reg._dim.w
        reg._dim.y = j * reg._dim.h
    s._dim.w = s.entries * reg._dim.w
    s._dim.h = s.nbits   * reg._dim.h


#-------------------------------------------------------------------------
# Physical Elaboration
#-------------------------------------------------------------------------

def test_dump():
  model = QueueGL( 3, 16, (5,10) )
  model.elaborate()
  model.physical_elaboration()
  print
  model.dump_physical_design()
