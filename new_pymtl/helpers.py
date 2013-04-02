#=========================================================================
# helpers.py
#=========================================================================
# Collection of built-in helpers functions for the PyMTL framework.

import math

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
  assert N != 0
  return int( math.ceil( math.log( N ) ) )
