#-------------------------------------------------------------------------
# Utility linetracing function
#-------------------------------------------------------------------------

def valrdy_to_str( msg, val, rdy ):

  str = "{}".format( msg )
  num_chars = len(str)

  if val and not rdy:
    str = "#".ljust(num_chars)
  elif not val and rdy:
    str = " ".ljust(num_chars)
  elif not val and not rdy:
    str = ".".ljust(num_chars)

  return str

