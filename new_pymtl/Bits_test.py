from Bits import *
from Bits import _num_bits

def test_get_value():
  x = Bits( 8, 0b1100 )
  assert isinstance( x.uint(), int  )
  assert isinstance( x.int(),  int  )
  assert isinstance( x[1:2],   Bits )
  assert isinstance( x[0:4],   Bits )
  assert isinstance( x[2],     Bits )

def test_simple_overflow():
  width = 2
  x = Bits( width )
  tests = [
      (0, 0),
      (1, 1),
      (2, 2),
      (3, 3),
     # We can't do these because they are too big! -cbatten
     # (4, 0),
     # (5, 1),
     # (6, 2),
     # (7, 3),
      ]

  assert x.width == width
  for wr, rd in tests:
    x.write( wr )
    assert x.uint() == rd

# Not allowed to write a value that is too big! -cbatten
#
# def test_many_overflow():
#   for i in range(1,10):
#     x = Bits(i)
#     overflow_val = 2**i
#     for j in range(50):
#       x.write( j )
#       assert x.uint() ==  j % overflow_val

def test_neg_assign():
  x = Bits( 4, -1 )
  assert x.uint() == 0b1111
  x = Bits( 4, -2 )
  assert x.uint() == 0b1110

  # These are too big! -cbatten
  #
  # x.uint() = -15
  # assert x.uint() == 0b0001
  # x.uint() = -16
  # assert x.uint() == 0b0000
  # x.uint() = -17
  # assert x.uint() == 0b1111

def test_get_bit():
  x = Bits( 4, 0b1100 )
  assert x[3] == 1
  assert x[2] == 1
  assert x[1] == 0
  assert x[0] == 0
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1

  # Too big! -cbatten
  # x.uint() = 22
  # assert x[3] == 0
  # assert x[2] == 1
  # assert x[1] == 1
  # assert x[0] == 0

def test_get_slice():
  x = Bits( 4, 0b1100 )
  assert x[:] == 0b1100
  assert x[2:4] == 0b11
  assert x[0:1] == 0b0
  assert x[1:3] == 0b10
  # TODO: check out of bounds is caught
  #assert x[1:5] == 0b10
  # check open ended ranges
  assert x[1:] == 0b110
  assert x[:3] == 0b100

def test_set_bit():
  x = Bits( 4, 0b1100 )
  x[3] = 0
  assert x.uint() == 0b0100
  x[2] = 1
  assert x.uint() == 0b0100
  x[1] = 1
  assert x.uint() == 0b0110
  # TODO: ensure check
  #x[0] = 2
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1

def test_set_slice():
  x = Bits( 4, 0b1100 )
  x[:] = 0b0010
  assert x.uint() == 0b0010
  x[2:4] = 0b11
  assert x.uint() == 0b1110
  x[0:1] = 0b1
  assert x.uint() == 0b1111
  x[1:3] = 0b10
  assert x.uint() == 0b1101
  # TODO: check out of bounds is caught
  #assert x[1:5] == 0b10
  # check open ended ranges
  x[1:] = 0b001
  assert x.uint() == 0b0011
  x[:3] = 0b110
  assert x.uint() == 0b0110

def test_eq():
  x = Bits( 4, 0b1010 )
  assert x.uint() == x.uint()
  # TODO: compare objects by value or by id?
  assert x == x
  # Check the value
  assert x.uint() == 0b1010
  assert x.uint() == 0xA
  assert x.uint() == 10
  # Checking the equality operator
  assert x == 0b1010
  assert x == 0xA
  assert x == 10
  # Checking comparison with another bit container
  y = Bits( 4, 0b1010 )
  assert x.uint() == y.uint()
  # TODO: how should equality between Bits objects work?
  #       Same object? Same value? Same value and width?
  # assert x == y
  y = Bits( 8 , 0b1010 )
  assert x.uint() == y.uint()
  #assert x == y
  # Check the negatives
  x = Bits( 4, -1 )
  assert x.uint() == 0b1111
  assert x.uint() == 0xF
  assert x.uint() == 15
  # TODO: check -1?
  # assert x.uint() == -1
  # Checking the equality operator
  assert x == 0b1111
  assert x == 0xF
  assert x == 15
  #assert x == -1
  assert x.uint() == Bits(4, -1).uint()
  assert x == Bits(4, -1).uint()
  # TODO: see above comment on Bits object equality
  #assert x == Bits(4, -1)

def test_ne():
  x = Bits( 4, 0b1100 )
  y = Bits( 4, 0b0011 )
  # TODO: check width?
  assert x.uint() != y.uint()
  assert x != y
  # added for bug
  z = Bits(1, 0)
  assert z.uint() != 1L
  assert z != 1L

