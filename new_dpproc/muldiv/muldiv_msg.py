#=========================================================================
# object to index bitfields in a Bits object
#=========================================================================

from new_pymtl import *
import new_pmlib


class BitStructIndex:
  DIV_OP    = 0
  REM_OP    = 1
  MUL_OP    = 2
  DIVU_OP   = 3
  REMU_OP   = 4
  length    = 67
  arg_B     = slice(0, 32)
  arg_A     = slice(32, 64)
  muldiv_op = slice(64, 67)

  # Helper function to create 32b Bits objects
def B( num ):
  return Bits( 32, num )

  # Helper function to create 1b Bits objects
def Op( num ):
  return Bits( 3, num )

def createMulDivMessage(op, a, b):
  return concat( Op(op), B(a), B(b) )
