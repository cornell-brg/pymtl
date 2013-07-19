#=========================================================================
# Mux
#=========================================================================
# Module containing the Mux model.

from new_pymtl import *

#-------------------------------------------------------------------------
# Mux
#-------------------------------------------------------------------------
# Multiplexor parameterizable by ports and bitwidth.
class Mux( Model ):

  @capture_args
  def __init__( s, nbits = 1, nports = 2 ):

    s.nports = nports
    s.nsel   = get_sel_nbits( nports )

    s.in_ = [ InPort( nbits ) for x in xrange( nports ) ]
    s.sel = InPort  ( s.nsel )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      assert s.sel < s.nports
      s.out.v = s.in_[ s.sel ]

  def line_trace( s ):
    return "{} {} {} () {}".format( s.in_[0], s.in_[1], s.sel, s.out )