import pytest
@pytest.mark.xfail
def test_compare_uint_neg():
  x = Bits( 4, 2 )
  assert x      != -1
  assert x.uint() != -1
  assert x       > -1
  assert x.uint()  > -1
  assert x      >= -1
  assert x.uint() >= -1

@pytest.mark.xfail
def test_compare_int_neg():
  x = Bits( 4, -2 )
  #assert x     == -2  # Should fail
  assert x.int == -2
  assert x.int  > -1
  assert x.int >= -1

def test_lt():
  x = Bits( 4, 0b1100 )
  y = Bits( 4, 0b0011 )
  assert y.uint() < x.uint()
  assert y.uint() < 10
  assert y < x.uint()
  assert y < 10
  assert y < x

def test_gt():
  x = Bits( 4, 0b1100 )
  y = Bits( 4, 0b0011 )
  assert x.uint() > y.uint()
  assert x.uint() > 2
  assert x > y.uint()
  assert x > 2
  assert x > y

def test_lte():
  x = Bits( 4, 0b1100 )
  y = Bits( 4, 0b0011 )
  z = Bits( 4, 0b0011 )
  assert y.uint() <= x.uint()
  assert y.uint() <= 10
  assert y.uint() <= z.uint()
  assert y.uint() <= 0b0011
  assert y <= x.uint()
  assert y <= 10
  assert y <= z.uint()
  assert y <= 0b0011
  assert y <= x
  assert y <= z
  assert z <= x
  assert z <= z

def test_gte():
  x = Bits( 4, 0b1100 )
  y = Bits( 4, 0b0011 )
  z = Bits( 4, 0b1100 )
  assert x.uint() >= y.uint()
  assert x.uint() >= 2
  assert x.uint() >= z.uint()
  assert x.uint() >= 0b1100
  assert x >= y.uint()
  assert x >= 2
  assert x >= z.uint()
  assert x >= 0b1100
  assert x >= y
  assert x >= z
  assert z >= y
  assert z >= x
  assert x >= x

def test_invert():
  x = Bits( 4, 0b0001 )
  assert ~x == 0b1110
  x = Bits( 4, 0b1001 )
  assert ~x == 0b0110
  x = Bits( 16, 0b1111000011110000 )
  assert ~x == 0b0000111100001111

def test_add():
  x = Bits( 4, 4 )
  y = Bits( 4, 4 )
  assert x + y == 8
  assert x + Bits( 4, 4 ) == 8
  assert x + 4 == 8
  y = Bits( 4, 14 )
  assert x + y == 2
  assert x + 14 == 2

def test_sub():
  x = Bits( 4, 5 )
  y = Bits( 4, 4 )
  assert x - y == 1
  assert x - Bits(4, 4) == 1
  assert x - 4 == 1
  y = Bits( 4, 5 )
  assert x - y == 0
  assert x - 5 == 0
  y = Bits( 4, 7 )
  assert x - y == 0b1110
  assert x - 7 == 0b1110

def test_lshift():
  x = Bits( 8, 0b1100 )
  y = Bits( 8, 4 )
  assert x << y == 0b11000000
  assert x << 4 == 0b11000000
  assert x << 6 == 0b00000000
  assert y << x == 0b00000000
  assert y << 0 == 0b00000100
  assert y << 1 == 0b00001000

def test_rshift():
  x = Bits( 8, 0b11000000 )
  y = Bits( 8, 4 )
  assert x >> y  == 0b00001100
  assert x >> 7  == 0b00000001
  assert x >> 8  == 0b00000000
  assert x >> 10 == 0b00000000
  x = Bits( 8, 2 )
  assert y >> x == 0b00000001
  assert y >> 0 == 0b00000100
  assert y >> 2 == 0b00000001
  assert y >> 5 == 0b00000000

def test_and():
  x = Bits( 8, 0b11001100 )
  y = Bits( 8, 0b11110000 )
  assert x & y      == 0b11000000
  assert x & 0b1010 == 0b00001000
  #assert 0b1010 & x == 0b00001000

def test_or():
  x = Bits( 8, 0b11001100 )
  y = Bits( 8, 0b11110000 )
  assert x | y      == 0b11111100
  assert x | 0b1010 == 0b11001110
  #assert 0b1010 | x == 0b11001110

def test_xor():
  x = Bits( 8, 0b11001100 )
  y = Bits( 8, 0b11110000 )
  assert x ^ y      == 0b00111100
  assert x ^ 0b1010 == 0b11000110
  #assert 0b1010 ^ x == 0b11000110

