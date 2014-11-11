#=========================================================================
# Queue
#=========================================================================

import collections
import copy

class Queue (object):

  def __init__( s, size ):
    s.queue = collections.deque( maxlen=size )

  def num_empty_entries( s ):
    return s.queue.maxlen - len(s.queue)

  def enq( s, value ):
    assert not s.full()
    s.queue.append( copy.deepcopy(value) )

  def deq( s ):
    assert not s.empty()
    return s.queue.popleft()

  def front( s ):
    assert not s.empty()
    return s.queue[0]

  def clear( s ):
    s.queue.clear()

  def empty( s ):
    return len(s.queue) == 0

  def full( s ):
    return len(s.queue) == s.queue.maxlen

  def __len__( s ):
    return len(s.queue)

