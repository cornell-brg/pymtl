from Bits import *

def test_simple_overflow():
  width = 2
  x = Bits(width)
  tests = [
      (0, 0),
      (1, 1),
      (2, 2),
      (3, 3),
      (4, 0),
      (5, 1),
      (6, 2),
      (7, 3),
      ]

  assert x.width == width
  for wr, rd in tests:
    x.uint = wr
    assert x.uint == rd

def test_many_overflow():
  for i in range(1,10):
    x = Bits(i)
    overflow_val = 2**i
    for j in range(50):
      x.uint = j
      assert x.uint ==  j % overflow_val

def test_neg_assign():
  x = Bits(4)
  x.uint = -1
  assert x.uint == 0b1111
  x.uint = -2
  assert x.uint == 0b1110
  x.uint = -15
  assert x.uint == 0b0001
  x.uint = -16
  assert x.uint == 0b0000
  x.uint = -17
  assert x.uint == 0b1111

def test_get_bit():
  x = Bits(4)
  x.uint = 0b1100
  assert x[3] == 1
  assert x[2] == 1
  assert x[1] == 0
  assert x[0] == 0
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1
  x.uint = 22
  assert x[3] == 0
  assert x[2] == 1
  assert x[1] == 1
  assert x[0] == 0

def test_get_slice():
  x = Bits(4)
  x.uint = 0b1100
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
  x = Bits(4)
  x.uint = 0b1100
  x[3] = 0
  assert x.uint == 0b0100
  x[2] = 1
  assert x.uint == 0b0100
  x[1] = 1
  assert x.uint == 0b0110
  # TODO: ensure check
  #x[0] = 2
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1

def test_set_slice():
  x = Bits(4)
  x.uint = 0b1100
  x[:] = 0b0010
  assert x.uint == 0b0010
  x[2:4] = 0b11
  assert x.uint == 0b1110
  x[0:1] = 0b1
  assert x.uint == 0b1111
  x[1:3] = 0b10
  assert x.uint == 0b1101
  # TODO: check out of bounds is caught
  #assert x[1:5] == 0b10
  # check open ended ranges
  x[1:] = 0b001
  assert x.uint == 0b0011
  x[:3] = 0b110
  assert x.uint == 0b0110

def test_eq():
  x = Bits(4)
  x.uint = 0b1010
  assert x.uint == x.uint
  # TODO: compare objects by value or by id?
  assert x == x
  # Check the value
  assert x.uint == 0b1010
  assert x.uint == 0xA
  assert x.uint == 10
  # Checking the equality operator
  assert x == 0b1010
  assert x == 0xA
  assert x == 10
  # Checking comparison with another bit container
  y = Bits(4)
  y.uint = 0b1010
  assert x.uint == y.uint
  # TODO: how should equality between Bits objects work?
  #       Same object? Same value? Same value and width?
  # assert x == y
  y = Bits(8)
  y.uint = 0b1010
  assert x.uint == y.uint
  #assert x == y
  # Check the negatives
  x.uint = -1
  assert x.uint == 0b1111
  assert x.uint == 0xF
  assert x.uint == 15
  # TODO: check -1?
  # assert x.uint == -1
  # Checking the equality operator
  assert x == 0b1111
  assert x == 0xF
  assert x == 15
  #assert x == -1
  assert x.uint == Bits(4, -1).uint
  assert x == Bits(4, -1).uint
  # TODO: see above comment on Bits object equality
  #assert x == Bits(4, -1)

def test_ne():
  x = Bits(4)
  x.uint = 0b1100
  y = Bits(4)
  y.uint = 0b0011
  assert x.uint != y.uint
  assert x != y
  # TODO: check width?

def test_lt():
  x = Bits(4)
  y = Bits(4)
  x.uint = 0b1100
  y.uint = 0b0011
  assert y.uint < x.uint
  assert y.uint < 10
  assert y < x.uint
  assert y < 10
  assert y < x

def test_gt():
  x = Bits(4)
  y = Bits(4)
  x.uint = 0b1100
  y.uint = 0b0011
  assert x.uint > y.uint
  assert x.uint > 2
  assert x > y.uint
  assert x > 2
  assert x > y

