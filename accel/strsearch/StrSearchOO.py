#=========================================================================
# StrSearchOO.py
#=========================================================================

#-------------------------------------------------------------------------
# StrSearchMath
#-------------------------------------------------------------------------
# Simple python string searcher.
class StrSearchMath( object ):
  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( self, string ):
    self.string = string

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def find( self, doc ):
    return self.string in doc

#-------------------------------------------------------------------------
# StrSearchAlg
#-------------------------------------------------------------------------
# Knuth-Morris-Pratt algorithm.
class StrSearchAlg( object ):
  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( self, string ):
    self.re  = re  = string
    self.DFA = DFA = (len(re) + 1) * [0]

    # build the deterministic finite-state automaton
    i = 0
    DFA[0] = -1
    while i < len(re):
      DFA[i+1] = DFA[i] + 1
      while (DFA[i+1] > 0 and re[i] != re[DFA[i+1] - 1]):
        DFA[i+1] = DFA[DFA[i+1] - 1] + 1
      i+=1

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def find( self, doc ):
    index = 0
    j     = 0

    while j < len(doc):

      # if character not a match, rewind the DFA
      #while (index > 0 and doc[j] != re[index]):
      if (index > 0 and doc[j] != self.re[index]):
        index = self.DFA[index]

      # check if this character matches our current search
      if (doc[j] == self.re[index]):
        index += 1

        # we found a match! now check for overlapping matches
        if index == (len(self.re)):
          index = self.DFA[index]
          #print ("FOUND: "+doc[:j+1-len(self.re)]+"|"
          #      +doc[j+1-len(self.re):j+1]+"|"+doc[j+1:])
          return True

      # increment the doc indice
      j += 1

    return False
