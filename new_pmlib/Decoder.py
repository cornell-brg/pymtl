#==============================================================================
# Decoder.py
#==============================================================================

from new_pymtl import *

class Decoder( Model ):
  def __init__( s, sel_nbits, out_nbits ):
    s.in_ = InPort ( sel_nbits )
    s.out = OutPort( out_nbits )

    s.out_nbits = out_nbits

  def elaborate_logic( s ):

    @s.combinational
    def logic():
      for i in range( s.out_nbits ):
        s.out[i].value = (s.in_ == i)

  def line_trace( s ):
    return '{} () {}'.format( s.in_, s.out )
