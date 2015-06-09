#=======================================================================
# sim_utils.py
#=======================================================================

import warnings
import greenlet

from ..ast_helpers            import get_method_ast
from ...datatypes.SignalValue import SignalValue

from ast_visitor import (
  DetectLoadsAndStores,
  DetectDecorators,
  DetectIncorrectValueNext,
  DetectMissingValueNext
)

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
# signals_to_nets
#-----------------------------------------------------------------------
# Generate nets describing structural connections in the model.  Each
# net describes a set of Signal objects which have been interconnected,
# either directly or indirectly, by calls to connect().
def signals_to_nets( signals ):

  nets           = []
  slice_connects = set()

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

#---------------------------------------------------------------------
# insert_signal_values
#---------------------------------------------------------------------
# Transform each net into a single SignalValue object. Model attributes
# currently referencing Signal objects will be modified to reference
# the SignalValue object of their associated net instead.
def insert_signal_values( sim, nets ):

  # Utility functions which create SignalValue callbacks.

  #-------------------------------------------------------------------
  # create_comb_update_cb
  #-------------------------------------------------------------------
  def create_comb_update_cb( sim, svalue ):
    def notify_sim_comb_update():
      sim.add_event( svalue )
    return notify_sim_comb_update

  #-------------------------------------------------------------------
  # create_seq_update_cb
  #-------------------------------------------------------------------
  def create_seq_update_cb( sim, svalue ):
    def notify_sim_seq_update():
      sim._register_queue.append( svalue )
    return notify_sim_seq_update

  # Each grouping represents a single SignalValue object. Perform a swap
  # so that all attributes currently pointing to Signal objects in this
  # grouping instead point to the SignalValue.
  for group in nets:

    # Get an element out of the set and use it to determine the bitwidth
    # of the net, needed to create a properly sized SignalValue object.
    # TODO: no peek() so have to pop() then reinsert it! Another way?
    # TODO: what about BitStructs?
    temp = group.pop()
    group.add( temp )

    # TODO: should this be visible to sim?
    svalue       = temp.dtype()
    svalue._next = temp.dtype()

    #svalue._DEBUG_signal_names = group

    # Add a callback to the SignalValue to notify SimulationTool every
    # time a sequential update occurs (.next is written).
    # TODO: currently all signals get this, necessary?
    svalue.notify_sim_seq_update = create_seq_update_cb ( sim, svalue )

    # Create a callback for the SignalValue to notify SimulationTool
    # every time a combinational update occurs (.value is written).
    # We just store the callback for now, only add it later if we detect
    # that a combinational block is sensitive to us.
    svalue._ucb                   = create_comb_update_cb( sim, svalue )

    # Modify model attributes currently referencing Signal objects to
    # reference SignalValue objects instead.
    for x in group:
      # Set the value of the SignalValue object if we encounter a
      # constant (check for Constant object instead?)
      if isinstance( x._signalvalue, int ):
        svalue.write_value( x._signalvalue )
        svalue.constant = True
      # Otherwise swap the value
      else:
        # We need 'in locals()' because of the nested function above,
        # see: http://stackoverflow.com/a/4484946
        exec( "x.parent.{} = svalue".format( x.name ) ) in locals()

      # Also give signals a pointer to the SignalValue object.
      # (Needed for VCD tracing and slice logic generator).
      x._signalvalue = svalue

#---------------------------------------------------------------------
# register_seq_blocks
#---------------------------------------------------------------------
# Register all decorated @tick and  @posedge_clk functions.
# Sequential logic blocks get executed any time cycle() is called.
def register_seq_blocks( model ):

  all_models = []
  def create_model_list( current ):
    all_models.append( current )
    for m in current.get_submodules():
      create_model_list( m )

  create_model_list( model )

  sequential_blocks = []
  for i in all_models:
    for func in i.get_tick_blocks() + i.get_posedge_clk_blocks():

      # Grab the AST and src code of each function
      tree, src = get_method_ast( func )

      # Check there were no mistakes in use of .value/.next
      DetectIncorrectValueNext( func, 'value' ).visit( tree )
      DetectMissingValueNext  ( func, 'next'  ).visit( tree )

      # If function is decorated with tick_fl, wrap it with a greenlet
      if 'tick_fl' in DetectDecorators().enter( tree ):
        func = _pausable_tick( func )

      sequential_blocks.append( func )

    for func in i.get_combinational_blocks():

      tree, _ = get_method_ast( func )
      DetectIncorrectValueNext( func, 'next'  ).visit( tree )
      DetectMissingValueNext  ( func, 'value' ).visit( tree )

  return sequential_blocks

