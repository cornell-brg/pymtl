#=========================================================================
# InputRowCtrl
#=========================================================================
# control for packets through east/west ports

from   pymtl import *
import pmlib

from RouteCompute import RouteCompute

class InputRowCtrl (Model):

  @capture_args
  def __init__( s, router_x_id, router_y_id, num_routers, srcdest_nbits,
    credit_nbits, max_credit_count ):

    # Local Constants

    s.max_credit_count = max_credit_count

    # Interface Ports

    s.deq_val         = InPort  ( 1 )
    s.dest            = InPort  ( srcdest_nbits )
    s.grants          = InPort  ( 5 )

    s.out0_credit_cnt = InPort  ( credit_nbits )
    s.out2_credit_cnt = InPort  ( credit_nbits )

    s.deq_rdy         = OutPort ( 1 )
    s.reqs            = OutPort ( 5 )
    s.in_credit       = OutPort ( 1 )

    # Temporary Wires

    s.bubble_north    = Wire    ( 1 )
    s.bubble_south    = Wire    ( 1 )

    # route computation

    s.routecomp = RouteCompute( router_x_id, router_y_id, num_routers,
                    srcdest_nbits )
    connect( s.routecomp.dest, s.dest )

    # in_credit buffer

    s.in_credit_reg = pmlib.regs.RegRst( 1 )
    connect( s.in_credit_reg.out, s.in_credit )

  @combinational
  def comb( s ):

    # bubble condition calculations

    s.bubble_north.value = ( s.out0_credit_cnt.value < (s.max_credit_count - 1 ) )
    s.bubble_south.value = ( s.out2_credit_cnt.value < (s.max_credit_count - 1 ) )

    # reqs calculation

    if   s.deq_val.value and ( s.routecomp.route.value == 4 ):
      s.reqs.value = 0b10000
    elif (   ( s.deq_val.value and ( s.routecomp.route.value == 0 ) )
          and s.bubble_north.value ):
      s.reqs.value = 0b00001
    elif s.deq_val.value and ( s.routecomp.route.value == 1 ):
      s.reqs.value = 0b00010
    elif (   ( s.deq_val.value and ( s.routecomp.route.value == 2 ) )
          and s.bubble_south.value ):
      s.reqs.value = 0b00100
    elif s.deq_val.value and ( s.routecomp.route.value == 3 ):
      s.reqs.value = 0b01000
    else:
      s.reqs.value = 0b00000

    # deq_rdy calculation

    s.deq_rdy.value = \
     ( ( s.grants.value & s.reqs.value ) != 0 )

    # input to credit register

    s.in_credit_reg.in_.value = \
     ( ( s.grants.value & s.reqs.value ) != 0 )
