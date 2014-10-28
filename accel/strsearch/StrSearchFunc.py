#=========================================================================
# StrSearchFunc.py
#=========================================================================

from pymtl          import *

StrSignalValue = CreateWrappedClass( str )
# TODO: necessary because RandomDelay module initializes output with an int
#       how should we handle this?
StrSignalValue.__format__ = lambda self, formatstr : str(self)[0:30].ljust(30)

#-------------------------------------------------------------------------
# StrSearchMath
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchMath( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, string ):
    s.string = string

    s.in_    = InPort ( StrSignalValue )
    s.out    = OutPort( 1 )

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    @s.tick
    def find_logic():
      doc = s.in_
      s.out.next = s.string in doc


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

      doc   = s.in_
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

