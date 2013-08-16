#=========================================================================
# StrSearchFunc.py
#=========================================================================

from new_pymtl import *

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

    s.in_    = InPort ( 8 * max_doc_chars )
    s.out    = OutPort( 1 )

  #-----------------------------------------------------------------------
  # find
  #-----------------------------------------------------------------------
  def elaborate_logic( s ):

    @s.tick
    def find_logic():
      to_chr = lambda i : chr( s.in_[i:i+8] )
      doc = ''.join( [ to_chr( i ) for i in range( 0, 64*8, 8 )
                    if to_chr( i ) != '\x00'] )
      #print doc in s.string, doc, s.string
      s.out.next = s.string in doc

      #if s.in_ in s.string:
      #  print "HELLO"
      #  s.out.v = True
      #else:
      #  s.out.v = False

