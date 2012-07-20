"""Tool for simulating MTL models.

This module contains classes which construct a simulator given a MTL model
for execution in the python interpreter.
"""

from collections import deque
import ast, _ast
import inspect
import pprint
from rtler_vbase import VerilogSlice

# TODO: make commandline parameter
debug_hierarchy = True

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
    self.num_cycles     = 0
    self.vnode_callbacks = {}
    self.event_queue    = deque()

  def cycle(self):
    """Execute a single cycle in the simulator.

    Executes any functions in the event queue and increments the num_cycles
    count.

    TODO: execute all @posedge, @negedge decorated functions.
    """
    while self.event_queue:
      func = self.event_queue.pop()
      func()
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

  def generate(self, model=None):
    """Construct a simulator for the provided model by adding necessary hooks.

    Parameters
    ----------
    model: the MTL model (VerilogModule) to add simulator hooks to. If None is
           provided, the model provided in the LogicSim constructor is used
           (toplevel).
    """
    #TODO: hacky... first call to generate should use toplevel model
    model = model if model else self.model
    if debug_hierarchy:
      print 70*'-'
      print "Model:", model
      print "Ports:"
      pprint.pprint( model.ports, indent=3 )
      print "Submodules:"
      pprint.pprint( model.submodules, indent=3 )

    self.infer_sensitivity_list( model )

    for m in model.submodules:
      self.generate( m )

    # TODO: debug_sensitivity_list
    #print "VALUE NODE CALLBACKS"
    #pprint.pprint( self.vnode_callbacks )

  def infer_sensitivity_list(self, model):
    """Utility method which detects the sensitivity list of annotated functions.

    This method uses the SensitivityListVisitor class to walk the AST of the
    provided model and register any functions annotated with the @combinational
    decorator. The SensitivityListVisitor attempts to construct a signal
    sensitivity list based on accesses in the annotated function.

    Parameters
    ----------
    model: a VerilogModel instance
    """

    # Create an AST Tree
    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    temp_registry = set()

    # Walk the tree to inspect a given modules combinational blocks and
    # build a sensitivity list from it,
    # only gives us function names... still need function pointers
    SensitivityListVisitor( temp_registry ).visit( tree )

    # Get the function pointers here
    # TODO: debug_sensitivity_list
    for port_name, func_name in temp_registry:
      port_ptr = model.__getattribute__(port_name)
      func_ptr = model.__getattribute__(func_name)
      value_ptr = port_ptr._value
      if isinstance(value_ptr, VerilogSlice):
        value_ptr = value_ptr._value
      #print value_ptr
      # TODO: use a defaultdict here?
      if value_ptr in self.vnode_callbacks:
        self.vnode_callbacks[value_ptr] += [func_ptr]
      else:
        #TODO: hacky! Adding simulator instance to Nodes here...
        value_ptr.sim = self
        self.vnode_callbacks[value_ptr] = [func_ptr]


class SensitivityListVisitor(ast.NodeVisitor):
  """Hidden class for building a sensitivity list from the AST of a MTL model.

  This class takes the AST tree of a VerilogModule class and looks for any
  functions annotated with the @combinational decorator. Variables that perform
  loads in these functions are added to the sensitivity list (registry).
  """
  # http://docs.python.org/library/ast.html#abstract-grammar
  def __init__(self, registry):
    """Construct a new SensitivityListVisitor.

    Parameters
    ----------
    registry: a set() object with which to add variable names to.
    """
    self.current_fn = None
    self.registry   = registry

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    #pprint.pprint( dir(node) )
    #print "Function Name:", node.name
    if not node.decorator_list:
      return
    decorator_names = [x.id for x in node.decorator_list]
    if 'combinational' in decorator_names:
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.current_fn = node.name
        self.visit(x)
        self.current_fn = None

  # All attributes... only want names?
  #def visit_Attribute(self, node):
  def visit_Name(self, node):
    """Visit all variables, add those that perform loads to the registry."""
    #pprint.pprint( dir(node.ctx) )
    #print node.id, type( node.ctx )
    if not self.current_fn:
      return
    if isinstance( node.ctx, _ast.Load ) and node.id != "self":
      #print node.id, type( node.ctx )
      self.registry.add( (node.id, self.current_fn) )



# Decorators

def combinational(func):
  # Normally a decorator returns a wrapped function, but here we return
  # func unmodified.  We only use the decorator as a flag for the ast
  # parsers.
  return func

