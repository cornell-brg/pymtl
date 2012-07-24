"""Tool for simulating MTL models.

This module contains classes which construct a simulator given a MTL model
for execution in the python interpreter.
"""

from collections import deque
import ast, _ast
import inspect
import pprint
from rtler_vbase import VerilogSlice, ValueNode, VerilogConstant, RegisterNode
import pygraphviz as pgv

# TODO: make commandline parameter
debug_hierarchy = False
# TODO: temporary
dag = pgv.AGraph(directed=True)


class LogicSim():

  """User visible class implementing a tool for simulating MTL models.

  This class takes a MTL model instance and creates a simulator for execution
  in the python interpreter (once the generate() function is called).
  """

  def __init__(self, model):
    """Construct a simulator from a MTL model.

    Parameters
    ----------
    model: an instantiated MTL model (VerilogModule).
    """
    self.model = model
    self.num_cycles      = 0
    self.vnode_callbacks = {}
    self.rnode_callbacks = []
    self.event_queue     = deque()
    self.posedge_clk_fns = []
    self.node_groups = []

  def cycle(self):
    """Execute a single cycle in the simulator.

    Executes any functions in the event queue and increments the num_cycles
    count.

    TODO: execute all @posedge, @negedge decorated functions.
    """
    # Call all event queue events
    while self.event_queue:
      func = self.event_queue.pop()
      func()

    # Call all rising edge triggered functions
    for func in self.posedge_clk_fns:
      func()

    # Then call clock() on all registers
    for reg in self.rnode_callbacks:
      reg.clock()

    self.num_cycles += 1

  def add_event(self, value_node):
    """Add an event to the simulator event queue for later execution.

    This function will check if the written ValueNode instance has any
    registered events (functions decorated with @combinational), and if so, adds
    them to the event queue.

    Parameters
    ----------
    value_node: the ValueNode instance which was written and called add_event().
    """
    # TODO: debug_event
    #print "    ADDEVENT: VALUE", value_node, value_node.value, value_node in self.vnode_callbacks
    if value_node in self.vnode_callbacks:
      funcs = self.vnode_callbacks[value_node]
      for func in funcs:
        if func not in self.event_queue:
          self.event_queue.appendleft(func)

  def generate(self):
    """Construct a simulator for the provided model by adding necessary hooks.

    Parameters
    ----------
    model: the MTL model (VerilogModule) to add simulator hooks to. If None is
           provided, the model provided in the LogicSim constructor is used
           (toplevel).
    """

    # build up the node_groups data structure
    self.find_node_groupings(self.model)

    # create ValueNodes and add them to each port
    #pprint.pprint( self.node_groups )
    for group in self.node_groups:
      width = max( [port.width for port in group] )
      # TODO: handle constant
      value = ValueNode(width, sim=self)
      for port in group:
        if not port._value:
          port._value = value

    # walk the AST of each module to create sensitivity lists and add registers
    self.infer_sensitivity_list(self.model)


    #self.add_value_nodes(model)
    # Recursively call on all submodules
    #for m in model.submodules:
    #  self.generate( m )
    # DEBUGGING: creates a graphviz graph
    # Recursively call on all submodules
    # All value nodes have been added, create the sensitivity list.
    #self.infer_sensitivity_list( model )
    #self.graphviz(model)

    # TODO: debug_sensitivity_list
    #print "VALUE NODE CALLBACKS"
    #pprint.pprint( self.vnode_callbacks )

  def find_node_groupings(self, model):
    if debug_hierarchy:
      print 70*'-'
      print "Model:", model
      print "Ports:"
      pprint.pprint( model.ports, indent=3 )
      print "Submodules:"
      pprint.pprint( model.submodules, indent=3 )

    # Walk ports to add value nodes.  Do leaves or toplevel first?
    for p in model.ports:
      self.add_to_node_groups(p)

    for m in model.submodules:
      self.find_node_groupings( m )


  def add_to_node_groups(self, port):
    group = set([port])
    group.update( port.connections )
    # Utility function for our list comprehension below.  If the group and set
    # are disjoint, return true.  Otherwise return false and join the set to
    # the group.
    def disjoint(group,s):
      if not group.isdisjoint(s):
        group.update(s)
        return False
      else:
        return True

    self.node_groups[:] = [x for x in self.node_groups if disjoint(group, x)]
    self.node_groups += [ group ]

  def add_value_nodes(self, model):
    """Utility method which adds ValueNodes to port and wire connections.

    WARNING: this implementation is very fragile.  The best way to really do
    this would be to create some kind of datastructure that groups all ports
    and wires by their connections.  Once this datastructure is complete we
    could instantiate a ValueNode for each grouping, set its width to be equal
    to the largest port attached to that node, and then walk through the list
    of all ports attached to the node and give them pointers to the ValueNode
    instance.

    Parameters
    ----------
    model: a VerilogModel instance
    """
    #print "\n### CREATE NODES"
    for port in model.ports:
      port_name = "{0}.{1}".format( port.parent.name, port.name )
      #print port_name, port.connections
      has_vnodes = any(cxn._value for cxn in port.connections)
      if port._value:
        #print "HAS VAL", port._value
        pass
      # We don't have a ValueNode yet, and none of our connections do either,
      # create a new value
      elif not port._value and not has_vnodes:
        widths = [port.width]
        widths += [cxn.width for cxn in port.connections]
        max_width = max(widths)
        port._value = ValueNode(max_width, sim=self)
        #print "CREATE:", port._value
      # We don't have a ValueNode yet, but at least one of our connections does,
      # attach to his connection.  This is pretty fragile...
      # TODO: fix
      else:
        widths = [cxn.width for cxn in port.connections]
        idx = widths.index( max(widths) )
        cxn = port.connections[idx]
        assert port.width == cxn.width
        port._value = cxn._value
        #print "CONNECT:", port._value

  def graphviz(self, model):
    """Temporary utility method to add edges to a graphviz plot."""
    print "\n### VERIFY NODES"
    # DAG Debug
    for port in model.ports:
      pname = "{0}.{1}".format( port.parent.name, port.name )
      print "EDGE", pname, port._value
      if not port._value:
        dag.add_edge( pname, "NONE" )
      elif isinstance(port._value, VerilogSlice):
        name = "{0}.{1}".format( port._value.parent.name, port._value.name )
        dag.add_edge( pname, name )
        dag.add_edge( name, port._value._value)
        #dag.add_edge( pname, port._value.name)
        #dag.add_edge( port._value.name, port._value._value )
      else:
        dag.add_edge( pname, port._value )
      for c in port.connections:
        if c.parent:
          cname = "{0}.{1}".format( c.parent.name, c.name )
        else:
          cname = c.name
        dag.add_edge( pname, cname, style='dashed' )
        if isinstance(c, VerilogSlice):
          dag.add_edge( cname, c._value )
      #  if isinstance(c, VerilogSlice):
      #    for x in c.connections:
      #      if x.parent:
      #        xname = "{0}.{1}".format( x.parent.name, x.name )
      #      else:
      #        xname = x.name
      #      dag.add_edge( cname, xname )


  def dump_graphviz(self):
    """Temporary utility method to dump out a graphviz plot."""
    #print dag.string()
    dag.layout(prog='dot')
    # layout types: neato dot twopi circo fdp nop
    dag.draw('test.png')


  def infer_sensitivity_list(self, model):
    """Utility method which detects the sensitivity list of annotated functions.

    This method uses the SensitivityListVisitor class to walk the AST of the
    provided model and register any functions annotated with special
    decorators.

    For @combinational decorators, the SensitivityListVisitor attempts to
    construct a signal sensitivity list based on loads performed inside the
    annotated function.

    For @posedge_clk decorators, the SensitivityListVisitor replaces the
    ValueNodes of written ports/wires with RegisterNodes.

    Parameters
    ----------
    model: a VerilogModel instance
    """

    # Create an AST Tree
    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    comb_loads = set()
    reg_stores = set()

    # Walk the tree to inspect a given modules combinational blocks and
    # build a sensitivity list from it,
    # only gives us function names... still need function pointers
    SensitivityListVisitor( comb_loads, reg_stores ).visit( tree )
    #print "COMB", comb_loads
    #print "REGS", reg_stores

    # Iterate through all comb_loads, add function_pointers to vnode_callbacks
    for port_name, func_name in comb_loads:
      port_ptr = model.__getattribute__(port_name)
      func_ptr = model.__getattribute__(func_name)
      value_ptr = port_ptr._value
      if isinstance(value_ptr, VerilogSlice):
        value_ptr = value_ptr._value
      #print value_ptr
      # TODO: use a defaultdict here?
      # Initialize value_ptr entry to [] if not in callback list yet
      if value_ptr not in self.vnode_callbacks:
        self.vnode_callbacks[value_ptr] = []
      self.vnode_callbacks[value_ptr] += [func_ptr]

    # Iterate through all reg_stores, replace all instances of ValueNodes
    # with RegisterNodes. This could be tricky!
    for port_name, func_name in reg_stores:
      port_ptr = model.__getattribute__(port_name)
      func_ptr = model.__getattribute__(func_name)
      # Add the @posedge_clk function to the callback list
      self.posedge_clk_fns += [func_ptr]
      # TODO: special case for slices
      # Create a RegisterNode object to replace the ValueNode
      value_node = port_ptr._value
      register_node = RegisterNode( value_node.width, sim=self )
      for group in self.node_groups:
        if port_ptr in group:
          for port in group:
            #print port.parent.name, port.name, type(port._value)
            if not isinstance(port._value, VerilogSlice):
              port._value = register_node
            else:
              # TODO: needs testing!
              print "TEST ME!!!!"
      # Add the register node to the callback list
      self.rnode_callbacks += [register_node]

    for m in model.submodules:
      self.infer_sensitivity_list( m )

