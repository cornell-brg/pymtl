#=========================================================================
# StrSearchFunc_test.py
#=========================================================================
#
# PyMTL Functional Model of strsearch.

from new_pymtl        import *
from new_pmlib        import TestSource, TestSink
from StrSearchOO_test import strings, docs, reference
from StrSearchAB      import StrSignalValue, StrSearchMath, StrSearchAlg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, ModelType, string, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    print "TH"
    s.src  = TestSource ( StrSignalValue, src_msgs,  src_delay  )
    print "\TH"
    s.sort = ModelType  ( 64, string )
    s.sink = TestSink   ( 1, sink_msgs, sink_delay )

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


#-------------------------------------------------------------------------
# test_strsearch_math
#-------------------------------------------------------------------------
def test_strsearch_math():
  run_test( StrSearchMath, 0, 0, 0 )

#-------------------------------------------------------------------------
# test_strsearch_alg
#-------------------------------------------------------------------------
def test_strsearch_alg():
  run_test( StrSearchMath, 0, 0, 0 )
