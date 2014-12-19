#=========================================================================
# StrSearchFunc.py
#=========================================================================

from collections import deque

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from StrSearchFunc import StrSignalValue

#-------------------------------------------------------------------------
# StrSearchMath
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchMath( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, string, stages=4 ):
    s.string = string
    s.stages = stages

    s.in_    = InValRdyBundle( StrSignalValue )
    s.out    = OutValRdyBundle( 1 )

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.buf      = deque( maxlen=2 )
    s.pipeline = deque( s.stages*[None] )

    @s.tick
    def find_logic():

      # Dequeue From Pipeline
      if s.out.val and s.out.rdy:
        s.pipeline[-1] = None

      # Enqueue Into Input Buffer
      if s.in_.val and s.in_.rdy :
        s.buf.append( s.string in s.in_.msg )

      # Advance pipeline
      if s.out.rdy:
        s.pipeline.rotate()
        if s.buf:
          s.pipeline[ 0 ] = s.buf.popleft()

      # Set Ports
      if s.pipeline[-1] != None:
        s.out.msg.next = s.pipeline[-1]
      s.out.val.next = s.pipeline[-1] != None
      s.in_.rdy.next = len( s.buf ) < s.buf.maxlen

  def line_trace( s ):
    return "{}".format( len( s.buf ) )


#-------------------------------------------------------------------------
# StrSearchAlg
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchAlg( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, string ):
    s.string = string

    s.in_    = InValRdyBundle( StrSignalValue )
    s.out    = OutValRdyBundle( 1 )

    s.DFA    = DFA = (len(string) + 1) * [0]

    # build the deterministic finite-state automaton
    i = 0
    DFA[0] = -1
    while i < len(string):
      DFA[i+1] = DFA[i] + 1
      while (DFA[i+1] > 0 and string[i] != string[DFA[i+1] - 1]):
        DFA[i+1] = DFA[DFA[i+1] - 1] + 1
      i+=1

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.buf    = deque( maxlen=2 )
    s.result = None
    s.index  = 0
    s.j      = 0

    @s.tick
    def find_logic():

      # Dequeue
      if s.out.val and s.out.rdy:
        s.result = None

      # Enqueue
      if s.in_.val and s.in_.rdy:
        s.buf.append( s.in_.msg[:] )

      # Do Work:
      if s.buf and s.result == None:

        doc   = s.buf[0]
        j     = s.j

        #while j < len(doc):
        if j <  len( doc ):

          # if character not a match, rewind the DFA
          if (s.index > 0 and doc[j] != s.string[s.index]):
            s.index = s.DFA[s.index]

          # check if this character matches our current search
          if (doc[j] == s.string[s.index]):
            s.index += 1

            # we found a match! now check for overlapping matches
            if s.index == (len(s.string)):
              #s.index = s.DFA[index]
              #print ("FOUND: "+doc[:j+1-len(s.string)]+"|"
              #      +doc[j+1-len(s.string):j+1]+"|"+doc[j+1:])
              s.result = True
              s.index  = 0
              s.j      = -1
              s.buf.popleft()

          # increment the doc indice
          s.j += 1

        else:
          s.result = False
          s.index  = 0
          s.j      = 0
          s.buf.popleft()

      # Set Ports
      if s.result != None:
        s.out.msg.next = s.result
      s.out.val.next = s.result != None
      s.in_.rdy.next = len( s.buf ) < s.buf.maxlen

  def line_trace( s ):
    return "{:2} {:2}".format( len( s.buf[0] )  if s.buf else '  ', s.j )

