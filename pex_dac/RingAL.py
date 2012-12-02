#=========================================================================
# Architecture Level Physical Design Example
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# Router
#-------------------------------------------------------------------------

class Router( Model ):

  def __init__( s, router_sz ):
    s.router_sz = router_sz

  def physical_elaboration( s ):
    w, h = s.router_sz
    s._dim.w = w
    s._dim.h = h

#-------------------------------------------------------------------------
# Ring
#-------------------------------------------------------------------------

class RingAL( Model ):

  def __init__( s, num_routers=8, router_sz=(20,20), link_len=40 ):
    s.router_sz = router_sz
    s.link_len  = link_len
    s.routers   = [ Router( router_sz )
                    for x in range( num_routers ) ]

  def physical_elaboration( s ):
    max = len( s.routers )
    for i, r in enumerate( s.routers ):
      r.physical_elaboration()
      if i < (max / 2):
        r._dim.x = i * ( r._dim.w + s.link_len )
        r._dim.y = 0
      else:
        r._dim.x = (max - i - 1) * ( r._dim.w + s.link_len )
        r._dim.y = r._dim.h + s.link_len

    half = max / 2
    s._dim.w = half * r._dim.w + (half - 1) * s.link_len
    s._dim.h = 2 * r._dim.h + s.link_len

#-------------------------------------------------------------------------
# Physical Elaboration
#-------------------------------------------------------------------------

def test_dump():
  model = RingAL( 8, (200,300), (400) )
  model.elaborate()
  model.physical_elaboration()
  print
  model.dump_physical_design()