class SensitivityListVisitor(ast.NodeVisitor):
  """Hidden class for building a sensitivity list from the AST of a MTL model.

  This class takes the AST tree of a VerilogModule class and looks for any
  functions annotated with the @combinational decorator. Variables that perform
  loads in these functions are added to the sensitivity list (registry).
  """
  # http://docs.python.org/library/ast.html#abstract-grammar
  def __init__(self, comb_loads, reg_stores):
    """Construct a new SensitivityListVisitor.

    Parameters
    ----------
    comb_loads: a set() object, (var_name, func_name) tuples will be added to
                this set for all variables loaded inside @combinational blocks
    reg_stores: a set() object, (var_name, func_name) tuples will be added to
                this set for all variables updated inside @posedge_clk blocks
                (via the <<= operator)
    """
    self.current_fn = None
    self.comb_loads = comb_loads
    self.reg_stores = reg_stores
    self.add_regs   = False

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    #pprint.pprint( dir(node) )
    #print "Function Name:", node.name
    if not node.decorator_list:
      return
    decorator_names = [x.id for x in node.decorator_list]
    self.current_fn = node.name
    if 'combinational' in decorator_names:
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.visit(x)
    elif 'posedge_clk' in decorator_names:
      # Visit each line in the function, translate one at a time.
      self.add_regs = True
      for x in node.body:
        self.visit(x)
      self.add_regs = False
    self.current_fn = None

  def visit_AugAssign(self, node):
    """Visit all aug assigns, searches for synchronous (registered) stores."""
    # @posedge_clk annotation, find nodes we need toconvert to registers
    if self.add_regs and isinstance(node.op, _ast.LShift):
      self.reg_stores.add( (node.target.id, self.current_fn) )
    else:
      self.generic_visit(node)

  # All attributes... only want names?
  #def visit_Attribute(self, node):
  def visit_Name(self, node):
    """Visit all variables, searches for combinational loads."""
    #pprint.pprint( dir(node.ctx) )
    #print node.id, type( node.ctx )
    # Function with no annotations
    if not self.current_fn or self.add_regs:
      return
    # @combinational annotation, find nodes to add to the sensitivity list
    elif (not self.add_regs
          and isinstance( node.ctx, _ast.Load )
          and node.id != "self"):
      #print node.id, type( node.ctx )
      self.comb_loads.add( (node.id, self.current_fn) )



# Decorators

def combinational(func):
  # Normally a decorator returns a wrapped function, but here we return
  # func unmodified.  We only use the decorator as a flag for the ast
  # parsers.
  return func

def posedge_clk(func):
  return func

