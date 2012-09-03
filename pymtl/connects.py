#=========================================================================
# Connection helpers
#=========================================================================

from pymtl import *
import re

#-------------------------------------------------------------------------
# connect_auto
#-------------------------------------------------------------------------
# Connect ports with the same name in two different models.

def connect_auto( model_a, model_b ):

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

#-------------------------------------------------------------------------
# connect_chain
#-------------------------------------------------------------------------
# Given a list of models, connect the output ports named out_* from the
# first model to the input ports of the second model named in_* where the
# wildcard portions match. Iteratively do the same for all models in
# order. So if model_a and ports out_0 and out_1, model_b has ports in_0
# and in_1 as well as out_0 and out_1 and finally model_c has ports in_0
# and in_1 the following will connect these three models together in a
# chain.
#
#  connect_chain([ model_a, model_b, model_c ])
#

def connect_chain( models ):

  assert len(models) > 1

  out_pattern = re.compile(r'^out_(.*)$')

  for i in xrange(len(models)-1):

    model_curr = models[i]
    model_next = models[i+1]

    print model_curr, ">>>", model_next

    # Iterate over the members in current model to get a set of port names

    port_names_curr = set()
    for member in dir(model_curr):
      if isinstance( getattr( model_curr, member ), InPort ):
        port_names_curr.add( member )
      if isinstance( getattr( model_curr, member ), OutPort ):
        port_names_curr.add( member )

    # Iterate over the members in next model to get a set of port names

    port_names_next = set()
    for member in dir(model_next):
      if isinstance( getattr( model_next, member ), InPort ):
        port_names_next.add( member )
      if isinstance( getattr( model_next, member ), OutPort ):
        port_names_next.add( member )

    # Iterate over port names in current model looking for matches in the
    # port names for the next model. This is slow, there is probably a
    # better way.

    for port_name_curr in port_names_curr:

      print port_name_curr

      # See if the port in the current model is an out_ port

      match_out = out_pattern.match(port_name_curr)
      if match_out:

        # If so then search for corresponding in_ port in next model

        port_name_next = "in_" + match_out.group(1)
        if port_name_next in port_names_next:

          print "connecting", model_curr, ".", port_name_curr, "->", \
                              model_next, ".", port_name_next

          connect( getattr( model_curr, port_name_curr ),
                   getattr( model_next, port_name_next ) )

