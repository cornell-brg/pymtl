#=========================================================================
# Simulation Tool
#=========================================================================
# Tool for simulating MTL models.
#
# This module contains classes which construct a simulator given a MTL model
# for execution in the python interpreter.

import pprint
import collections
import inspect

from new_Bits import Bits

#=========================================================================
# SimulationTool
#=========================================================================
# User visible class implementing a tool for simulating MTL models.
#
# This class takes a MTL model instance and creates a simulator for execution
# in the python interpreter.
class SimulationTool():

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  # Construct a simulator from a MTL model.
  def __init__( self, model ):

    # Check that the model has been elaborated
    if not model.is_elaborated():
      raise Exception( "cannot initialize {0} tool.\n"
                       "Provided model has not been elaborated yet!!!"
                       "".format( self.__class__.__name__ ) )

    self.model            = model
    self.value_sets       = []
    self.event_queue      = collections.deque()
    self.vnode_callbacks  = collections.defaultdict(list)

    # Actually construct the simulator
    self._construct_sim()

  #-----------------------------------------------------------------------
  # Evaluate Combinational Blocks
  #-----------------------------------------------------------------------
  # Evaluates all events in the combinational logic event queue.
  def eval_combinational(self):
    while self.event_queue:
      func = self.event_queue.pop()
      #self.pstats.add_eval_call( func, self.num_cycles )
      func()

  #-----------------------------------------------------------------------
  # Add Callback to Event Queue
  #-----------------------------------------------------------------------
  # Add an event to the simulator event queue for later execution.
  #
  # This function will check if the written Node instance has any
  # registered events (functions decorated with @combinational), and if so, adds
  # them to the event queue.
  def add_event(self, value_node):
    # TODO: debug_event
    #print "    ADDEVENT: VALUE", value_node, value_node.value, value_node in self.vnode_callbacks
    if value_node in self.vnode_callbacks:
      funcs = self.vnode_callbacks[value_node]
      for func in funcs:
        if func not in self.event_queue:
          self.event_queue.appendleft(func)

  #-----------------------------------------------------------------------
  # Construct Simulator
  #-----------------------------------------------------------------------
  # Construct a simulator for the provided model.
  def _construct_sim(self):
    self._group_connection_nodes( self.model )
    self._insert_value_nodes()
    self._register_decorated_functions( self.model )

  #-----------------------------------------------------------------------
  # Find Node Groupings
  #-----------------------------------------------------------------------
  def _group_connection_nodes( self, model ):

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

    for m in model.get_submodules():
      self._group_connection_nodes( m )

    # Create value nodes starting at the leaves, should simplify
    # ConnectionGraph minimization?
    for c in model.get_connections():

      # Temporary exception
      if c.src_slice or c.dest_slice:
        raise Exception( "Slices not supported yet!" )

      # Create a new value set containing this connections ports
      new_group = set( [ c.src_node, c.dest_node ] )
      updated = True

      # See if this value set has overlap with another set, if
      # so, return the union of that group and see if the union
      # has overlap with other sets.   Otherwise add the new grouping
      # to the collection of value sets.
      # TODO: super inefficient!  Replace by walking value graphs?
      while updated:
        updated = False
        for group in self.value_sets:
          if not group.isdisjoint( new_group ):
            new_group = group.union( new_group )
            self.value_sets.remove( group )
            updated = True
            break
        if not updated:
          self.value_sets.append( new_group )

    # Some ports (ie. top-level module ports) may have no connections.
    # We still need to replace them with ValueNodes.
    for p in model.get_ports():
      if not p.connections:
        self.value_sets.append( set( [ p ] ) )

  #-----------------------------------------------------------------------
  # Replace Ports with Value Nodes
  #-----------------------------------------------------------------------
  def _insert_value_nodes( self ):

    # DEBUG
    #print
    #print "NODE SETS"
    #for set in self.value_sets:
    #  print '    ', [ x.parent.name + '.' + x.name for x in set ]

    from types import MethodType

    def create_notify_sim_closure( sim, vnode ):
      def notify_sim():
        sim.add_event( vnode )
      return notify_sim

    # Each grouping is a bits object, make all ports pointing to
    # it point to the Bits object instead
    for group in self.value_sets:
      temp  = group.pop()
      # TODO: what about BitStructs?
      vnode = Bits( temp.nbits )
      vnode.notify_sim = create_notify_sim_closure( self, vnode )
      group.add( temp )
      for x in group:
        if 'IDX' in x.name:
          name, idx = x.name.split('IDX')
          x.parent.__dict__[ name ][ int (idx) ] = vnode
        else:
          x.parent.__dict__[ x.name ] = vnode

  #-----------------------------------------------------------------------
  # Register Decorated Functions
  #-----------------------------------------------------------------------
  # Utility method which detects the sensitivity list of annotated functions.
  #
  # This method uses the DecoratedFunctionVisitor class to walk the AST of the
  # provided model and register any functions annotated with special
  # decorators.
  def _register_decorated_functions(self, model):
    # Create an AST Tree
    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    #print
    #import debug_utils
    #debug_utils.print_ast(tree)
    comb_funcs    = set()
    posedge_funcs = set()

    # Walk the tree to inspect a given modules combinational blocks and
    # build a sensitivity list from it,
    # only gives us function names... still need function pointers
    _DecoratedFunctionVisitor( comb_funcs, posedge_funcs ).visit( tree )
    #print "COMB", comb_funcs
    #print "PEDGE", posedge_funcs

    # Iterate through all @combinational decorated function names we detected,
    # retrieve their associated function pointer, then add entries for each
    # item in the function's sensitivity list to vnode_callbacks
    print "\nSENSES"
    for func_name, sensitivity_list in model._newsenses.items():
      print '@@@', func_name, [ x.parent.name+'.'+x.name for x in sensitivity_list ]
      func_ptr = model.__getattribute__(func_name)
      for signal in sensitivity_list:
        # TODO: handle arrays
        value_ptr = model.__getattribute__( signal.name )
        print value_ptr
        self.vnode_callbacks[value_ptr] += [func_ptr]
        # Prime the simulation by putting all events on the event_queue
        # This will make sure all nodes come out of reset in a consistent
        # state. TODO: put this in reset() instead?
        if func_ptr not in self.event_queue:
          self.event_queue.appendleft(func_ptr)

    # Add all posedge_clk functions
    for func_name in posedge_funcs:
      func_ptr = model.__getattribute__(func_name)
      self.posedge_clk_fns += [func_ptr]

    # Recursively perform for submodules
    for m in model.get_submodules():
      self._register_decorated_functions( m )

#=========================================================================
# Decorated Function Visitor
#=========================================================================
# Hidden class for building a sensitivity list from the AST of a MTL model.
#
# This class takes the AST tree of a Model class and looks for any
# functions annotated with the @combinational decorator. Variables that perform
# loads in these functions are added to the sensitivity list (registry).
import ast
class _DecoratedFunctionVisitor(ast.NodeVisitor):
  # http://docs.python.org/library/ast.html#abstract-grammar

  # Construct a new Decorated Function Visitor.
  def __init__(self, comb_funcs, posedge_funcs):
    self.current_fn    = None
    self.comb_funcs    = comb_funcs
    self.posedge_funcs = posedge_funcs
    self.add_regs      = False

  # Visit all functions, but only parse those with special decorators.
  def visit_FunctionDef(self, node):
    #pprint.pprint( dir(node) )
    #print "Function Name:", node.name
    if not node.decorator_list:
      return
    decorator_names = [x.id for x in node.decorator_list]
    if 'combinational' in decorator_names:
      self.comb_funcs.add( node.name )
    elif 'posedge_clk' in decorator_names:
      self.posedge_funcs.add( node.name )
    elif 'tick' in decorator_names:
      self.posedge_funcs.add( node.name )

