#=========================================================================
# QueuePortProxy
#=========================================================================
# These classes provide part of a standard Python deque interface, but
# the implementation essentially turns the popleft() and append() methods
# into a val/rdy port-based interface. We use greenlets to enable us to
# wait until data is ready via the val/rdy interface before returning to
# function calling the popleft() or append() method.

from greenlet import greenlet

#=========================================================================
# InQueuePortProxy
#=========================================================================

class InQueuePortProxy (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, in_ ):

    s.in_   = in_
    s.trace = " "

  #-----------------------------------------------------------------------
  # popleft
  #-----------------------------------------------------------------------

  def popleft( s ):

    # Set the rdy signal

    s.in_.rdy.next = 1
    s.trace = "+"

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    # If input interface is not valid then yield

    while not s.in_.val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # Input interface is valid so reset rdy signal and return message

    s.trace = " "
    s.in_.rdy.next = 0
    return s.in_.msg

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

#=========================================================================
# OutQueuePortProxy
#=========================================================================

class OutQueuePortProxy (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, out ):

    s.out   = out
    s.trace = " "

  #-----------------------------------------------------------------------
  # append
  #-----------------------------------------------------------------------

  def append( s, msg ):

    # Set the val signal and message

    s.out.msg.next = msg
    s.out.val.next = 1
    s.trace = "+"

    # Yield so we wait at least one cycle for the rdy

    greenlet.getcurrent().parent.switch(0)

    # If output interface is not ready then yield

    while not s.out.rdy:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # Output interface is ready so reset val signal

    s.trace = " "
    s.out.val.next = 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

