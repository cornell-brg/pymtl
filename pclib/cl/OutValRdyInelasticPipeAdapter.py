#=========================================================================
# OutValRdyInelasticPipeAdapter
#=========================================================================
# Models an inelastic pipeline at an output interface. Note that if
# nstages is set to zero, then this essentially models a single-entry
# bypass queue.

from copy        import deepcopy
from collections import deque
from pymtl       import *
from pipelines   import Pipeline

#-----------------------------------------------------------------------
# OutValRdyBypassAdapter
#-----------------------------------------------------------------------
# An output val-rdy bypass adapter

class OutValRdyBypassAdapter( Model ):

  def __init__( s, out, size=1 ):
    s.out  = out
    s.data = deque( maxlen = size )

  def is_full( s ):
    return len( s.data ) == s.data.maxlen

  def full( s ):
    return s.is_full()

  def enq( s, item ):
    assert not s.is_full()
    s.data.append( item )
    if len( s.data ) != 0:
      s.out.msg.next = s.data[0]
    s.out.val.next = len( s.data ) != 0

  def xtick( s ):
    if s.out.rdy and s.out.val:
      s.data.popleft()
    if len( s.data ) != 0:
      s.out.msg.next = s.data[0]
    s.out.val.next = len( s.data ) != 0

#-------------------------------------------------------------------------
# OutValRdyInelasticPipeAdapter
#-------------------------------------------------------------------------

class OutValRdyInelasticPipeAdapter (object):

  def __init__( s, out, nstages=1 ):

    s.nstages    = nstages
    s.out_q      = OutValRdyBypassAdapter( out, size = 1 )

    # instantiate a pipeline if requires
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

    s.out_q.xtick()

    if s.nstages != 0:

      # If the output bypass queue adapter is not full
      if not s.out_q.is_full():

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
