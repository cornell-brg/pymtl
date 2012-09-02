from connect import *


def test_node_node():
  x = Node(8)
  y = Node(8)
  assert x.width == y.width
  assert x.value == 0
  assert y.value == 0
  connect(x, y)
  x.value = 5
  assert x.value == y.value
  y.value = -1
  assert x.value == y.value

def test_node_slice_node():
  x = Node(8)
  y = Node(2)
  assert x.width != y.width
  assert x[2:4].width == y.width
  connect( x[2:4], y )
  x.value = 0b1100
  assert y.value == 0b11
  y.value = 0b01
  assert x.value == 0b0100
  x.value = 0b11000100
  assert y.value == 0b01

def test_node_node_slice_node():
  w = Node(8)
  x = Node(8)
  y = Node(2)
  connect( w, x )
  connect( x[2:4], y )
  w.value = 0b1100
  assert x.value == 0b1100
  assert y.value == 0b11
  y.value = 0b01
  assert x.value == 0b0100
  assert w.value == 0b0100
  w.value = 0b11000100
  assert x.value == 0b11000100
  assert y.value == 0b01
  x.value = 0b10101010
  assert w.value == 0b10101010
  assert x.value == 0b10101010
  assert y.value == 0b10

def test_node_manyslices():
  a = Node(6)
  b = Node(2)
  c = Node(2)
  d = Node(4)
  connect( a[0:2], b)
  connect( a[2:4], c)
  connect( a[2:6], d)
  # TODO: prevent writes to overlapping ranges
  a.value = 0b110110
  assert b.value == 0b10
  assert c.value == 0b01
  assert d.value == 0b1101
  b.value = 0b11
  assert a.value == 0b110111
  assert c.value == 0b01
  assert d.value == 0b1101
  c.value = 0b10
  assert a.value == 0b111011
  assert b.value == 0b11
  assert d.value == 0b1110
  d.value = 0b1001
  assert a.value == 0b100111
  assert b.value == 0b11
  assert c.value == 0b01

def test_node_slice_slice_node():
  a = Node(6)
  b = Node(4)
  connect( a[0:3], b[1:4])
  a.value = 0b110110
  assert b.value == 0b1100
  a.value = 0b110001
  assert b.value == 0b0010
  a.value = 0b000001
  assert b.value == 0b0010
  b.value = 0b1111
  assert a.value == 0b000111
  b.value = 0b1110
  assert a.value == 0b000111
  b.value = 0b0110
  assert a.value == 0b000011

