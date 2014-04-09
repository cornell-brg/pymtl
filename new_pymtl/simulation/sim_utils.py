#=======================================================================
# sim_utils.py
#=======================================================================

import warnings

from ast_visitor   import DetectLoadsAndStores
from ..ast_helpers import get_method_ast
from ..SignalValue import SignalValue

#-----------------------------------------------------------------------
# collect_signals
#-----------------------------------------------------------------------
# Utility function to collect all the Signal type objects (ports,
# wires, constants) in the model.
def collect_signals( model ):
  #self.metrics.reg_model( model )
  signals = set( model.get_ports() + model.get_wires() )
  for m in model.get_submodules():
    signals.update( collect_signals( m ) )
  return signals

#-----------------------------------------------------------------------
# connections_to_nets
#-----------------------------------------------------------------------
# Generate nets describing structural connections in the model.  Each
# net describes a set of Signal objects which have been interconnected,
# either directly or indirectly, by calls to connect().
def connections_to_nets( model ):

  nets           = []
  slice_connects = set()

  signals = collect_signals( model )

  #---------------------------------------------------------------------
  # valid_connection
  #---------------------------------------------------------------------
  # Utility function to filter only supported connections (ports/wires),
  # ignore slices and constants.
  def valid_connection( c ):
    if c.src_slice != None or c.dest_slice != None:
      # TODO: collect slice connections somewhere else
      slice_connects.add( c )
      return False
    else:
      return True

  #---------------------------------------------------------------------
  # iter_dfs
  #---------------------------------------------------------------------
  # Iterative Depth-First-Search algorithm, borrowed from Listing 5-5
  # in 'Python Algorithms': http://www.apress.com/9781430232377/
  def iter_dfs( s ):
    S, Q = set(), []
    Q.append( s )
    while Q:
      u = Q.pop()
      if u in S: continue
      S.add( u )
      connected_signals = [ x.other( u ) for x in u.connections
                            if valid_connection( x ) ]
      Q.extend( connected_signals )
      #yield u
    return S

  # Initially signals contains all the Signal type objects in the model.
  # We perform a depth-first search on the connections of each Signal
  # object, and remove connected objects from the signals set.  The
  # result is a collection of nets describing structural connections in
  # the design. Each independent net will later be transformed into a
  # single SignalValue object.

  while signals:
    s = signals.pop()
    net = iter_dfs( s )
    for i in net:
      #if i is not s: signals.remove( i )
      signals.discard( i )
    nets.append( net )

  return nets, slice_connects

