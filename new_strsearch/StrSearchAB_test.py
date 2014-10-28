#=========================================================================
# StrSearchFunc_test.py
#=========================================================================
#
# PyMTL Functional Model of strsearch.

from pymtl        import *
from new_pmlib        import TestSource, TestSink
from StrSearchOO_test import strings, docs, reference
from StrSearchAB      import StrSignalValue, StrSearchMath, StrSearchAlg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, ModelType, string,
                src_msgs, sink_msgs, src_delay, sink_delay ):

    # Instantiate models

    s.src  = TestSource ( StrSignalValue, src_msgs, src_delay )
    s.sort = ModelType  ( string )
    s.sink = TestSink   (  1, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src.out,  s.sort.in_ )
    s.connect( s.sort.out, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src. line_trace() + " > " + \
           s.sort.line_trace() + " > " + \
           s.sink.line_trace()


#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------
def run_test( ModelType, str_id, src_delay, sink_delay ):

  # Test messages

  ndocs     = len( docs )
  src_msgs  = docs
  sink_msgs = reference[str_id*ndocs:str_id*ndocs+ndocs]
  string    = strings[ str_id ]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, string, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()


import pytest

#-------------------------------------------------------------------------
# test_strsearch_math
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
    ('src_delay', 'sink_delay'),
    [(0,0), (3,0), (0,3), (3,5)]
)
def test_strsearch_math( src_delay, sink_delay ):
  for i, string in enumerate( strings ):
    run_test( StrSearchMath, i, src_delay, sink_delay )

#-------------------------------------------------------------------------
# test_strsearch_alg
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
    ('src_delay', 'sink_delay'),
    [(0,0), (3,0), (0,3), (3,5)]
)
def test_strsearch_alg( src_delay, sink_delay ):
  for i, string in enumerate( strings ):
    run_test( StrSearchAlg, i, src_delay, sink_delay )
