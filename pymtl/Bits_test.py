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
    x.value = wr
    assert x.value == rd

def test_many_overflow():
  for i in range(1,10):
    x = Bits(i)
    overflow_val = 2**i
    for j in range(50):
      x.value = j
      assert x.value ==  j % overflow_val

def test_get_bit():
  x = Bits(4)
  x.value = 0b1100
  assert x[3] == 1
  assert x[2] == 1
  assert x[1] == 0
  assert x[0] == 0
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1
  x.value = 22
  assert x[3] == 0
  assert x[2] == 1
  assert x[1] == 1
  assert x[0] == 0

def test_get_slice():
  x = Bits(4)
  x.value = 0b1100
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
  x.value = 0b1100
  x[3] = 0
  assert x.value == 0b0100
  x[2] = 1
  assert x.value == 0b0100
  x[1] = 1
  assert x.value == 0b0110
  # TODO: ensure check
  #x[0] = 2
  # TODO: support negative indexes, or catch?
  #assert x[-1] == 1
  # TODO: check that out of bounds is caught
  #assert x[8] == 1

def test_get_slice():
  x = Bits(4)
  x.value = 0b1100
  x[:] = 0b0010
  assert x.value == 0b0010
  x[2:4] = 0b11
  assert x.value == 0b1110
  x[0:1] = 0b1
  assert x.value == 0b1111
  x[1:3] = 0b10
  assert x.value == 0b1101
  # TODO: check out of bounds is caught
  #assert x[1:5] == 0b10
  # check open ended ranges
  x[1:] = 0b001
  assert x.value == 0b0011
  x[:3] = 0b110
  assert x.value == 0b0110

def test_negative_assign():
  x = Bits(4)
  x.value = -1
  assert x.value == 0b1111
  x.value = -2
  assert x.value == 0b1110
  x.value = -15
  assert x.value == 0b0001
  x.value = -16
  assert x.value == 0b0000
  x.value = -17
  assert x.value == 0b1111

#def test_equality():
#  x = Bits(4)
#  x.value = 0b1010
#  # Check the value
#  assert x.value == 0b1010
#  assert x.value == 0xA
#  assert x.value == 10
#  # Checking the equality operator
#  assert x == 0b1010
#  assert x == 0xA
#  assert x == 10
#  # Checking comparison with another bit container
#  y = Bits(4)
#  y.value = 0b1010
#  assert x.value == y.value
#  # TODO: how should equality between Bits objects work?
#  #       Same object? Same value? Same value and width?
#  # assert x == y
#  y = Bits(8)
#  y.value = 0b1010
#  assert x.value == y.value
#  #assert x == y
#  # Check the negatives
#  x.value = -1
#  assert x.value == 0b1111
#  assert x.value == 0xF
#  assert x.value == 15
#  # TODO: check -1?
#  # assert x.value == -1
#  # Checking the equality operator
#  assert x == 0b1111
#  assert x == 0xF
#  assert x == 15
#  #assert x == -1
#  assert x.value == Bits(4, -1).value
#  assert x == Bits(4, -1).value
#  # TODO: see above comment on Bits object equality
#  #assert x == Bits(4, -1)

#def test_complement():
#  # TODO: return Bits or Int when complement?
#  x = Bits(4)
#  x.value = 0b0001
#  assert ~x == 0b1110
#  x.value = 0b1001
#  assert ~x == 0b0110
#  x = Bits(16)
#  x.value = 0b1111000011110000
#  assert ~x == 0b0000111100001111
