#=========================================================================
# OutValRdyInelasticPipeAdapter_test.py
#=========================================================================

import pytest
import random

from copy       import deepcopy
from fractions  import gcd

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from adapters                      import InValRdyQueueAdapter
from OutValRdyInelasticPipeAdapter import OutValRdyInelasticPipeAdapter

from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

#-------------------------------------------------------------------------
# TestModelCL
#-------------------------------------------------------------------------

class TestModelCL (Model):

  def __init__( s, nstages ):

    s.in_   = InValRdyBundle  (16)
    s.out   = OutValRdyBundle (16)

    s.in_q  = InValRdyQueueAdapter( s.in_ )
    s.out_q = OutValRdyInelasticPipeAdapter( s.out, nstages )

    @s.tick_cl
    def block():
      s.in_q.xtick()
      s.out_q.xtick()
      if not s.in_q.empty() and not s.out_q.full():
        s.out_q.enq( s.in_q.deq() )

  def line_trace( s ):
    return "{}({}){}".format( s.in_, s.out_q, s.out )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, msgs, nstages, src_delay, sink_delay ):

    # Instantiate models

    s.src   = TestSource  ( 16, msgs,  src_delay  )
    s.model = TestModelCL ( nstages )
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
rgen.seed(0x658bb395)

basic_msgs  = [ 0, 1, 2, 3, 4 ]
random_msgs = [ rgen.randint(0,0xffff) for _ in range(20) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msgs         nstages src_delay sink_delay"),

  [ "basic_nstages0_0x0",  basic_msgs,  0,      0,        0          ],
  [ "random_nstages0_0x0", random_msgs, 0,      0,        0          ],
  [ "random_nstages0_9x0", random_msgs, 0,      9,        0          ],
  [ "random_nstages0_0x9", random_msgs, 0,      0,        9          ],
  [ "random_nstages0_9x9", random_msgs, 0,      9,        9          ],

  [ "basic_nstages1_0x0",  basic_msgs,  1,      0,        0          ],
  [ "random_nstages1_0x0", random_msgs, 1,      0,        0          ],
  [ "random_nstages1_9x0", random_msgs, 1,      9,        0          ],
  [ "random_nstages1_0x9", random_msgs, 1,      0,        9          ],
  [ "random_nstages1_9x9", random_msgs, 1,      9,        9          ],

  [ "basic_nstages4_0x0",  basic_msgs,  4,      0,        0          ],
  [ "random_nstages4_0x0", random_msgs, 4,      0,        0          ],
  [ "random_nstages4_9x0", random_msgs, 4,      9,        0          ],
  [ "random_nstages4_0x9", random_msgs, 4,      0,        9          ],
  [ "random_nstages4_9x9", random_msgs, 4,      9,        9          ],

])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( test_params.msgs, test_params.nstages,
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

#-------------------------------------------------------------------------
# Test val-rdy protocol
#-------------------------------------------------------------------------
# This test checks if the OutValRdyInelasticPipeAdapter adheres to the
# val-rdy hadnshaking protocol. In general we never make val and rdy
# signals for a given port to depdend on each other. In situations when
# this is not possible, we can choose the rdy signal depend on the val
# signal but not the val signal to depend on the rdy signal. This test
# essentially checks if the val signal is ever dependent on the rdy signal
# and if so it should essentially reach the max timeout limit. If the model
# correctly adheres to the val-rdy handshaking protocol as described above
# the cylce count for the simulations would be lower than the max timeout
# limit.

class TestValRdyProtocolHarness( Model ):

  def __init__( s, msgs, nstages ):

    # Instantiate models
    s.src   = TestSource  ( 16, msgs, 0 )
    s.model = TestModelCL ( nstages )

    # Wire
    s.out_rdy = Wire( 1 )

    # Connect
    s.connect( s.src.out,       s.model.in_ )
    s.connect( s.model.out.val, s.out_rdy   )

    # NOTE: we are making the rdy signal depend on the val to test if the
    # val signal is dependent on the rdy signal in the model under test
    s.connect( s.model.out.rdy, s.out_rdy   )

  def line_trace( s ):
    return s.src.line_trace() + " > " + \
           s.model.line_trace()

@pytest.mark.parametrize(
  ('nstages'),[0]
)
def test_valrdy_protocol( dump_vcd, nstages ):

  # max_cycles
  max_cycles = 100

  # Setup the model
  dut = TestValRdyProtocolHarness( basic_msgs, nstages )
  dut.vcd_file = dump_vcd
  dut.elaborate()

  # Create a simulator
  sim = SimulationTool( dut )

  # Reset the model
  sim.reset()
  print()

  # Run Simulation
  while not dut.src.done() and sim.ncycles < max_cycles:
    sim.print_line_trace()
    sim.cycle()

  # Force a test failure if we timed out
  assert sim.ncycles < max_cycles

  # Extra ticks to make the VCD easier to read
  sim.cycle()
  sim.cycle()
  sim.cycle()
