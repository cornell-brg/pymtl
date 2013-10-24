#=========================================================================
# cgen.py
#=========================================================================

from cgen import inspect_live_object

def test_class_fields():

  class TestObj( object ):
    def __init__( self ):
      self.a = 5

  x = TestObj()

  inspect_live_object( x )



