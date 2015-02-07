#=========================================================================
# MeshNetworkBL_test
#=========================================================================

from __future__ import print_function

import pytest
import random

from pymtl      import *
from pclib.test import TestSource, TestNetSink
from pclib.ifcs import NetMsg

from traffic_generators import *
from MeshNetworkBL      import MeshNetworkBL

#-------------------------------------------------------------------------
# network args
#-------------------------------------------------------------------------

import traffic_generators

nrouters      = traffic_generators.nrouters      =  16
nmessages     = traffic_generators.nmessages     = 128
payload_nbits = traffic_generators.payload_nbits =  32

nentries = 4

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, ModelType, src_msgs, sink_msgs, src_delay, sink_delay,
                nrouters, nmessages, payload_nbits, nentries, test_verilog ):

    s.src_msgs      = src_msgs
    s.sink_msgs     = sink_msgs
    s.src_delay     = src_delay
    s.sink_delay    = sink_delay
    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits
    s.nentries      = nentries
    s.ModelType     = ModelType
    s.test_verilog  = test_verilog

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    # instantiate models

    msg_type = NetMsg( s.nrouters, s.nmessages, s.payload_nbits )

    s.src  = [ TestSource ( msg_type, s.src_msgs[x],  s.src_delay  )
               for x in xrange( s.nrouters ) ]
    s.mesh = s.ModelType( s.nrouters, s.nmessages,
                          s.payload_nbits, s.nentries )
    s.sink = [ TestNetSink( msg_type, s.sink_msgs[x], s.sink_delay )
               for x in xrange( s.nrouters ) ]

    # enable verilog testing (only for RTL models)

    if s.test_verilog:
      s.mesh.vcd_file = s.vcd_file
      s.mesh = TranslationTool( s.mesh )

    # connect signals

    for i in xrange( s.nrouters ):
      s.connect( s.mesh.in_[i], s.src[i] .out )
      s.connect( s.mesh.out[i], s.sink[i].in_ )

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------
  def done( s ):
    done_flag = 1
    for i in xrange( s.nrouters ):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):
    return s.mesh.line_trace()

#-------------------------------------------------------------------------
# run_net_test
#-------------------------------------------------------------------------
# RunTest Utility Function
def run_net_test( dump_vcd, ModelType, src_delay, sink_delay, test_msgs,
                  nrouters, nmessages, payload_nbits, nentries,
                  test_verilog=False ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs, src_delay, sink_delay,
                       nrouters, nmessages, payload_nbits, nentries,
                       test_verilog )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check for success

  if not model.done():
    raise AssertionError( "Simulation did not complete!" )

#-------------------------------------------------------------------------
# test_mesh
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay,sink_delay,test_msgs', [
  # terminal tests
  (0, 0, terminal_msgs()),
  (5, 0, terminal_msgs()),
  (0, 5, terminal_msgs()),
  (8, 5, terminal_msgs()),
  # nearest neighbor east tests
  (0, 0, nearest_neighbor_east_msgs(8)),
  (5, 0, nearest_neighbor_east_msgs(8)),
  (0, 5, nearest_neighbor_east_msgs(8)),
  (8, 5, nearest_neighbor_east_msgs(8)),
  # nearest neighbor east tests
  (0, 0, nearest_neighbor_west_msgs(8)),
  (5, 0, nearest_neighbor_west_msgs(8)),
  (0, 5, nearest_neighbor_west_msgs(8)),
  (8, 5, nearest_neighbor_west_msgs(8)),
  # hotspot tests
  (0, 0, hotspot_msgs(8)),
  (5, 0, hotspot_msgs(8)),
  (0, 5, hotspot_msgs(8)),
  (8, 5, hotspot_msgs(8)),
  # partition tests
  (0, 0, partition_msgs(8)),
  (5, 0, partition_msgs(8)),
  (0, 5, partition_msgs(8)),
  (8, 5, partition_msgs(8)),
  # uniform random tests
  (0, 0, uniform_random_msgs(8)),
  (5, 0, uniform_random_msgs(8)),
  (0, 5, uniform_random_msgs(8)),
  (8, 5, uniform_random_msgs(8)),
  # tornado tests
  (0, 0, tornado_msgs(8)),
  (5, 0, tornado_msgs(8)),
  (0, 5, tornado_msgs(8)),
  (8, 5, tornado_msgs(8)),
])
def test_mesh( dump_vcd, src_delay, sink_delay, test_msgs ):
  run_net_test( dump_vcd, MeshNetworkBL, src_delay, sink_delay, test_msgs,
                nrouters, nmessages, payload_nbits, nentries )