def test_lte():
  x = Bits(4)
  y = Bits(4)
  z = Bits(4)
  x.uint = 0b1100
  y.uint = 0b0011
  z.uint = 0b0011
  assert y.uint <= x.uint
  assert y.uint <= 10
  assert y.uint <= z.uint
  assert y.uint <= 0b0011
  assert y <= x.uint
  assert y <= 10
  assert y <= z.uint
  assert y <= 0b0011
  assert y <= x
  assert y <= z
  assert z <= x
  assert z <= z

def test_gte():
  x = Bits(4)
  y = Bits(4)
  z = Bits(4)
  x.uint = 0b1100
  y.uint = 0b0011
  z.uint = 0b1100
  assert x.uint >= y.uint
  assert x.uint >= 2
  assert x.uint >= z.uint
  assert x.uint >= 0b1100
  assert x >= y.uint
  assert x >= 2
  assert x >= z.uint
  assert x >= 0b1100
  assert x >= y
  assert x >= z
  assert z >= y
  assert z >= x
  assert x >= x

def test_invert():
  x = Bits(4)
  x.uint = 0b0001
  assert ~x == 0b1110
  x.uint = 0b1001
  assert ~x == 0b0110
  x = Bits(16)
  x.uint = 0b1111000011110000
  assert ~x == 0b0000111100001111

def test_add():
  x = Bits(4)
  y = Bits(4)
  x.uint = 4
  y.uint = 4
  assert x + y == 8
  assert x + Bits(4, 4) == 8
  assert x + 4 == 8
  y.uint = 14
  assert x + y == 2
  assert x + 14 == 2

def test_sub():
  x = Bits(4)
  y = Bits(4)
  x.uint = 5
  y.uint = 4
  assert x - y == 1
  assert x - Bits(4, 4) == 1
  assert x - 4 == 1
  y.uint = 5
  assert x - y == 0
  assert x - 5 == 0
  y.uint = 7
  assert x - y == 0b1110
  assert x - 7 == 0b1110

def test_lshift():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b1100
  y.uint = 4
  assert x << y == 0b11000000
  assert x << 4 == 0b11000000
  assert x << 6 == 0b00000000
  assert y << x == 0b00000000
  assert y << 0 == 0b00000100
  assert y << 1 == 0b00001000

def test_rshift():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b11000000
  y.uint = 4
  assert x >> y  == 0b00001100
  assert x >> 7  == 0b00000001
  assert x >> 8  == 0b00000000
  assert x >> 10 == 0b00000000
  x.uint = 2
  assert y >> x == 0b00000001
  assert y >> 0 == 0b00000100
  assert y >> 2 == 0b00000001
  assert y >> 5 == 0b00000000

def test_and():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b11001100
  y.uint = 0b11110000
  assert x & y      == 0b11000000
  assert x & 0b1010 == 0b00001000
  #assert 0b1010 & x == 0b00001000

def test_or():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b11001100
  y.uint = 0b11110000
  assert x | y      == 0b11111100
  assert x | 0b1010 == 0b11001110
  #assert 0b1010 | x == 0b11001110

def test_xor():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b11001100
  y.uint = 0b11110000
  assert x ^ y      == 0b00111100
  assert x ^ 0b1010 == 0b11000110
  #assert 0b1010 ^ x == 0b11000110

def test_mult():
  x = Bits(8)
  y = Bits(8)
  x.uint = 0b00000000
  x.uint = 0b00000000
  assert x * y == 0b0000000000000000
  assert x * 0b1000 == 0b0000000000000000
  x.uint = 0b11111111
  y.uint = 0b11111111
  assert x * y == 0b0000000000000001111111000000001
  assert x * 0b11111111 == 0b0000000000000001111111000000001

  # TODO: Currently fails as the second operand is larger than the Bits
  # object x. Should update the test when we define the behaviour  
  #assert x * 0b1111111111 == 0b0000000000000001111111000000001

  y.uint = 0b10000000
  assert x * y == 0b0000000000000000111111110000000
