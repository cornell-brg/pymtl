#=========================================================================
# AutoQueues_test.py
#=========================================================================
# Unit tests for the ValRdy PortBundle.

from new_pymtl  import *
from new_pmlib  import TestSource, TestSink
from new_pmlib  import InValRdyBundle, OutValRdyBundle
from AutoQueues import InAutoQueue, OutAutoQueue

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs,  sink_msgs,
                   maxlen,    src_delay, sink_delay ):

    s.src  = TestSource ( 8, src_msgs,  src_delay  )
    s.q    = ModelType  ( 8, maxlen )
    s.sink = TestSink   ( 8, sink_msgs, sink_delay )

  def elaborate_logic( s ):

    s.connect( s.src.out, s.q.in_    )
    s.connect( s.q.out,   s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.q.line_trace()    + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# TestInAutoQueue
#-------------------------------------------------------------------------
class TestInAutoQueue( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, nbits, qlen ):

    s.in_   = InValRdyBundle ( nbits )
    s.out   = OutValRdyBundle( nbits )

    s.nbits = nbits
    s.qlen  = qlen

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.q = InAutoQueue( s.nbits, s.qlen )

    s.connect( s.in_, s.q.in_ )

    @s.tick
    def logic():

      if s.out.val & s.out.rdy:
        s.q.deq()

      if not s.q.is_empty():
        s.out.msg.next = s.q.peek()
        s.out.val.next = True
      else:
        s.out.val.next = False

      s.q.set_ports()

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def line_trace( s ):
    return s.q.line_trace()


#-------------------------------------------------------------------------
# Test Runner
#-------------------------------------------------------------------------
def run_in_test( dump_vcd, vcd_file_name, ModelType, maxlen,
                 src_delay, sink_delay ):

  src_msgs = sink_msgs = range( 10 )

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs,  sink_msgs,
                       maxlen,    src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  assert model.done()

#-------------------------------------------------------------------------
# in_test
#-------------------------------------------------------------------------

def test_in_1_0_0( dump_vcd ):
  run_in_test( dump_vcd, "0.vcd",
               TestInAutoQueue, 1, 0, 0 )

def test_in_1_2_5( dump_vcd ):
  run_in_test( dump_vcd, "1.vcd",
               TestInAutoQueue, 1, 2, 5 )

def test_in_3_2_5( dump_vcd ):
  run_in_test( dump_vcd, "2.vcd",
               TestInAutoQueue, 3, 2, 5 )


#-------------------------------------------------------------------------
# TestOutAutoQueue
#-------------------------------------------------------------------------
class TestOutAutoQueue( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, nbits, qlen ):

    s.in_   = InValRdyBundle ( nbits )
    s.out   = OutValRdyBundle( nbits )

    s.nbits = nbits
    s.qlen  = qlen

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.q = OutAutoQueue( s.nbits, s.qlen )

    s.connect( s.out, s.q.out )

    @s.tick
    def logic():

      if s.in_.val & s.in_.rdy:
        s.q.enq( s.in_.msg[:] )

      s.in_.rdy.next = not s.q.is_full()

      s.q.set_ports()

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def line_trace( s ):
    return s.q.line_trace()


#-------------------------------------------------------------------------
# in_test
#-------------------------------------------------------------------------

def test_out_1_0_0( dump_vcd ):
  run_in_test( dump_vcd, "3.vcd",
               TestOutAutoQueue, 1, 0, 0 )

def test_out_1_2_5( dump_vcd ):
  run_in_test( dump_vcd, "4.vcd",
               TestOutAutoQueue, 1, 2, 5 )

def test_out_3_2_5( dump_vcd ):
  run_in_test( dump_vcd, "5.vcd",
               TestOutAutoQueue, 3, 2, 5 )
