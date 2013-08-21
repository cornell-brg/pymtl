#=========================================================================
# StrSearchFunc.py
#=========================================================================

from new_pymtl     import *
from new_pmlib     import InValRdyBundle, OutValRdyBundle
from StrSearchFunc import StrSignalValue

#-------------------------------------------------------------------------
# StrSearchMath
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchMath( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, max_doc_chars, string ):
    s.string = string

    s.in_    = InValRdyBundle( StrSignalValue )
    s.out    = OutValRdyBundle( 1 )

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    s.buf_full = False

    @s.tick
    def find_logic():
      if s.out.val and s.out.rdy:
        s.buf_full = False

      if s.in_.val and s.in_.rdy:
        s.out.msg.next = s.string in s.in_.msg
        s.buf_full = True

      s.out.val.next = s.buf_full
      s.in_.rdy.next = True


#-------------------------------------------------------------------------
# StrSearchAlg
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchAlg( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, max_doc_chars, string ):
    s.string = string

    s.in_    = InPort ( StrSignalValue )
    s.out    = OutPort( 1 )

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

    @s.tick
    def find_logic():

      doc   = s.in_.data()
      index = 0
      j     = 0

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
            s.out.next = True
            return

        # increment the doc indice
        j += 1

      s.out.next = False

