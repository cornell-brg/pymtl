#=========================================================================
# ValRdy helper functions
#=========================================================================
# Eventually, I don't think we will need this when we have true val/rdy
# port bundles.
#

def valrdy_to_str( msg, val, rdy ):

  str = ""
  if val and rdy:
    str = "{:04x}".format( msg )
  elif val and not rdy:
    str = "#   "
  elif not val and rdy:
    str = "    "
  elif not val and not rdy:
    str = ".   "
  else:
    str = "?   "

  return str

