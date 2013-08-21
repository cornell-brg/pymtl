#=========================================================================
# StrSearchFunc_test.py
#=========================================================================
#
# PyMTL Functional Model of strsearch.

from new_pymtl        import *
from StrSearchOO_test import strings, docs, reference

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

    sim.reset()

    for doc in docs:
      model.in_.v = doc
      sim.cycle()
      assert model.out == reference[ i ]
      i += 1

from StrSearchFunc import StrSearchMath, StrSearchAlg

#-------------------------------------------------------------------------
# test_strsearch_math
#-------------------------------------------------------------------------
def test_strsearch_math():
  run_test( StrSearchMath )

#-------------------------------------------------------------------------
# test_strsearch_alg
#-------------------------------------------------------------------------
def test_strsearch_alg():
  run_test( StrSearchAlg )
