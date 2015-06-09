#=========================================================================
# pipelines_test.py
#=========================================================================

import pytest

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test import TestSrcSinkSim
from pclib.cl   import InValRdyQueue, OutValRdyQueue
from pipelines  import Pipeline

#-------------------------------------------------------------------------
# test_Pipeline
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
  ('stages'), [1, 3, 12]
)
def test_Pipeline( dump_vcd, stages ):

  # Create the pipeline
  pipeline = Pipeline( stages )
  pipeline.vcd_file = dump_vcd

  # Fill up the pipeline
  i = -1
  for i in range( stages-1 ):
    pipeline.advance()
    pipeline.insert( i )
    assert not pipeline.ready()

  # Insert one last item
  pipeline.advance()
  pipeline.insert( i+1 )

  # Make sure there is something at the tail of the pipeline
  assert pipeline.ready()

  # Start removing items from the pipeline
  for i in range( stages ):
    assert pipeline.ready()
    assert pipeline.remove() == i
    pipeline.advance()

  assert not pipeline.ready()

#-------------------------------------------------------------------------
# TestValRdyPipeline
#-------------------------------------------------------------------------
class ValRdyPipelineHarness( Model ):
  def __init__( s, dtype, stages, pipeq, bypassq ):

    s.in_  = InValRdyBundle ( dtype )
    s.out  = OutValRdyBundle( dtype )

    s.in_q  = InValRdyQueue ( dtype, pipe  =pipeq   )
    s.out_q = OutValRdyQueue( dtype, bypass=bypassq )

    s.pipe  = Pipeline( stages )
    s.connect( s.in_, s.in_q. in_ )
    s.connect( s.out, s.out_q.out )

    @s.tick
    def logic():

      # Automatically enq from input / deq from output
      s.in_q.xtick()
      s.out_q.xtick()

      # No stall
      if not s.out_q.is_full():

        # Insert item into pipeline from input queue
        if not s.in_q.is_empty():
          s.pipe.insert( s.in_q.deq() )

        # Items graduating from pipeline, add to output queue
        if s.pipe.ready():
          s.out_q.enq( s.pipe.remove() )

        # Advance the pipeline
        s.pipe.advance()

#-------------------------------------------------------------------------
# test_ValRdyPipeline
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
    ('stages', 'pipeq', 'bypassq', 'src_delay', 'sink_delay'),
    [
      (1, 0, 0, 0, 0), (1, 0, 1, 0, 0), (1, 1, 0, 0, 0), (1, 1, 1, 0, 0),
      (1, 0, 0, 3, 0), (1, 0, 1, 3, 0), (1, 1, 0, 3, 0), (1, 1, 1, 3, 0),
      (1, 0, 0, 0, 3), (1, 0, 1, 0, 3), (1, 1, 0, 0, 3), (1, 1, 1, 0, 3),
      (1, 0, 0, 3, 5), (1, 0, 1, 3, 5), (1, 1, 0, 3, 5), (1, 1, 1, 3, 5),
      (5, 0, 0, 0, 0), (5, 0, 1, 0, 0), (5, 1, 0, 0, 0), (5, 1, 1, 0, 0),
      (5, 0, 0, 3, 0), (5, 0, 1, 3, 0), (5, 1, 0, 3, 0), (5, 1, 1, 3, 0),
      (5, 0, 0, 0, 3), (5, 0, 1, 0, 3), (5, 1, 0, 0, 3), (5, 1, 1, 0, 3),
      (5, 0, 0, 3, 5), (5, 0, 1, 3, 5), (5, 1, 0, 3, 5), (5, 1, 1, 3, 5),
    ]
)
def test_ValRdyPipeline( dump_vcd, stages, pipeq, bypassq, src_delay, sink_delay ):
  msgs  = range( 20 )
  model = ValRdyPipelineHarness( Bits( 8 ), stages, pipeq, bypassq )
  model.vcd_file = dump_vcd
  sim   = TestSrcSinkSim( model, msgs, msgs, src_delay, sink_delay )
  sim.run_test()

