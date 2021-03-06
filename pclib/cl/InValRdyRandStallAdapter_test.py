#=========================================================================
# InValRdyRandStallAdapter_test.py
#=========================================================================

import pytest
import random

from copy       import deepcopy
from fractions  import gcd

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from adapters                 import OutValRdyQueueAdapter
from InValRdyRandStallAdapter import InValRdyRandStallAdapter

from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

#-------------------------------------------------------------------------
# TestModelCL
#-------------------------------------------------------------------------

class TestModelCL (Model):

  def __init__( s, stall_prob ):

    s.in_   = InValRdyBundle  (16)
    s.out   = OutValRdyBundle (16)

    s.in_q  = InValRdyRandStallAdapter( s.in_, stall_prob )
    s.out_q = OutValRdyQueueAdapter( s.out )

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

  def __init__( s, msgs, stall_prob, src_delay, sink_delay ):

    # Instantiate models

    s.src   = TestSource  ( 16, msgs,  src_delay  )
    s.model = TestModelCL ( stall_prob )
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

random.seed(0xdeadbeef)

basic_msgs  = [ 0, 1, 2, 3, 4 ]
random_msgs = [ random.randint(0,0xffff) for _ in range(20) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msgs         stall_prob src_delay sink_delay"),
  [ "basic_stall0.0_0x0",  basic_msgs,  0,         0,        0          ],
  [ "random_stall0.0_0x0", random_msgs, 0,         0,        0          ],
  [ "random_stall0.0_9x0", random_msgs, 0,         9,        0          ],
  [ "random_stall0.0_0x9", random_msgs, 0,         0,        9          ],
  [ "random_stall0.0_9x9", random_msgs, 0,         9,        9          ],
  [ "random_stall0.5_0x0", random_msgs, 0.5,       0,        0          ],
  [ "random_stall0.5_9x0", random_msgs, 0.5,       9,        0          ],
  [ "random_stall0.5_0x9", random_msgs, 0.5,       0,        9          ],
  [ "random_stall0.5_9x9", random_msgs, 0.5,       9,        9          ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( test_params.msgs, test_params.stall_prob,
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

