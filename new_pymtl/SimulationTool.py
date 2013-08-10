#=========================================================================
# SimulationTool.py
#=========================================================================
# Tool for simulating hardware models.
#
# This module contains classes which construct a model simulator for
# execution in the Python interpreter.

import pprint
import collections
import inspect
import copy
import warnings

from sys               import flags
from SignalValue       import SignalValue
from ast_visitor       import DetectLoadsAndStores, get_method_ast
#from EventQueue        import new_cpp_queue, cpp_callback
from SimulationMetrics import SimulationMetrics, DummyMetrics

#-------------------------------------------------------------------------
# SimulationTool
#-------------------------------------------------------------------------
# User visible class implementing a tool for simulating hardware models.
#
# This class takes a model instance and creates a simulator for execution
# in the Python interpreter.
class SimulationTool( object ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  # Construct a simulator based on the provided model.
  def __init__( self, model, collect_metrics = False ):

    # Check that the model has been elaborated
    if not model.is_elaborated():
      raise Exception( "cannot initialize {0} tool.\n"
                       "Provided model has not been elaborated yet!!!"
                       "".format( self.__class__.__name__ ) )

    self.model                = model
    self.ncycles              = 0
    self._nets                = []
    self._sequential_blocks   = []
    self._register_queue      = []
    self._event_queue         = EventQueue()
    self._current_func        = None
    self._slice_connects      = set() # TODO: temporary hack
    #self._DEBUG_signal_cbs    = collections.defaultdict(list)

    # Only collect metrics if they are enabled, otherwise replace
    # with a dummy collection class.
    if collect_metrics:
      self.metrics            = SimulationMetrics()
    else:
      self.metrics            = DummyMetrics()

    # If the -O flag was passed to Python, use the perf implementation
    # of cycle, otherwise use the dev version.
    if flags.optimize:
      self.cycle              = self._perf_cycle
      self.eval_combinational = self._perf_eval
    else:
      self.cycle              = self._dev_cycle
      self.eval_combinational = self._dev_eval

    # Actually construct the simulator
    self._construct_sim()

  #-----------------------------------------------------------------------
  # eval_combinational
  #-----------------------------------------------------------------------
  # Evaluates all combinational logic blocks currently in the event queue.
  def eval_combinational( self ):
    pass

  #-----------------------------------------------------------------------
  # _debug_eval
  #-----------------------------------------------------------------------
  # Implementation of eval_combinational() for use during
  # develop-test-debug loops.
  def _dev_eval( self ):
    while self._event_queue.len():
      self._current_func = func = self._event_queue.deq()
      self.metrics.incr_comb_evals( func )
      func()
      self._current_func = None
      #try:
      #  self.metrics.incr_comb_evals( func )
      #  func()
      #  self._current_func = None
      #except TypeError:
      #  # TODO: can we catch this at static elaboration?
      #  raise Exception("Concurrent block '{}' must take no parameters!\n"
      #                  "file: {}\n"
      #                  "line: {}\n"
      #                  "".format( func.func_name,
      #                             func.func_code.co_filename,
      #                             func.func_code.co_firstlineno ) )

  #-----------------------------------------------------------------------
  # _perf_eval
  #-----------------------------------------------------------------------
  # Implementation of eval_combinataional () for use when benchmarking
  # models.
  def _perf_eval( self ):
    while self._event_queue.len():
      #self._event_queue.eval()
      self._current_func = func = self._event_queue.deq()
      func()
      self._current_func = None

  #-----------------------------------------------------------------------
  # cycle
  #-----------------------------------------------------------------------
  # Advances the simulator by a single clock cycle, executing all
  # sequential @tick and @posedge_clk blocks defined in the design, as
  # well as any @combinational blocks that have been added to the event
  # queue.
  #
  # Note: see _debug_cycle and _perf_cycle for actual implementations.
  def cycle( self ):
    pass

  #-----------------------------------------------------------------------
  # _debug_cycle
  #-----------------------------------------------------------------------
  # Implementation of cycle() for use during develop-test-debug loops.
  def _dev_cycle( self ):

    # Call all events generated by input changes
    self.eval_combinational()

    # TODO: Hacky auto clock generation
    #if self.vcd:
    #  print >> self.o, "#%s" % (10 * self.num_cycles)
    self.model.clk.value = 0

    #if self.vcd:
    #  print >> self.o, "#%s" % ((10 * self.num_cycles) + 5)
    self.model.clk.value = 1

    # Distinguish between events caused by input vectors changing (above)
    # and events caused by clocked logic (below).
    self.metrics.start_tick()

    # Call all rising edge triggered functions
    for func in self._sequential_blocks:
      func()

    # Then flop the shadow state on all registers
    while self._register_queue:
      reg = self._register_queue.pop()
      reg.flop()

    # Call all events generated by synchronous logic
    self.eval_combinational()

    # Increment the simulator cycle count
    self.ncycles += 1

    # Tell the metrics module to prepare for the next cycle
    self.metrics.incr_metrics_cycle()

  #-----------------------------------------------------------------------
  # _perf_cycle
  #-----------------------------------------------------------------------
  # Implementation of cycle() for use when benchmarking models.
  def _perf_cycle( self ):

    # Call all events generated by input changes
    self.eval_combinational()

    # Call all rising edge triggered functions
    for func in self._sequential_blocks:
      func()

    # Then flop the shadow state on all registers
    while self._register_queue:
      reg = self._register_queue.pop()
      reg.flop()

    # Call all events generated by synchronous logic
    self.eval_combinational()

    # Increment the simulator cycle count
    self.ncycles += 1

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------
  # Sets the reset signal high and cycles the simulator.
  def reset( self ):
    self.model.reset.v = 1
    self.cycle()
    self.cycle()
    self.model.reset.v = 0

  #-----------------------------------------------------------------------
  # print_line_trace
  #-----------------------------------------------------------------------
  # Print cycle number and line trace of model.
  def print_line_trace( self ):
    print "{:>3}:".format( self.ncycles ), self.model.line_trace()

  #-----------------------------------------------------------------------
  # add_event
  #-----------------------------------------------------------------------
  # Add an event to the simulator event queue for later execution.
  #
  # This function will check if the written SignalValue instance has any
  # registered events (functions decorated with @combinational), and if
  # so, adds them to the event queue.
  def add_event( self, signal_value ):
    # TODO: debug_event
    #print "    ADDEVENT: VALUE", signal_value.v,
    #print signal_value in self._DEBUG_signal_cbs,
    #print [x.fullname for x in signal_value._DEBUG_signal_names],
    #print self._DEBUG_signal_cbs[signal_value]

    self.metrics.incr_add_events()

    # Execute all slice callbacks immediately

    #for func in signal_value._slices:
    #  func()

    # Place all other callbacks in the event queue for execution later

    for func in signal_value._callbacks:
      self.metrics.incr_add_callbk()
      if func != self._current_func:
        self._event_queue.enq( func.cb, func.id )

  #-----------------------------------------------------------------------
  # _construct_sim
  #-----------------------------------------------------------------------
  # Construct a simulator for the provided model.
  def _construct_sim( self ):
    self._create_nets( self.model )
    self._insert_signal_values()
    self._register_decorated_functions( self.model )
    self._create_slice_callbacks()

  #-----------------------------------------------------------------------
  # _create_nets
  #-----------------------------------------------------------------------
  # Generate nets describing structural connections in the model.  Each
  # net describes a set of Signal objects which have been interconnected,
  # either directly or indirectly, by calls to connect().
  def _create_nets( self, model ):

    # DEBUG
    #print 70*'-'
    #print "Model:", model
    #print "Ports:"
    #pprint.pprint( model.get_ports(), indent=3 )
    #print "Submodules:"
    #pprint.pprint( model.get_submodules(), indent=3 )

    #def a_printer( some_set ):
    #  return [ x.parent.name + '.' + x.name for x in some_set ]
    #t = [ a_printer( [ x.src_node, x.dest_node] ) for x in model.get_connections() ]
    #print "Connections:"
    #pprint.pprint( model.get_connections(), indent=3 )
    #pprint.pprint( t, indent=3 )

    # Utility function to collect all the Signal type objects (ports,
    # wires, constants) in the model.
    def collect_signals( model ):
      self.metrics.reg_model( model )
      signals = set( model.get_ports() + model.get_wires() )
      for m in model.get_submodules():
        signals.update( collect_signals( m ) )
      return signals

    signals = collect_signals( model )

    # Utility function to filter only supported connections: ports, and
    # wires.  No slices or Constants.
    def valid_connection( c ):
      if c.src_slice != None or c.dest_slice != None:
        # TEMPORARY HACK, remove slice connections from connections?
        self._slice_connects.add( c )
        return False
      else:
        return True

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

    # Initially signals contains all the Signal type objects in the
    # model.  We perform a depth-first search on the connections of each
    # Signal object, and remove connected objects from the signals set.
    # The result is a collection of nets describing structural
    # connections in the design. Each independent net will later be
    # transformed into a single SignalValue object.
    while signals:
      s = signals.pop()
      net = iter_dfs( s )
      for i in net:
        #if i is not s:
        #  signals.remove( i )
        signals.discard( i )
      self._nets.append( net )

  #-----------------------------------------------------------------------
  # _insert_signal_values
  #-----------------------------------------------------------------------
  # Transform each net into a single SignalValue object. Model attributes
  # currently referencing Signal objects will be modified to reference
  # the SignalValue object of their associated net instead.
  def _insert_signal_values( self ):

    # DEBUG
    #print
    #print "NODE SETS"
    #for set in self._nets:
    #  print '    ', [ x.parent.name + '.' + x.name for x in set ]

    # Utility functions which create SignalValue callbacks.

    def create_comb_update_cb( sim, svalue ):
      def notify_sim_comb_update():
        sim.add_event( svalue )
      return notify_sim_comb_update

    def create_seq_update_cb( sim, svalue ):
      def notify_sim_seq_update():
        sim._register_queue.append( svalue )
      return notify_sim_seq_update

    # Each grouping represents a single SignalValue object. Perform a swap
    # so that all attributes currently pointing to Signal objects in this
    # grouping instead point to the SignalValue.
    for group in self._nets:

      # Get an element out of the set and use it to determine the bitwidth
      # of the net, needed to create a properly sized SignalValue object.
      # TODO: no peek() so have to pop() then reinsert it! Another way?
      # TODO: what about BitStructs?
      temp = group.pop()
      group.add( temp )
      svalue = temp.msg_type
      # TODO: should this be visible to sim?
      svalue._next = copy.copy( svalue )
      #svalue._DEBUG_signal_names = group

      # Add a callback to the SignalValue to notify SimulationTool every
      # time a sequential update occurs (.next is written).
      # TODO: currently all signals get this, necessary?
      svalue.notify_sim_seq_update = create_seq_update_cb ( self, svalue )

      # Create a callback for the SignalValue to notify SimulationTool
      # every time a combinational update occurs (.value is written).
      # We just store the callback for now, only add it later if we detect
      # that a combinational block is sensitive to us
      svalue._ucb                  = create_comb_update_cb( self, svalue )

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

  #-----------------------------------------------------------------------
  # _register_decorated_functions
  #-----------------------------------------------------------------------
  # Register all decorated @tick, @posedge_clk, and @combinational
  # functions with the simulator.  Sequential logic blocks get called
  # any time cycle() is called, combinational logic blocks are registered
  # with SignalValue objects and get added to the event queue as values
  # change.
  def _register_decorated_functions( self, model ):

    # Add all cycle driven functions
    self._sequential_blocks.extend( model._tick_blocks )
    self._sequential_blocks.extend( model._posedge_clk_blocks )

    # Utility function to turn attributes/names acquired from the ast
    # into Python objects
    # TODO: should never use eval... but this is easy
    # TODO: how to handle when self is neither 's' nor 'self'?
    # TODO: how to handle temps!
    def name_to_object( name ):
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
        else:                                    raise NameError
      except NameError:
        warnings.warn( "Cannot add variable '{}' to sensitivity list."
                       "".format( name ), Warning )
        return None

    # Utility function to recursively add signals/lists of signals to
    # the sensitivity list.
    def add_senses( name ):
      obj = name_to_object( name )
      # If name_to_object returned a tuple, this is a list inside of a
      # for loop.  Iteratively go through each object in the list and
      # recursively call add_senses on it.
      if   isinstance( obj, tuple ):
        obj_list, list_name, attr = obj
        for i, o in enumerate( obj_list ):
          obj_name = "{}[{}]{}".format( list_name, i, attr )
          add_senses( obj_name )
      # If this is a signal value, add it to the sensitivity list
      elif isinstance( obj, SignalValue ):
        model._newsenses[ func ].append( obj._target_bits )


    # Get the sensitivity list of each event driven (combinational) block
    # TODO: do before or after we swap value nodes?
    for func in model._combinational_blocks:
      tree = get_method_ast( func )
      loads, stores = DetectLoadsAndStores().enter( tree )
      for name in loads:
        add_senses( name )

    # Iterate through all @combinational decorated function names we
    # detected, retrieve their associated function pointer, then add
    # entries for each item in the function's sensitivity list to
    # svalue_callbacks
    # TODO: merge this code with above to reduce mem of data structures?
    for func_ptr, sensitivity_list in model._newsenses.items():
      func_ptr.id = self._event_queue.get_id()
      func_ptr.cb = func_ptr
      self.metrics.reg_eval( func_ptr.cb )
      for signal_value in sensitivity_list:

        # Only add "notify_sim" funcs if @comb blocks are sensitive to us
        signal_value.notify_sim_comb_update = signal_value._ucb

        # Prime the simulation by putting all events on the event_queue
        # This will make sure all nodes come out of reset in a consistent
        # state. TODO: put this in reset() instead?
        signal_value.register_callback( func_ptr )
        self._event_queue.enq( func_ptr.cb, func_ptr.id )

        #self._DEBUG_signal_cbs[ signal_value ].append( func_ptr )

    # Recursively perform for submodules
    for m in model.get_submodules():
      self._register_decorated_functions( m )

  #-----------------------------------------------------------------------
  # _create_slice_callbacks
  #-----------------------------------------------------------------------
  # All ConnectionEdges that contain bit slicing need to be turned into
  # combinational blocks.  This significantly simplifies the connection
  # graph update logic.
  def _create_slice_callbacks( self ):

    # Utility function to create our callback
    def create_slice_cb_closure( c ):
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

    for c in self._slice_connects:
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
        func_ptr = create_slice_cb_closure( c )
        signal_value = c.src_node._signalvalue
        signal_value.register_slice( func_ptr )
        func_ptr.id = self._event_queue.get_id()
        func_ptr.cb = func_ptr
        self._event_queue.enq( func_ptr.cb, func_ptr.id )
        self.metrics.reg_eval( func_ptr.cb, is_slice = True )
        #self._DEBUG_signal_cbs[ signal_value ].append( func_ptr )

#-------------------------------------------------------------------------
# EventQueue
#-------------------------------------------------------------------------
class EventQueue( object ):

  def __init__( self, initsize = 1000 ):
    self.fifo     = collections.deque()
    self.func_bv  = [ False ] * initsize
    self.func_ids = 0

  def enq( self, event, id ):
    if not self.func_bv[ id ]:
      self.func_bv[ id ] = True
      self.fifo.appendleft( event )

  def deq( self ):
    event = self.fifo.pop()
    self.func_bv[ event.id ] = False
    return event

  def len( self ):
    return len( self.fifo )

  def __len__( self ):
    return len( self.fifo )

  def get_id( self ):
    id = self.func_ids
    self.func_ids += 1
    if self.func_ids > len( self.func_bv ):
      self.func_bv.extend( [ False ] * 1000 )
    return id

#class EventQueue( object ):
#
#  def __init__( self ):
#    self.fifo     = new_cpp_queue()
#    self.func_ids = 0
#    assert self.fifo.len() == 0
#
#  def enq( self, cb, id):
#    self.fifo.enq( cb, id )
#
#  def deq( self ):
#    return self.fifo.deq()
#
#  def len( self ):
#    return self.fifo.len()
#
#  def __len__( self ):
#    return self.fifo.len()
#
#  def get_id( self ):
#    id = self.func_ids
#    self.func_ids += 1
#    return id
