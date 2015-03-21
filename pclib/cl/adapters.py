#=========================================================================
# adapters
#=========================================================================

from copy        import deepcopy
from collections import deque

from pymtl       import *

#-------------------------------------------------------------------------
# InValRdyQueueAdapter
#-------------------------------------------------------------------------

class InValRdyQueueAdapter (object):

  def __init__( s, in_, size=1 ):
    s.in_  = in_
    s.data = deque( maxlen = size )

  def empty( s ):
    return len( s.data ) == 0

  def deq( s ):
    assert not s.empty()
    item = s.data.popleft()
    s.in_.rdy.next = ( len( s.data ) != s.data.maxlen )
    return item

  def first( s ):
    return s.data[0]

  def clear( s ):
    s.data.clear()
    s.in_.rdy.next = 1

  def __len__( s ):
    return len(s.data)

  def xtick( s ):
    if s.in_.rdy and s.in_.val:
      s.data.append( deepcopy(s.in_.msg) )
    s.in_.rdy.next = ( len( s.data ) != s.data.maxlen )

#-------------------------------------------------------------------------
# OutValRdyQueueAdapter
#-------------------------------------------------------------------------

class OutValRdyQueueAdapter (object):

  def __init__( s, out, size=1 ):
    s.out  = out
    s.data = deque( maxlen = size )

  def full( s ):
    return len( s.data ) == s.data.maxlen

  def enq( s, item ):
    assert not s.full()
    s.data.append( item )
    if len( s.data ) != 0:
      s.out.msg.next = s.data[0]
    s.out.val.next = ( len( s.data ) != 0 )

  def clear( s ):
    s.data.clear()
    s.out.val.next = 0

  def __len__( s ):
    return len(s.data)

  def xtick( s ):
    if s.out.rdy and s.out.val:
      s.data.popleft()
    if len( s.data ) != 0:
      s.out.msg.next = s.data[0]
    s.out.val.next = ( len( s.data ) != 0 )

