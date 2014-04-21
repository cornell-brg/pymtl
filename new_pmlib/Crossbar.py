#=======================================================================
# Crossbar.py
#=======================================================================

from new_pymtl import *

class Crossbar( Model ):

  def __init__( s, nports, nbits ):

    s.nports  = nports
    sel_nbits = get_sel_nbits( nports )

    # Interface Ports

    s.in_    = [ InPort  ( nbits )     for x in range( nports ) ]
    s.out    = [ OutPort ( nbits )     for x in range( nports ) ]
    s.sel    = [ InPort  ( sel_nbits ) for x in range( nports ) ]

  def elaborate_logic( s ) :
    @s.combinational
    def comb_logic():

      for i in range( s.nports ):
        s.out[i].value = s.in_[ s.sel[ i ] ]

  def line_trace( s ):
    in_str  = ' '.join( [ str(x) for x in s.in_ ] )
    sel_str = ' '.join( [ str(x) for x in s.sel ] )
    out_str = ' '.join( [ str(x) for x in s.out ] )
    return '{} ( {} ) {}'.format( in_str, sel_str, out_str )
