#=========================================================================
# OutValRdyInelasticPipeAdapter
#=========================================================================
# Models an inelastic pipeline at an output interface. Note that if
# nstages is set to zero, then this essentially models a single-entry
# bypass queue.

from copy        import deepcopy
from collections import deque
from pymtl       import *
from pclib.cl    import OutValRdyQueueAdapter
from pipelines   import Pipeline

#-------------------------------------------------------------------------
# OutValRdyInelasticPipeAdapter
#-------------------------------------------------------------------------

class OutValRdyInelasticPipeAdapter (object):

  def __init__( s, out, nstages=1 ):

    s.nstages    = nstages

    # instantiate a single-entry bypass queue adapter
    s.out_q      = OutValRdyQueueAdapter( out )

    # instantiate a cycle-level pipeline
    if s.nstages > 0:
      s.pipe       = Pipeline( s.nstages )

  def full( s ):
    if s.nstages == 0:
      return s.out_q.full()
    else:
      return not s.pipe.data[0] == None

  def enq( s, item ):
    assert not s.full()
    if s.nstages == 0:
      s.out_q.enq( item )
    else:
      s.pipe.insert( item )

  def xtick( s ):

    # Call the xtick of output bypass queue adapter
    s.out_q.xtick()

    # Model the pipeline behavior
    if s.nstages != 0:

      # If the output bypass queue adapter is not full
      if not s.out_q.full():

        # Items graduating from pipeline, add to output queue
        if s.pipe.ready():
          s.out_q.enq( s.pipe.remove() )

        # Advance the pipeline
        s.pipe.advance()

  def __str__( s ):
    if s.nstages > 0:
      return ''.join([ ("*" if x != None else ' ') for x in s.pipe.data ])
    else:
      return ""
