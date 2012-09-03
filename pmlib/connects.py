#=========================================================================
# Connection helpers
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# auto_connect
#-------------------------------------------------------------------------
# Connect ports with the same name in two different models.

def auto_connect( model_a, model_b ):

  # Iterate over the members in model_a to get a set of port names

  port_names_a = set()
  for member in dir(model_a):
    if isinstance( getattr( model_a, member ), InPort ):
      port_names_a.add( member )
    if isinstance( getattr( model_a, member ), OutPort ):
      port_names_a.add( member )

  # Iterate over the members in model_b to get a set of port names

  port_names_b = set()
  for member in dir(model_b):
    if isinstance( getattr( model_b, member ), InPort ):
      port_names_b.add( member )
    if isinstance( getattr( model_b, member ), OutPort ):
      port_names_b.add( member )

  # Iterate over common ports

  for port_name in port_names_a & port_names_b:
    connect( getattr( model_a, port_name ), getattr( model_b, port_name ) )

