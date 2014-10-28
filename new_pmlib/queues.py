#=======================================================================
# queues.py
#=======================================================================
# Collection of queues for cycle-level modeling.

from pymtl    import *
from ValRdyBundle import InValRdyBundle, OutValRdyBundle
from collections  import deque

#-----------------------------------------------------------------------
# Queue
#-----------------------------------------------------------------------
class Queue( object ):

  def __init__( self, size=1 ):
    self.data = deque( maxlen=size )

  def is_empty( self ):
    return len( self.data ) == 0

  def is_full( self ):
    return len( self.data ) == self.data.maxlen

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

  def __init__( s, MsgType, size=1, pipe=False ):
    s.in_  = InValRdyBundle( MsgType )
    s.data = deque( maxlen = size )
    s.deq  = s._pipe_deq if pipe else s._simple_deq

  def elaborate_logic( s ):
    pass

  def is_empty( s ):
    return len( s.data ) == 0

  def empty( s ):
    return s.is_empty()

  def deq( s ):
    pass

  def _simple_deq( s ):
    return s.data.popleft()

  def _pipe_deq( s ):
    data = s.data.popleft()
    s.in_.rdy.next = len( s.data ) != s.data.maxlen
    return data

  def peek( s ):
    return s.data[0]

  def xtick( s ):
    if s.in_.rdy and s.in_.val:
      s.data.append( s.in_.msg[:] )
    s.in_.rdy.next = len( s.data ) != s.data.maxlen

#-----------------------------------------------------------------------
# OutValRdyQueue
#-----------------------------------------------------------------------
class OutValRdyQueue( Model ):

  def __init__( s, MsgType, size=1, bypass=False ):
    s.out  = OutValRdyBundle( MsgType )
    s.data = deque( maxlen = size )
    s.enq  = s._bypass_enq if bypass else s._simple_enq

  def elaborate_logic( s ):
    pass

  def is_full( s ):
    return len( s.data ) == s.data.maxlen

  def full( s ):
    return s.is_full()

  def enq( s ):
     s.data.append( item )

  def _simple_enq( s, item ):
    assert not s.is_full()
    s.data.append( item )

  def _bypass_enq( s, item ):
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

class ChildReqRespQueueAdapter( Model ):

  def __init__( s, child, size=1 ):
    s.req_q  = InValRdyQueue ( child.req  )
    s.resp_q = OutValRdyQueue( child.resp )

    s.connect(s.req_q.in_.msg, child.req_msg)
    s.connect(s.req_q.in_.val, child.req_val)
    s.connect(s.req_q.in_.rdy, child.req_rdy)

    s.connect(s.resp_q.out.msg, child.resp_msg)
    s.connect(s.resp_q.out.val, child.resp_val)
    s.connect(s.resp_q.out.rdy, child.resp_rdy)

  def xtick( s ):
    s.req_q.xtick()
    s.resp_q.xtick()

  def elaborate_logic( s ):
    pass

  def get_req( s ):
    return s.req_q.deq()

  def push_resp( s, resp ):
    s.resp_q.enq( resp )


#-----------------------------------------------------------------------
# ParentReqRespQueueAdapter
#-----------------------------------------------------------------------
class ParentReqRespQueueAdapter( Model ):

  def __init__( s, parent, size=1 ):
    s.req_q  = OutValRdyQueue( parent.req  )
    s.resp_q = InValRdyQueue ( parent.resp )

    s.connect(s.req_q.out.msg, parent.req_msg)
    s.connect(s.req_q.out.val, parent.req_val)
    s.connect(s.req_q.out.rdy, parent.req_rdy)

    s.connect(s.resp_q.in_.msg, parent.resp_msg)
    s.connect(s.resp_q.in_.val, parent.resp_val)
    s.connect(s.resp_q.in_.rdy, parent.resp_rdy)

  def xtick( s ):
    s.req_q.xtick()
    s.resp_q.xtick()

  def elaborate_logic( s ):
    pass

  def push_req( s, resp ):
    s.req_q.enq( resp )

  def get_resp( s ):
    return s.resp_q.deq()

