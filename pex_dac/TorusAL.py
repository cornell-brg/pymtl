#=========================================================================
# Architecture Level Physical Design Example
#=========================================================================

from pymtl import *
import math

#-------------------------------------------------------------------------
# Router
#-------------------------------------------------------------------------

class TorusRouter( Model ):

  def __init__( s, router_sz ):
    s.router_sz = router_sz

  def physical_elaboration( s ):
    w, h = s.router_sz
    s._dim.w = w
    s._dim.h = h

#-------------------------------------------------------------------------
# Ring
#-------------------------------------------------------------------------

class TorusAL( Model ):

  def __init__( s, num_routers=16, router_sz=(300,300), link_len=100 ):
    s.router_sz = router_sz
    s.link_len  = link_len
    s.routers   = [ TorusRouter( router_sz )
                    for x in range( num_routers ) ]

  def physical_elaboration( s ):
    edges = math.sqrt( len(s.routers) )
    assert edges % 1 == 0
    edges = int(edges)
    for i in range( edges ):
      for j in range( edges ):
        r = s.routers[ i + j*edges ]
        r.physical_elaboration()
        r._dim.x = i * ( r._dim.w + s.link_len )
        r._dim.y = j * ( r._dim.h + s.link_len )

    s._dim.w = edges * r._dim.w + (edges-1) * s.link_len
    s._dim.h = edges * r._dim.h + (edges-1) * s.link_len

#-------------------------------------------------------------------------
# Physical Elaboration
#-------------------------------------------------------------------------

def test_dump():
  model = TorusAL()
  model.elaborate()
  model.physical_elaboration()
  print
  model.dump_physical_design()

