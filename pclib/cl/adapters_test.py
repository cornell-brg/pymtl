#=========================================================================
# adapters_test
#=========================================================================

import pytest
import random

from copy       import deepcopy
from fractions  import gcd

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.cl   import InValRdyQueueAdapter, OutValRdyQueueAdapter

from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

#-------------------------------------------------------------------------
# TestModelCL
#-------------------------------------------------------------------------

class TestModelCL (Model):

  def __init__( s ):

    s.in_   = InValRdyBundle  (16)
    s.out   = OutValRdyBundle (16)

    s.in_q  = InValRdyQueueAdapter  ( s.in_ )
    s.out_q = OutValRdyQueueAdapter ( s.out )

    @s.tick_cl
    def block():
      s.in_q.xtick()
      s.out_q.xtick()
      if not s.in_q.empty() and not s.out_q.full():
        s.out_q.enq( s.in_q.deq() )

  def line_trace( s ):
    return "{}(){}".format( s.in_, s.out )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, msgs, src_delay, sink_delay ):

    # Instantiate models

    s.src   = TestSource  ( 16, msgs,  src_delay  )
    s.model = TestModelCL ()
    s.sink  = TestSink    ( 16, msgs, sink_delay )

    # Connect

    s.connect( s.src.out,   s.model.in_ )
    s.connect( s.model.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " > " + \
           s.model.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# Test src/sink messages
#-------------------------------------------------------------------------

rgen = random.Random()
rgen.seed(0x21a0728b)

basic_msgs  = [ 0, 1, 2, 3, 4 ]
random_msgs = [ rgen.randint(0,0xffff) for _ in xrange(20) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (              "msgs         src_delay sink_delay"),
  [ "basic_0x0",  basic_msgs,  0,        0          ],
  [ "random_0x0", random_msgs, 0,        0          ],
  [ "random_9x0", random_msgs, 9,        0          ],
  [ "random_0x9", random_msgs, 0,        9          ],
  [ "random_9x9", random_msgs, 9,        9          ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( test_params.msgs,
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

