#=========================================================================
# InValRdyRandStallAdapter
#=========================================================================
# Randomly stalls an input interface.

from copy        import deepcopy
from random      import random

from pymtl       import *

#-------------------------------------------------------------------------
# InValRdyRandStallAdapter
#-------------------------------------------------------------------------

class InValRdyRandStallAdapter (object):

  def __init__( s, in_, stall_prob=0 ):
    s.in_        = in_
    s.stall_prob = stall_prob
    s.data       = None

  def empty( s ):
    return s.data == None

  def deq( s ):
    assert not s.empty()
    item = s.data
    s.data = None
    s.in_.rdy.next = ( random() > s.stall_prob )
    return item

  def first( s ):
    return s.data

  def xtick( s ):

    if s.in_.rdy and s.in_.val:
      s.data = deepcopy(s.in_.msg)

    s.in_.rdy.next = ( s.data == None ) and ( random() > s.stall_prob )

