#=========================================================================
# Queue
#=========================================================================

import collections

class Queue (object):

  def __init__( s, size ):
    s.queue = collections.deque( maxlen=size )

  def enq( s, value ):
    assert not s.full()
    s.queue.append( value )

  def deq( s ):
    assert not s.empty()
    return s.queue.popleft()

  def front( s ):
    assert not s.empty()
    return s.queue[0]

  def empty( s ):
    return len(s.queue) == 0

  def full( s ):
    return len(s.queue) == s.queue.maxlen

