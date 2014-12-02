#==============================================================================
# GcdFL_test
#==============================================================================

from pymtl        import *
from pclib.test   import TestSource, TestMemory
from GcdProcCL    import GcdProcCL as Gcd
from pclib.ifaces import CP2Msg, mem_msgs

import pytest

#------------------------------------------------------------------------------
# TestHarness
#------------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, lane_id ):

    cpu_ifc = CP2Msg( 5, 32 )
    s.lane = Gcd( cpu_ifc )

  def elaborate_logic( s ):
    pass

  def done( s ):
    return s.lane.cpu_ifc_resp.val

  def line_trace( s ):
    return "{}".format( s.lane.line_trace() )

#------------------------------------------------------------------------------
# run_gcd_test
#------------------------------------------------------------------------------
def run_gcd_test( dump_vcd, model, lane_id, src_a, src_b, exp_value):

  model.vcd_file = dump_vcd
  model.elaborate()
  sim = SimulationTool( model )

  sim.reset()

  sim.print_line_trace()
  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc_req.val.next = 1
  model.lane.cpu_ifc_req.msg.data.next = src_a
  model.lane.cpu_ifc_req.msg.ctrl_msg.next = 1

  sim.print_line_trace()
  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc_req.val.next = 1
  model.lane.cpu_ifc_req.msg.data.next = src_b
  model.lane.cpu_ifc_req.msg.ctrl_msg.next = 2

  sim.cycle()
  sim.cycle()
  model.lane.cpu_ifc_req.val.next = 1
  model.lane.cpu_ifc_req.msg.data.next = True
  model.lane.cpu_ifc_req.msg.ctrl_msg.next = 0

  while not model.done() and sim.ncycles < 300:
    sim.print_line_trace()
    sim.cycle()
    model.lane.cpu_ifc_req.val.next = 0
  sim.print_line_trace()
  assert model.done()

  assert exp_value == model.lane.cpu_ifc_resp.msg

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#------------------------------------------------------------------------------
# test_gcd
#------------------------------------------------------------------------------
#
def test_gcd_cl1( dump_vcd ):
  lane = 0
  run_gcd_test( dump_vcd,
                TestHarness( lane ),
                lane,
                16,
                12,
                4,
              )

def test_gcd_cl2( dump_vcd ):
  lane = 0
  run_gcd_test( dump_vcd,
                TestHarness( lane ),
                lane,
                72,
                71,
                1,
              )
