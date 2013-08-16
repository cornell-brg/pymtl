#=========================================================================
# StrSearchFunc_test.py
#=========================================================================
#
# PyMTL Functional Model of strsearch.

from new_pymtl        import *
from StrSearchOO_test import strings, docs, reference

#-------------------------------------------------------------------------
# str_to_bits
#-------------------------------------------------------------------------
def str_to_bits( string, nchars ):
  bits = Bits( nchars*8 )
  for i, char in enumerate( bytearray( string ) ):
    bits[i*8:i*8+8] = char
  return bits

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------
def run_test( SearchModel ):

  i = 0
  for string in strings:

    # Instantiate the model, elaborate it, and create a simulator
    model = SearchModel( 64, string )
    model.elaborate()
    sim   = SimulationTool( model )

    for doc in docs:
      doc_bits = str_to_bits( doc, 64 )
      model.in_.v = doc_bits
      sim.cycle()
      assert model.out == reference[ i ]
      i += 1

from StrSearchFunc import StrSearchMath #, StrSearchAlg

#-------------------------------------------------------------------------
# test_strsearch_math
#-------------------------------------------------------------------------
def test_strsearch_math():
  run_test( StrSearchMath )

#-------------------------------------------------------------------------
# test_strsearch_alg
#-------------------------------------------------------------------------
#def test_strsearch_alg():
#  run_test( StrSearchAlg )
