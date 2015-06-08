#=======================================================================
# helpers.py
#=======================================================================
'Collection of built-in helpers functions for the PyMTL framework.'

import math
import operator

# NOTE: circular imports between Bits and helpers, using 'import'
#       instead of 'from Bits import' ensures pydoc still works
import Bits

#-----------------------------------------------------------------------
# get_nbits
#-----------------------------------------------------------------------
def get_nbits( N ):
  'Return the number of bits needed to represent a value "N".'
  if N > 0:
    return N.bit_length()
  else:
    return N.bit_length() + 1

#-----------------------------------------------------------------------
# clog2
#-----------------------------------------------------------------------
def clog2( N ):
  'Return the number of bits needed to choose between "N" items.'
  assert N > 0
  return int( math.ceil( math.log( N, 2 ) ) )

#-----------------------------------------------------------------------
# zext
#-----------------------------------------------------------------------
def zext( value, new_width ):
  'Return a zero extended version of the provided SignalValue object.'
  return value._zext( new_width )

#-----------------------------------------------------------------------
# sext
#-----------------------------------------------------------------------
def sext( value, new_width ):
  'Return a sign extended version of the provided SignalValue object.'
  return value._sext( new_width )

#-----------------------------------------------------------------------
# concat
#-----------------------------------------------------------------------
def concat( *args ):
  'Return a Bits which is the concatenation of the Bits in bits_list.'

  assert isinstance( args[0], Bits.Bits )

  # Calculate total new bitwidth
  nbits = sum( [ x.nbits for x in args ] )

  # Create new Bits and add each bits from bits_list to it
  concat_bits = Bits.Bits( nbits )

  begin = 0
  for bits in reversed( args ):
    concat_bits[ begin : begin+bits.nbits ] = bits
    begin += bits.nbits

  return concat_bits

#-----------------------------------------------------------------------
# reduce_and
#-----------------------------------------------------------------------
def reduce_and( signal ):
  return reduce( operator.and_, (signal[x] for x in xrange( signal.nbits )) )

#-----------------------------------------------------------------------
# reduce_or
#-----------------------------------------------------------------------
def reduce_or( signal ):
  return reduce( operator.or_,  (signal[x] for x in xrange( signal.nbits )) )

#-----------------------------------------------------------------------
# reduce_xor
#-----------------------------------------------------------------------
# Verilog iterates through MSB to LSB, so we must reverse iteration.
def reduce_xor( signal ):
  return reduce( operator.xor,
                 (signal[x] for x in reversed( xrange( signal.nbits ) ))
               )
