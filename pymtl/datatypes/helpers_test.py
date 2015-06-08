#=======================================================================
# helpers_test.py
#=======================================================================

import pytest

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


def test_clog2():

  assert clog2( 1 ) == 0  # TODO: return 1 or 0 here?
  assert clog2( 2 ) == 1
  assert clog2( 3 ) == 2
  assert clog2( 4 ) == 2
  assert clog2( 5 ) == 3
  assert clog2( 6 ) == 3
  assert clog2( 7 ) == 3
  assert clog2( 8 ) == 3
  assert clog2( 9 ) == 4

  assert clog2(  16 ) == 4
  assert clog2(  32 ) == 5
  assert clog2(  64 ) == 6
  assert clog2( 128 ) == 7
  assert clog2( 256 ) == 8

  assert get_nbits( 0x000f ) == 4
  assert get_nbits( 0x00ff ) == 8
  assert get_nbits( 0x0fff ) == 12
  assert get_nbits( 0xffff ) == 16

  with pytest.raises( AssertionError ):
    assert clog2( 0 ) == 1

  with pytest.raises( AssertionError ):
    assert clog2( -1 ) == 2


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

  assert concat( Bits(4,0xf), Bits(4,0x2) ) == Bits( 8, 0xf2 )
  assert concat( Bits(2,0x2), Bits(4,0xf) ) == Bits( 6, 0x2f )

  assert concat( Bits(2,0x2), Bits(4,0), Bits(4,0xf) ) == Bits( 10, 0x20f )
  assert concat( Bits(4,0x2), Bits(4,0), Bits(4,0xf) ) == Bits( 12, 0x20f )

def test_reduce_and():

  assert reduce_and( Bits(2,0b11) ) == 1
  assert reduce_and( Bits(2,0b01) ) == 0
  assert reduce_and( Bits(2,0b10) ) == 0
  assert reduce_and( Bits(2,0b00) ) == 0

  assert reduce_and( Bits(4,0b1111) ) == 1
  assert reduce_and( Bits(4,0b1010) ) == 0
  assert reduce_and( Bits(4,0b0101) ) == 0
  assert reduce_and( Bits(4,0b0000) ) == 0

def test_reduce_or():

  assert reduce_or( Bits(2,0b11) ) == 1
  assert reduce_or( Bits(2,0b01) ) == 1
  assert reduce_or( Bits(2,0b10) ) == 1
  assert reduce_or( Bits(2,0b00) ) == 0

  assert reduce_or( Bits(4,0b1111) ) == 1
  assert reduce_or( Bits(4,0b1010) ) == 1
  assert reduce_or( Bits(4,0b0101) ) == 1
  assert reduce_or( Bits(4,0b0000) ) == 0

def test_reduce_xor():
  assert reduce_xor( Bits(2,0b11) ) == 0
  assert reduce_xor( Bits(2,0b01) ) == 1
  assert reduce_xor( Bits(2,0b10) ) == 1
  assert reduce_xor( Bits(2,0b00) ) == 0

  assert reduce_xor( Bits(4,0b1111) ) == 0
  assert reduce_xor( Bits(4,0b1010) ) == 0
  assert reduce_xor( Bits(4,0b0101) ) == 0
  assert reduce_xor( Bits(4,0b0000) ) == 0

  assert reduce_xor( Bits(4,0b1001) ) == 0

  assert reduce_xor( Bits(4,0b1110) ) == 1
  assert reduce_xor( Bits(4,0b1101) ) == 1
  assert reduce_xor( Bits(4,0b1011) ) == 1
  assert reduce_xor( Bits(4,0b0111) ) == 1

  assert reduce_xor( Bits(4,0b0001) ) == 1
  assert reduce_xor( Bits(4,0b0010) ) == 1
  assert reduce_xor( Bits(4,0b0100) ) == 1
  assert reduce_xor( Bits(4,0b1000) ) == 1

  assert reduce_xor( Bits(3,0b111) ) == 1
  assert reduce_xor( Bits(3,0b100) ) == 1
  assert reduce_xor( Bits(3,0b010) ) == 1
  assert reduce_xor( Bits(3,0b001) ) == 1
  assert reduce_xor( Bits(3,0b011) ) == 0
  assert reduce_xor( Bits(3,0b101) ) == 0
  assert reduce_xor( Bits(3,0b110) ) == 0
  assert reduce_xor( Bits(3,0b000) ) == 0
