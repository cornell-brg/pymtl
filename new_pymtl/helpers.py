#=========================================================================
# helpers.py
#=========================================================================
# Collection of built-in helpers functions for the PyMTL framework.

import math

# NOTE: circular imports between Bits and helpers, using 'import'
#       instead of 'from Bits import' ensures pydoc still works
import Bits

#-------------------------------------------------------------------------
# get_nbits
#-------------------------------------------------------------------------
# Return the number of bits needed to represent a value 'N'.
def get_nbits( N ):
  if N > 0:
    return N.bit_length()
  else:
    return N.bit_length() + 1

#-------------------------------------------------------------------------
# get_sel_nbits
#-------------------------------------------------------------------------
# Return the number of bits needed to represent a control signal which can
# select between 'N' items.
def get_sel_nbits( N ):
  assert N > 0
  return int( math.ceil( math.log( N, 2 ) ) )

#-------------------------------------------------------------------------
# zext
#-------------------------------------------------------------------------
# Return a zero extended version of the provided SignalValue object.
def zext( value, new_width ):
  return value._zext( new_width )

#-------------------------------------------------------------------------
# sext
#-------------------------------------------------------------------------
# Return a sign extended version of the provided SignalValue object.
def sext( value, new_width ):
  return value._sext( new_width )

#-------------------------------------------------------------------------
# concat
#-------------------------------------------------------------------------
# Return a Bits which is the concatenation of the Bits in bits_list.
def concat( bits_list ):

  # Calculate total new bitwidth
  nbits = sum( [ x.nbits for x in bits_list ] )

  # Create new Bits and add each bits from bits_list to it
  concat_bits = Bits.Bits( nbits )

  begin = 0
  for bits in reversed( bits_list ):
    concat_bits[ begin : begin+bits.nbits ] = bits
    begin += bits.nbits

  return concat_bits
