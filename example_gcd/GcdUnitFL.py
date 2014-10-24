#=========================================================================
# GcdUnit functional-level model
#=========================================================================

from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle
from new_pmlib.queues import Queue, InValRdyQueue, OutValRdyQueue

import fractions

#=========================================================================
# GCD Unit Functional-Level Model
#=========================================================================
class GcdUnitFL( Model ):

  #-----------------------------------------------------------------------
  # Constructor: Define Interface
  #-----------------------------------------------------------------------
  def __init__( s ):

    s.in_ = InValRdyBundle ( 64 )
    s.out = OutValRdyBundle( 32 )
 
  #-----------------------------------------------------------------------
  # Elaborate: Define Connectivity and Logic
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    msg_type = s.in_.msg.msg_type
    s.queue = InValRdyQueue( msg_type, size=64 )
    s.connect( s.in_, s.queue.in_ )
        
    s.buf_full = False

    @s.tick
    def logic():

      s.queue.xtick()

      if s.out.val and s.out.rdy:
        s.buf_full = False

      if not s.queue.is_empty() and not s.buf_full:
	data = s.queue.deq()
	src0 = data[ 0:32].uint()
	src1 = data[32:64].uint()
        s.out.msg.next = fractions.gcd( src0, src1 )
	s.buf_full = True

      s.out.val.next = s.buf_full

  #-----------------------------------------------------------------------
  # Line Tracing: Debug Output
  #-----------------------------------------------------------------------
  def line_trace( s ):

    return "{} () {}".format( s.in_, s.out)