#---------------------------------------------------------------------
# register_comb_blocks
#---------------------------------------------------------------------
# Register all decorated @combinational functions with the simulator.
# Combinational logic blocks are registered with SignalValue objects
# and get added to the event queue when values are updated.
def register_comb_blocks( model, event_queue ):

  # Get the sensitivity list of each event driven (combinational) block
  # TODO: do before or after we swap value nodes?

  for func in model.get_combinational_blocks():
    tree, _ = get_method_ast( func )
    loads, stores = DetectLoadsAndStores().enter( tree )
    for name in loads:
      _add_senses( func, model, name )

  # Iterate through all @combinational decorated function names we
  # detected, retrieve their associated function pointer, then add
  # entries for each item in the function's sensitivity list to
  # svalue_callbacks
  # TODO: merge this code with above to reduce mem of data structures?
  # TODO: sensitivity_list contains duplicate items if a signal is
  #       accessed via slices or bitstruct accesses, use set instead?

  for func_ptr, sensitivity_list in model._newsenses.items():
    func_ptr.id = event_queue.get_id()
    func_ptr.cb = func_ptr
    #self.metrics.reg_eval( func_ptr.cb )
    for signal_value in sensitivity_list:

      # Only add "notify_sim" funcs if @comb blocks are sensitive to us
      signal_value.notify_sim_comb_update = signal_value._ucb

      # Prime the simulation by putting all events on the event_queue
      # This will make sure all nodes come out of reset in a consistent
      # state. TODO: put this in reset() instead?
      signal_value.register_callback( func_ptr )
      event_queue.enq( func_ptr.cb, func_ptr.id )

      #self._DEBUG_signal_cbs[ signal_value ].append( func_ptr )

  # Recursively perform for submodules
  for m in model.get_submodules():
    register_comb_blocks( m, event_queue )

#-----------------------------------------------------------------------
# _add_senses
#-----------------------------------------------------------------------
# Utility function to recursively add signals/lists of signals to
# the sensitivity list.
def _add_senses( func, model, name ):
  obj = _attr_name_to_object( model, name )
  # If name_to_object returned a tuple, this is a list inside of a
  # for loop.  Iteratively go through each object in the list and
  # recursively call add_senses on it.
  if   isinstance( obj, tuple ):
    obj_list, list_name, attr = obj
    for i, o in enumerate( obj_list ):
      obj_name = "{}[{}]{}".format( list_name, i, attr )
      _add_senses( func, model, obj_name )

  # If this is a signal value, add it to the sensitivity list
  elif isinstance( obj, SignalValue ):

    # Distinguish between attributes storing signals (InPort/OutPort/Wire)
    # and SignalValues (e.g., Bits), by checking the _ucb attribute.
    target_bits = obj._target_bits
    if hasattr( target_bits, '_ucb' ):
      model._newsenses[ func ].append( target_bits )
    elif model._debug:
      warnings.warn( "Cannot add SignalValue '{}' to sensitivity list."
                     "".format( name ), Warning )

