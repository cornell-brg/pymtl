#=======================================================================
# Mux.py
#=======================================================================

from pymtl import *

#-----------------------------------------------------------------------
# Mux
#-----------------------------------------------------------------------
class Mux( Model ):
  '''Multiplexor parameterizable by ports and bitwidth.'''

  def __init__( s, nbits = 1, nports = 2 ):

    nsel  = get_sel_nbits( nports )

    s.in_ = [ InPort( nbits ) for x in xrange( nports ) ]
    s.sel = InPort  ( nsel )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      assert s.sel < nports
      s.out.v = s.in_[ s.sel ]

  def line_trace( s ):
    return "{} {} {} () {}".format( s.in_[0], s.in_[1], s.sel, s.out )
