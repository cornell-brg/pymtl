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

      # TODO: fix to use PortLists !
      s.out.v = s.in_[ s.sel.uint() ]

  def line_trace( s ):
    return "{:04x} {:04x} {:01x} () {:04x}" \
      .format( s.in_[0].uint(), s.in_[1].uint(),
               s.sel.uint(), s.out.uint() )