def test_mult():
  x = Bits( 8, 0b00000000 )
  y = Bits( 8, 0b00000000 )
  assert x * y == 0b0000000000000000
  assert x * 0b1000 == 0b0000000000000000
  x = Bits( 8, 0b11111111 )
  y = Bits( 8, 0b11111111 )
  assert x * y == 0b0000000000000001111111000000001
  assert x * 0b11111111 == 0b0000000000000001111111000000001

  # TODO: Currently fails as the second operand is larger than the Bits
  # object x. Should update the test when we define the behaviour  
  #assert x * 0b1111111111 == 0b0000000000000001111111000000001

  y = Bits( 8, 0b10000000 )
  assert x * y == 0b0000000000000000111111110000000

#-------------------------------------------------------------------------
# Tests added by cbatten
#-------------------------------------------------------------------------

def test_num_bits():

  assert _num_bits(0) == 1
  assert _num_bits(1) == 1
  assert _num_bits(2) == 2
  assert _num_bits(3) == 2
  assert _num_bits(4) == 3
  assert _num_bits(5) == 3
  assert _num_bits(6) == 3
  assert _num_bits(7) == 3
  assert _num_bits(8) == 4

  assert _num_bits( 0x000f ) == 4
  assert _num_bits( 0x00ff ) == 8
  assert _num_bits( 0x0fff ) == 12
  assert _num_bits( 0xffff ) == 16

  assert _num_bits(-1) == 2
  assert _num_bits(-2) == 3
  assert _num_bits(-3) == 3
  assert _num_bits(-4) == 4
  assert _num_bits(-5) == 4
  assert _num_bits(-6) == 4
  assert _num_bits(-7) == 4
  assert _num_bits(-8) == 5

def test_constructor():

  assert Bits( 4,  2 ).uint() == 2
  assert Bits( 4,  4 ).uint() == 4
  assert Bits( 4, 15 ).uint() == 15

  assert Bits( 4, -2 ).uint() == 0b1110
  assert Bits( 4, -4 ).uint() == 0b1100

  assert Bits( 4, Bits(4, -2) ).uint() == 0b1110
  assert Bits( 4, Bits(4, -4) ).uint() == 0b1100

  # TODO: catch assert, initializing to None not allowed
  # assert Bits( 4, None ) != Bits( 4, 0 )
  assert Bits( 4 ) == Bits( 4, 0 )
  assert Bits( 4 ).uint() == 0
  # TODO: move to test_construct_from_bits
  a = Bits( 32, 5 )
  assert Bits( 32, ~a + 1 ).uint() == 0xFFFFFFFB

@pytest.mark.xfail
def test_construct_from_bits():

  a = Bits( 8, 5 )
  assert Bits( 16, ~a + 1 ).uint() == 0xFFFB
  #assert Bits( 16, ~a + 1 ).uint() == 0x00FB
  b = Bits( 32, 0 )
  assert Bits( 32, ~b + 1 ) + 1  == 1

def test_int():

  assert Bits( 4,  2 ).uint() == 2
  assert Bits( 4,  4 ).uint() == 4
  assert Bits( 4, 15 ).uint() == 15

  assert Bits( 4, -2 ).int() == -2
  assert Bits( 4, -4 ).int() == -4

def test_zext():

  assert Bits( 4,  2 ).zext( 8 ) == Bits( 8, 0x02 )
  assert Bits( 4,  4 ).zext( 8 ) == Bits( 8, 0x04 )
  assert Bits( 4, 15 ).zext( 8 ) == Bits( 8, 0x0f )

  assert Bits( 4, -2  ).zext( 8 ) == Bits( 8, 0x0e )
  assert Bits( 4, -4  ).zext( 8 ) == Bits( 8, 0x0c )

def test_sext():

  assert Bits( 4,  2 ).sext(8) == Bits( 8, 0x02 )
  assert Bits( 4,  4 ).sext(8) == Bits( 8, 0x04 )
  assert Bits( 4, 15 ).sext(8) == Bits( 8, 0xff )

  assert Bits( 4, -2  ).sext(8) == Bits( 8, 0xfe )
  assert Bits( 4, -4  ).sext(8) == Bits( 8, 0xfc )

def test_str():

  assert Bits(  4,        0x2 ).__str__() == "2"
  assert Bits(  8,       0x1f ).__str__() == "1f"
  assert Bits( 32, 0x0000beef ).__str__() == "0000beef"

def test_concat():

  assert concat([ Bits(4,0xf), Bits(4,0x2) ]) == Bits( 8, 0xf2 )
  assert concat([ Bits(2,0x2), Bits(4,0xf) ]) == Bits( 6, 0x2f )

  assert concat([ Bits(2,0x2), Bits(4,0), Bits(4,0xf) ]) == Bits( 10, 0x20f )
  assert concat([ Bits(4,0x2), Bits(4,0), Bits(4,0xf) ]) == Bits( 12, 0x20f )

