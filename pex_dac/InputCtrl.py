#=========================================================================
# InputCtrl
#=========================================================================
# For Ring Network

from   pymtl import *
import pmlib

from   RingRouteCompute import RingRouteCompute

class InputCtrl (Model):

  @capture_args
  def __init__( s, router_id, num_routers, srcdest_nbits,
    credit_nbits, max_credit_count ):

    # Local Constants

    s.max_credit_count = max_credit_count

    # Interface Ports

    s.deq_val         = InPort  ( 1 )
    s.dest            = InPort  ( srcdest_nbits )
    s.grants          = InPort  ( 3 )

    s.deq_rdy         = OutPort ( 1 )
    s.reqs            = OutPort ( 3 )
    s.in_credit       = OutPort ( 1 )

    # Temporary Wires

    s.bubble_east     = Wire    ( 1 )
    s.bubble_west     = Wire    ( 1 )

    # route computation

    s.routecomp = RingRouteCompute( router_id, num_routers,
                    srcdest_nbits)
    connect( s.routecomp.dest, s.dest )

    # in_credit buffer

    s.in_credit_reg = pmlib.regs.RegRst( 1 )
    connect( s.in_credit_reg.out, s.in_credit )

  @combinational
  def comb( s ):

    # reqs calculation

    if   s.deq_val.value and ( s.routecomp.route.value == 0 ):
      s.reqs.value = 0b001
    elif s.deq_val.value and ( s.routecomp.route.value == 1 ):
      s.reqs.value = 0b010
    elif s.deq_val.value and ( s.routecomp.route.value == 2 ):
      s.reqs.value = 0b100
    else:
      s.reqs.value = 0b000

    # deq_rdy calculation

    s.deq_rdy.value = \
     ( ( s.grants.value & s.reqs.value ) != 0 )

    # input to credit register

    s.in_credit_reg.in_.value = \
     ( ( s.grants.value & s.reqs.value ) != 0 )