#-----------------------------------------------------------------------
# _attr_name_to_object
#-----------------------------------------------------------------------
# Utility function to turn attributes/names acquired from the ast
# into Python objects
# TODO: should never use eval... but this is easy
# TODO: how to handle when self is neither 's' nor 'self'?
# TODO: how to handle temps!
def _attr_name_to_object( model, name ):
  # Temporarily creates the names 'self' and 's' in the current
  # scope.  SUPER HACKY
  self = s = model
  # If slice or list, get name components previous to indexing
  if '[?]' in name:
    name, extra = name.split('[?]', 1)
  # Try to return the Python object attached to the name. If the
  # object is not a  SignalValue or a list, we can't add it to
  # the sensitivity list.  Sometimes this is okay (eg. constants),
  # but sometimes this indicates an error in the user's code, so
  # display a warning.
  # In the case of a list, we need to reconstruct the name of each
  # item in the list so we can try to add it to the sensitivity
  # list. Return a tuple containing the list object, the list name
  # and the attribute string the appears after the list indexing.
  try:
    x = eval( name )
    if   isinstance( x, SignalValue ): return x
    elif isinstance( x, list        ): return ( x, name, extra )
    else:                              raise NameError
  except NameError:
    if model._debug:
      warnings.warn( "Cannot add variable '{}' to sensitivity list."
                     "".format( name ), Warning )
    return None


#-----------------------------------------------------------------------
# create_slice_callbacks
#-----------------------------------------------------------------------
# All ConnectionEdges that contain bit slicing need to be turned into
# combinational blocks.  This significantly simplifies the connection
# graph update logic.
def create_slice_callbacks( slice_connects, event_queue ):

  for c in slice_connects:
    src = c.src_node._signalvalue
    # If slice is connect to a Constant, don't create a callback.
    # Just write the constant value now.
    if isinstance( src, int ):
      dest      = c.dest_node._signalvalue
      dest_addr = c.dest_slice if c.dest_slice != None else slice( None )
      dest[ dest_addr ].v = src
    # If slice is connected to another Signal, create a callback
    # and put it on the combinational event queue.
    else:
      func_ptr     = _create_slice_cb_closure( c )
      signal_value = c.src_node._signalvalue
      signal_value.register_slice( func_ptr )
      func_ptr.id = event_queue.get_id()
      func_ptr.cb = func_ptr
      event_queue.enq( func_ptr.cb, func_ptr.id )
      #self.metrics.reg_eval( func_ptr.cb, is_slice = True )
      #self._DEBUG_signal_cbs[ signal_value ].append( func_ptr )

#-----------------------------------------------------------------------
# _create_slice_cb_closure
#-----------------------------------------------------------------------
# Utility function to create our callback
def _create_slice_cb_closure( c ):
  src       = c.src_node._signalvalue
  dest      = c.dest_node._signalvalue
  src_addr  = c.src_slice  if c.src_slice  != None else slice( None )
  dest_bits = dest[ c.dest_slice ] if c.dest_slice != None else dest
  def slice_cb():
    # We need to slice the src each time.  This is because writing
    # to a BitSlice will updates the Bits it was sliced from, but
    # not vice versa.
    dest_bits.v = src[ src_addr ]
  return slice_cb


#---------------------------------------------------------------------
# _pausable_tick
#---------------------------------------------------------------------
# Experimental support for creating tick blocks where we can pause the
# execution within the tick block. This avoids the need for creating a
# GreenletWrapper explicitly.
def _pausable_tick( func ):

  # The inner_wrapper function is the one which we will wrap in a
  # greenlet. It calls the tick function forever. It pauses after each
  # call to the tick function, but the tick function itself can also
  # pause.

  def inner_wrapper():
    while True:

      # Call the tick function

      func()

      # Yield so we always only do one tick per cycle

      greenlet.greenlet.getcurrent().parent.switch(0)

  # Create a greenlet and save it with the model. Note that we
  # currently only allow a single pausable_tick per model.

  func._pausable_tick = greenlet.greenlet(inner_wrapper)

  # The outer_wrapper is what will become the new tick function. This
  # is what gets added to the tick list.

  def outer_wrapper():
    func._pausable_tick.switch()

  return outer_wrapper

#-----------------------------------------------------------------------
# register_cffi_updates
#-----------------------------------------------------------------------
def register_cffi_updates( model ):

  def visit_models( m ):
    if hasattr( m, '_cffi_update' ):
      for port, func_ptr in m._cffi_update.items():
        signal_value = port._signalvalue
        signal_value.register_slice( func_ptr )
    else:
      for subm in m.get_submodules():
        visit_models( subm )

  visit_models( model )

