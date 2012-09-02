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

def test_slice_repitition():
  a = Node(2, 'a')
  b = Node(8, 'b')
  connect( a, b[0:2] )
  connect( a, b[2:4] )
  connect( a, b[4:6] )
  connect( a, b[6:8] )
  a.value = 0b01
  assert b.value == 0b01010101
  a.value = 0b10
  assert b.value == 0b10101010
  # TODO: this demonstrates a writer problem... catch this somehow
  #b.value = 0b11000000
  #assert a.value == 0b00
  #assert a.value == 0b11
  b.value = 0b11111111
  assert a.value == 0b11

def test_2node_slice_repition():
  a = Node(2, 'a')
  b = Node(6, 'b')
  c = Node(2, 'c')
  connect( a, b[0:2] )
  connect( a, b[2:4] )
  connect( c, b[4:6] )
  a.value = 0b11
  assert b.value == 0b001111
  assert c.value == 0b00
  assert a.value == 0b11
  c.value = 0b10
  assert b.value == 0b101111
  assert a.value == 0b11
  assert c.value == 0b10
  b.value = 0b011010
  assert a.value == 0b10
  assert c.value == 0b01
  assert b.value == 0b011010
  # TODO: impossible b value... catch this somehow
  #b.value = 0b010011
  #assert a.value == 0b00 | 0b11
  #assert c.value == 0b01
  #assert b.value == 0b010011

def test_slice_rotate():
  a = Node(4, 'a')
  b = Node(4, 'b')
  connect( a[0:2], b[2:4] )
  connect( a[2:4], b[0:2] )
  a.value = 0b1100
  assert b.value == 0b0011
  assert a.value == 0b1100
  b.value = 0b0110
  assert a.value == 0b1001
  assert b.value == 0b0110

def test_sign_ext():
  a = Node(4, 'a')
  b = Node(8, 'b')
  connect( a, b[0:4] )
  for i in range(4,8):
    connect( a[3], b[i] )
  a.value = 0b0011
  assert b.value == 0b00000011
  assert a.value == 0b0011
  a.value = 0b1100
  assert b.value == 0b11111100
  assert a.value == 0b1100
  a.value = 0b1010
  assert b.value == 0b11111010
  assert a.value == 0b1010

def test_slice_cascading():
  a = Node(4, 'a')
  b = Node(2, 'b')
  c = Node(1, 'c')
  connect(b, a[0:2])
  connect(c, b[0])
  a.value = 0b1101
  assert b.value == 0b01
  assert c.value == 0b1
  assert a.value == 0b1101
  c.value = 0b0
  assert b.value == 0b00
  assert c.value == 0b0
  assert a.value == 0b1100
  b.value = 0b11
  assert a.value == 0b1111
  assert c.value == 0b1
  assert b.value == 0b11

def test_slice_fanout():
  a  = Node(4)
  b0 = Node(2)
  b1 = Node(2)
  c0 = Node(1)
  c1 = Node(1)
  c2 = Node(1)
  c3 = Node(1)
  connect(b0, a[0:2])
  connect(b1, a[2:4])
  connect(c0, b0[0])
  connect(c1, b0[1])
  connect(c2, b1[0])
  connect(c3, b1[1])
  a.value = 0b1101
  assert b0.value == 0b01
  assert b1.value == 0b11
  assert c0.value == 0b1
  assert c1.value == 0b0
  assert c2.value == 0b1
  assert c3.value == 0b1
  c2.value = 0b0
  assert a.value  == 0b1001
  assert b0.value == 0b01
  assert b1.value == 0b10
