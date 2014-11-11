#=========================================================================
# TestSrcSinkSim.py
#=========================================================================

from pymtl  import *
from TestSource import TestSource
from TestSink   import TestSink

#-------------------------------------------------------------------------
# TestSrcSinkSim
#-------------------------------------------------------------------------
# This class simplifies creating unit tests which use the ValRdy latency
# insensitive interface. A user provides the model under test, a list
# of source messages to be fed into the simulation, and a list of 
# exptected output messages. The simulator will handle driving the
# simulation to completion.
#
class TestSrcSinkSim( object ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( self, model_inst, src_msgs,  sink_msgs,
                                  src_delay, sink_delay ):

    self.model = TestSrcSinkHarness( model_inst, src_msgs,  sink_msgs,
                                                 src_delay, sink_delay )
    self.vcd_file_name = None
 
  #-----------------------------------------------------------------------
  # dump_vcd
  #-----------------------------------------------------------------------
  def dump_vcd( self, vcd_file_name ):

    self.vcd_file_name = vcd_file_name

  #-----------------------------------------------------------------------
  # run_test
  #-----------------------------------------------------------------------
  def run_test( self ):

    # Create a simulator using the simulation tool

    self.model.elaborate()
    sim = SimulationTool( self.model )

    # Dump vcd

    if self.vcd_file_name != None:
      sim.dump_vcd( self.vcd_file_name )

    # Run the simulation

    print ""

    sim.reset()
    while not self.model.done():
      sim.print_line_trace()
      sim.cycle()

    # Add a couple extra ticks so that the VCD dump is nicer

    sim.cycle()
    sim.cycle()
    sim.cycle()
    
#-------------------------------------------------------------------------
# TestSourceSinkHarness
#-------------------------------------------------------------------------
# TestHarness with a TestSource, TestSink, and the module under test.
#
class TestSrcSinkHarness( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, model_inst, src_msgs,  sink_msgs,
                               src_delay, sink_delay ):

    # Source and sink take on the same input and output type as the
    # model under test
    src_msg_type  = model_inst.in_.msg.msg_type
    sink_msg_type = model_inst.out.msg.msg_type

    # Instantiate src and sink
    # TODO: should model be a model instance, or a type + params?
    s.src   = TestSource( src_msg_type,  src_msgs,  src_delay  )
    s.model = model_inst
    s.sink  = TestSink  ( sink_msg_type, sink_msgs, sink_delay )

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  # TODO: get rid of elaborate_logic()?
  def elaborate_logic( s ):
    s.connect( s.src  .out, s.model.in_ )
    s.connect( s.model.out, s.sink .in_ )

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------
  def done( s ):
    return s.src.done and s.sink.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):
    return s.src.  line_trace() + " > " + \
           s.model.line_trace() + " > " + \
           s.sink. line_trace()


