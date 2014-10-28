#=========================================================================
# Bytes_test.py
#=========================================================================

from pymtl import Bits
from Bytes import Bytes

import pytest

#-------------------------------------------------------------------------
# test_writing_bytearray
#-------------------------------------------------------------------------

def test_writing_bytearray():

  mem = Bytes(8)

  # Write first four bytes

  mem[0:4] = bytearray("\x01\x02\x03\x04")
  assert mem.mem == bytearray("\x01\x02\x03\x04\x00\x00\x00\x00")

  # Write second four bytes

  mem[4:8] = bytearray("\x01\x02\x03\x04")
  assert mem.mem == bytearray("\x01\x02\x03\x04\x01\x02\x03\x04")

  # Write middle four bytes

  mem[2:6] = bytearray("\xde\xad\xbe\xef")
  assert mem.mem == bytearray("\x01\x02\xde\xad\xbe\xef\x03\x04")

  # Write two bytes

  mem[2:4] = bytearray("\xab\xcd")
  assert mem.mem == bytearray("\x01\x02\xab\xcd\xbe\xef\x03\x04")

  # Write one byte

  mem[3] = bytearray("\x69")
  assert mem.mem == bytearray("\x01\x02\xab\x69\xbe\xef\x03\x04")

  # Write entire memory

  mem[0:8] = bytearray("\xde\xad\xbe\xef\xca\xfe\xca\xfe")
  assert mem.mem == bytearray("\xde\xad\xbe\xef\xca\xfe\xca\xfe")

#-------------------------------------------------------------------------
# test_writing_bits
#-------------------------------------------------------------------------

def test_writing_bits():

  mem = Bytes(8)

  # Write first four bytes

  mem[0:4] = Bits( 32, 0x04030201 )
  assert mem.mem == bytearray("\x01\x02\x03\x04\x00\x00\x00\x00")

  # Write second four bytes

  mem[4:8] = Bits( 32, 0x04030201 )
  assert mem.mem == bytearray("\x01\x02\x03\x04\x01\x02\x03\x04")

  # Write middle four bytes

  mem[2:6] = Bits( 32, 0xefbeadde )
  assert mem.mem == bytearray("\x01\x02\xde\xad\xbe\xef\x03\x04")

  # Write two bytes

  mem[2:4] = Bits( 16, 0xcdab )
  assert mem.mem == bytearray("\x01\x02\xab\xcd\xbe\xef\x03\x04")

  # Write one byte

  mem[3] = Bits( 8, 0x69 )
  assert mem.mem == bytearray("\x01\x02\xab\x69\xbe\xef\x03\x04")

  # Write entire memory

  mem[0:8] = Bits( 64, 0xfecafecaefbeadde )
  assert mem.mem == bytearray("\xde\xad\xbe\xef\xca\xfe\xca\xfe")

#-------------------------------------------------------------------------
# test_reading_bits
#-------------------------------------------------------------------------

def test_reading_bits():

  mem = Bytes(8)

  # Write first four bytes

  mem[0:4] = Bits( 32, 0x01020304 )
  assert mem[0:4] == Bits( 32, 0x01020304 )
  assert mem[0:8] == Bits( 64, 0x0000000001020304 )

  # Write second four bytes

  mem[4:8] = Bits( 32, 0x01020304 )
  assert mem[4:8] == Bits( 32, 0x01020304 )
  assert mem[0:8] == Bits( 64, 0x0102030401020304 )

  # Write middle four bytes

  mem[2:6] = Bits( 32, 0xdeadbeef )
  assert mem[2:6] == Bits( 32, 0xdeadbeef )
  assert mem[0:8] == Bits( 64, 0x0102deadbeef0304 )

  # Write two bytes

  mem[2:4] = Bits( 16, 0xabcd )
  assert mem[2:4] == Bits( 16, 0xabcd )
  assert mem[0:8] == Bits( 64, 0x0102deadabcd0304 )

  # Write one byte

  mem[3] = Bits( 8, 0x69 )
  assert mem[3]   == Bits( 8, 0x69 )
  assert mem[0:8] == Bits( 64, 0x0102dead69cd0304 )

  # Write entire memory

  mem[0:8] = Bits( 64, 0xdeadbeefcafecade )
  assert mem[0:8] == Bits( 64, 0xdeadbeefcafecade )

