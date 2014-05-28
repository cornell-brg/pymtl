#=========================================================================
# GreenletWrapper
#=========================================================================
# Thin shim that makes it a little cleaner to wrap a function in a
# greenlet and then check and see if we are finished executing that
# function.

from greenlet import greenlet

class GreenletWrapper:

  def __init__( self, func ):
    self.func_greenlet = greenlet(func)

  def __call__( self, *args, **kwargs ):
    self.func_greenlet.switch( *args, **kwargs )

  def done( self ):
    return self.func_greenlet.dead

