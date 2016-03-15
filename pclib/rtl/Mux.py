#=======================================================================
# Mux.py
#=======================================================================

from pymtl import *

#-----------------------------------------------------------------------
# Mux
#-----------------------------------------------------------------------
class Mux( Model ):
  'Multiplexor parameterizable by ports and datatype.'

  def __init__( s, dtype = 1, nports = 2 ):

    nsel  = clog2( nports )

    # round-up the number of cells to the nearest power of 2
    ncels = 2 ** nsel

    s.in_ = [ InPort( dtype ) for _ in range( ncels ) ]
    s.sel = InPort  ( nsel )
    s.out = OutPort ( dtype )

    @s.combinational
    def comb_logic():
      assert s.sel < nports
      s.out.v = s.in_[ s.sel ]

  def line_trace( s ):
    return "{} {} {} () {}".format( s.in_[0], s.in_[1], s.sel, s.out )
