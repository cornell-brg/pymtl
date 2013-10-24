#=========================================================================
# cgen.py
#=========================================================================

import sys

def inspect_live_object( obj ):

  create_class( obj )



def create_class( obj, o=sys.stdout ):
  
  print   >> o
  print   >> o, "class {} {{".format( obj.__class__.__name__ )
  print   >> o, "  public:"
  for name, obj in obj.__dict__.items():
    print >> o, "    {} {}; ".format( get_c_type( obj ), name, obj )
  print   >> o, "};"


symbol_table = {
  bool: "bool", 
  int:  "int",
  str:  "string",
}

def get_c_type( obj ):
  return symbol_table[ type(obj) ]

