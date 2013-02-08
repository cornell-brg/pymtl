#=========================================================================
# OutputCtrl
#=========================================================================

from   pymtl import *
import pmlib

from   pmlib.arbiters import RoundRobinArbiterEn

from   Counter import Counter

class OutputCtrl (Model):

  @capture_args
  def __init__( s, netmsg_params, max_credit_count, credit_nbits ):

    # Interface Ports

    s.reqs         = InPort  ( 5 )
    s.credit       = InPort  ( 1 )

    s.grants       = OutPort ( 5 )
    s.xbar_sel     = OutPort ( 3 )
    s.out_val      = OutPort ( 1 )
    s.credit_count = OutPort ( credit_nbits )

    # TODO: needed because of translation bugs when an output port is
    #       also used as the input to a submodule!
    s.credit_decr  = Wire ( 1 )
    connect( s.out_val,        s.credit_decr )

    # credit count

    s.credits_counter = Counter( max_credit_count )
    connect( s.credits_counter.increment, s.credit       )
    connect( s.credits_counter.decrement, s.credit_decr  )
    #connect( s.credits_counter.decrement, s.out_val      )
    connect( s.credits_counter.count,     s.credit_count )

    # arbiter

    s.arbiter = RoundRobinArbiterEn( 5 )

    connect( s.arbiter.reqs,   s.reqs    )
    connect( s.arbiter.grants, s.grants  )

  @combinational
  def comb( s ):

    # arbiter enable connection

    s.arbiter.en.value = ~s.credits_counter.zero.value

    # out val calculations

    #s.out_val.value = \
    s.credit_decr.value = \
      ( s.grants.value & s.reqs.value ) != 0

    # xbar sel

    if   ( s.grants.value == 0b00001 ):
      s.xbar_sel.value = 0
    elif ( s.grants.value == 0b00010 ):
      s.xbar_sel.value = 1
    elif ( s.grants.value == 0b00100 ):
      s.xbar_sel.value = 2
    elif ( s.grants.value == 0b01000 ):
      s.xbar_sel.value = 3
    elif ( s.grants.value == 0b10000 ):
      s.xbar_sel.value = 4
    else:
      s.xbar_sel.value = 0


