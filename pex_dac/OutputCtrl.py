#=========================================================================
# OutputCtrl
#=========================================================================

from   pymtl import *
import pmlib

from   RoundRobinArbiterEn5x5 import RoundRobinArbiterEn5x5

from   Counter import Counter

class OutputCtrl (Model):

  def __init__( s, max_credit_count, credit_nbits ):

    # Local Constants

    s.max_credit_count = max_credit_count

    # Interface Ports

    s.reqs         = InPort  ( 5 )
    s.credit       = InPort  ( 1 )

    s.grants       = OutPort ( 5 )
    s.xbar_sel     = OutPort ( 3 )
    s.out_val      = OutPort ( 1 )
    s.credit_count = OutPort ( credit_nbits )

    # Wire

    s.incr = Wire( 1 )

    # credit count

    s.credits_counter = Counter( max_count=max_credit_count )
    connect( s.credits_counter.decrement, s.credit       )
    connect( s.credits_counter.increment, s.incr      )
    connect( s.credits_counter.count,     s.credit_count )

    # arbiter

    s.arbiter = RoundRobinArbiterEn5x5( )

    connect( s.arbiter.reqs,   s.reqs    )
    connect( s.arbiter.grants, s.grants  )

  @combinational
  def comb( s ):

    # arbiter enable connection

    s.arbiter.en.value = \
      ( s.credits_counter.count.value < s.max_credit_count )

    # out val calculations

    s.out_val.value = \
      ( s.grants.value & s.reqs.value ) != 0

    s.incr.value = \
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


