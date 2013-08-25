#=======================================================================
# queues.py
#=======================================================================
# Collection of queues for cycle-level modeling.

from new_pymtl    import *
from ValRdyBundle import InValRdyBundle, OutValRdyBundle
from collections  import deque

#-----------------------------------------------------------------------
# Queue
#-----------------------------------------------------------------------
class Queue( object ):

  def __init__( self, size=1 ):
    self.size = size
    self.data = deque( maxlen=size )

  def is_empty( self ):
    return len( self.data ) == 0

  def is_full( self ):
    return len( self.data ) == self.size

  def enq( self, item ):
    assert not self.is_full()
    self.data.append( item )

  def deq( self ):
    return self.data.popleft()

  def peek( self ):
    return self.data[0]

  def nitems( self ):
    return len( self.data )

#-----------------------------------------------------------------------
# InValRdyQueue
#-----------------------------------------------------------------------
class InValRdyQueue( Model ):

  def __init__( s, MsgType, size=1 ):
    s.size = size
    s.data = deque( maxlen = size )

    s.in_  = InValRdyBundle( MsgType )

  def elaborate_logic( s ):
    pass

  def is_empty( self ):
    return len( self.data ) == 0

  def deq( self ):
    return self.data.popleft()

  def peek( self ):
    return self.data[0]

  def xtick( s ):
    # update internal state
    if s.in_.rdy and s.in_.val:
      s.data.append( s.in_.msg[:] )
    # set ports
    s.in_.rdy.next = len( s.data ) != s.size

#-----------------------------------------------------------------------
# OutValRdyQueue
#-----------------------------------------------------------------------
class OutValRdyQueue( Model ):

  def __init__( s, MsgType, size=1 ):
    s.size = size
    s.data = deque( maxlen = size )

    s.out  = OutValRdyBundle( MsgType )

  def elaborate_logic( s ):
    pass

  def is_full( self ):
    return len( self.data ) == self.size

  def enq( self, item ):
    assert not self.is_full()
    self.data.append( item )

  def xtick( s ):
    # update internal state
    if s.out.rdy and s.out.val:
      s.data.popleft()
    # set ports
    if len( s.data ) != 0:
      s.out.msg.next = s.data[0]
    s.out.val.next = len( s.data ) != 0

#-----------------------------------------------------------------------
# Pipeline
#-----------------------------------------------------------------------
class Pipeline( object ):

  def __init__( self, stages=1 ):
    assert stages > 0
    self.stages = stages
    self.data   = deque( [None]*stages, maxlen = stages )

  def insert( self, item ):
    self.data[0] = item

  def remove( self ):
    item = self.data[-1]
    self.data[-1] = None
    return item

  def ready( self ):
    return self.data[-1] != None

  def advance( self ):
    self.data.rotate()

