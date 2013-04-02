#=========================================================================
# helpers_test.py
#=========================================================================

from helpers import *
from Bits    import Bits

def test_get_nbits():

  assert get_nbits( 0 ) == 1
  assert get_nbits( 1 ) == 1
  assert get_nbits( 2 ) == 2
  assert get_nbits( 3 ) == 2
  assert get_nbits( 4 ) == 3
  assert get_nbits( 5 ) == 3
  assert get_nbits( 6 ) == 3
  assert get_nbits( 7 ) == 3
  assert get_nbits( 8 ) == 4

  assert get_nbits( 0x000f ) == 4
  assert get_nbits( 0x00ff ) == 8
  assert get_nbits( 0x0fff ) == 12
  assert get_nbits( 0xffff ) == 16

  assert get_nbits( -1 ) == 2
  assert get_nbits( -2 ) == 3
  assert get_nbits( -3 ) == 3
  assert get_nbits( -4 ) == 4
  assert get_nbits( -5 ) == 4
  assert get_nbits( -6 ) == 4
  assert get_nbits( -7 ) == 4
  assert get_nbits( -8 ) == 5


def test_zext():

  assert zext( Bits( 4,  2 ),  8 ) == Bits( 8, 0x02 )
  assert zext( Bits( 4,  4 ),  8 ) == Bits( 8, 0x04 )
  assert zext( Bits( 4, 15 ),  8 ) == Bits( 8, 0x0f )

  assert zext( Bits( 4, -2  ), 8 ) == Bits( 8, 0x0e )
  assert zext( Bits( 4, -4  ), 8 ) == Bits( 8, 0x0c )


def test_sext():

  assert sext( Bits( 4,  2 ), 8 )  == Bits( 8, 0x02 )
  assert sext( Bits( 4,  4 ), 8 )  == Bits( 8, 0x04 )
  assert sext( Bits( 4, 15 ), 8 )  == Bits( 8, 0xff )

  assert sext( Bits( 4, -2  ), 8 ) == Bits( 8, 0xfe )
  assert sext( Bits( 4, -4  ), 8 ) == Bits( 8, 0xfc )


def test_concat():

  assert concat([ Bits(4,0xf), Bits(4,0x2) ]) == Bits( 8, 0xf2 )
  assert concat([ Bits(2,0x2), Bits(4,0xf) ]) == Bits( 6, 0x2f )

  assert concat([ Bits(2,0x2), Bits(4,0), Bits(4,0xf) ]) == Bits( 10, 0x20f )
  assert concat([ Bits(4,0x2), Bits(4,0), Bits(4,0xf) ]) == Bits( 12, 0x20f )

