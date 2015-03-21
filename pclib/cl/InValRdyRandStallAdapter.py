#=========================================================================
# InValRdyRandStallAdapter
#=========================================================================
# Randomly stalls an input interface.

from copy        import deepcopy
from random      import Random
from pymtl       import *

#-------------------------------------------------------------------------
# InValRdyRandStallAdapter
#-------------------------------------------------------------------------

class InValRdyRandStallAdapter (object):

  def __init__( s, in_, stall_prob=0, seed=0x9dd809a6 ):
    s.in_        = in_

    s.stall_prob = stall_prob
    s.data       = None

    # We keep our own internal random number generator to keep the state
    # of this generator completely separate from other generators. This
    # ensure that any delays are reproducable.

    s.rgen = Random()
    s.rgen.seed(seed)

  def empty( s ):
    return s.data == None

  def deq( s ):
    assert not s.empty()
    item = s.data
    s.data = None
    s.in_.rdy.next = ( s.rgen.random() > s.stall_prob )
    return item

  def first( s ):
    return s.data

  def xtick( s ):

    if s.in_.rdy and s.in_.val:
      s.data = deepcopy(s.in_.msg)

    s.in_.rdy.next = ( s.data == None ) and ( s.rgen.random() > s.stall_prob )

