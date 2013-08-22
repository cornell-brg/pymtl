#=========================================================================
# StrSearchFunc.py
#=========================================================================

from new_pymtl     import *
from new_pmlib     import InValRdyBundle, OutValRdyBundle
from StrSearchFunc import StrSignalValue
from collections   import deque

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

    s.buf = deque( maxlen=2 )

    @s.tick
    def find_logic():

      # Dequeue
      if s.out.val and s.out.rdy:
        s.buf.popleft()

      # Enqueue
      if s.in_.val and s.in_.rdy:

        doc   = s.in_.msg
        index = 0
        j     = 0
        found = False

        while j < len(doc):

          # if character not a match, rewind the DFA
          #while (index > 0 and doc[j] != re[index]):
          if (index > 0 and doc[j] != s.string[index]):
            index = s.DFA[index]

          # check if this character matches our current search
          if (doc[j] == s.string[index]):
            index += 1

            # we found a match! now check for overlapping matches
            if index == (len(s.string)):
              index = s.DFA[index]
              #print ("FOUND: "+doc[:j+1-len(s.string)]+"|"
              #      +doc[j+1-len(s.string):j+1]+"|"+doc[j+1:])
              found = True
              break

          # increment the doc indice
          j += 1

        s.buf.append( found )

      # Set Ports
      if len( s.buf ) > 0:
        s.out.msg.next = s.buf[0]
      s.out.val.next = len( s.buf ) > 0
      s.in_.rdy.next = len( s.buf ) < s.buf.maxlen

  def line_trace( s ):
    return "{}".format( len( s.buf ) )

