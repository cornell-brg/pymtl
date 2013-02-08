#=========================================================================
# Counter.py
#=========================================================================

from   pymtl import *
import pmlib

from   math import ceil, log

# Counter Model

class Counter (Model):

  @capture_args
  def __init__( s, max_count ):

    # Local Constants

    s.max_count = max_count
    s.nbits     = int( ceil( log( max_count + 1, 2 ) ) )

    # Interface

    s.increment = InPort  ( 1 )
    s.decrement = InPort  ( 1 )
    s.count     = OutPort ( s.nbits )
    s.zero      = OutPort ( 1 )

    # credit count register

    s.count_reg = pmlib.regs.RegRst( s.nbits, reset_value = max_count )
    connect( s.count_reg.out, s.count )

  @combinational
  def comb( s ):

    if   ( s.increment.value and ~s.decrement.value
         and ( s.count_reg.out.value < s.max_count ) ):
      s.count_reg.in_.value = s.count_reg.out.value + 1
    elif ( ~s.increment.value and s.decrement.value
         and ( s.count_reg.out.value > 0 ) ):
      s.count_reg.in_.value = s.count_reg.out.value - 1
    else:
      s.count_reg.in_.value = s.count_reg.out.value

    s.zero.value = ( s.count_reg.out.value == 0 )

