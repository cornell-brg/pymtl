#=========================================================================
# OutValRdyInelasticPipeAdapter
#=========================================================================
# Models an inelastic pipeline at an output interface. Note that if
# nstages is set to zero, then this essentially models a single-entry
# bypass queue.

from copy        import deepcopy
from collections import deque
from pymtl       import *

#-------------------------------------------------------------------------
# OutValRdyInelasticPipeAdapter
#-------------------------------------------------------------------------

class OutValRdyInelasticPipeAdapter (object):

  def __init__( s, out, nstages=1 ):
    s.out        = out
    s.nstages    = nstages
    s.pipe       = deque( [None]*(nstages+1) )
    s.skidbuffer = deque( maxlen = 1 )

  def skidbuffer_full( s ):
    return len( s.skidbuffer ) == s.skidbuffer.maxlen

  def full( s ):
    if s.nstages == 0:
      return s.skidbuffer_full()
    else:
      return not s.out.rdy

  def enq( s, item ):
    if s.nstages == 0:
      assert not s.skidbuffer_full()
      s.skidbuffer.append( item )
      s.out.msg.next = s.skidbuffer[0]
      s.out.val.next = 1
    else:
      assert s.out.rdy
      s.pipe[-1] = deepcopy(item)

  def xtick( s ):

    # If nstages == 0, then model a single-entry bypass queue ...

    if s.nstages == 0:

      if s.out.rdy and s.out.val:
        s.skidbuffer.popleft()
        s.out.val.next = 0

    # ... else we model pipeline behavior

    else:

      # If output was ready previous cycle ...

      if s.out.rdy:

        # Remove item from front of pipeline

        s.pipe.popleft()

        # Tentatively append None, this may be overwritten with an enq

        s.pipe.append(None)

        # Setup output msg/val for next cycle

        if s.pipe[0] != None:
          s.out.val.next = 1
          s.out.msg.next = s.pipe[0]
        else:
          s.out.val.next = 0
          s.out.msg.next = 0

  def __str__( s ):
    if s.nstages > 0:
      return ''.join([ ("*" if x != None else ' ') for x in reversed(s.pipe) ])
    else:
      return ""
