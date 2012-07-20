from collections import deque
import ast, _ast
import inspect
import pprint
# TODO: cyclic dependency...
import rtler_vbase

# TODO: make commandline parameter
debug_hierarchy = True

class LogicSim():

  def __init__(self, model):
    self.model = model
    self.num_cycles     = 0
    self.vnode_callbacks = {}
    self.event_queue    = deque()

  def cycle(self):
    self.num_cycles += 1

    while self.event_queue:
      func = self.event_queue.pop()
      func()

  def add_event(self, value_node):
    # TODO: debug_event
    #print "    ADDEVENT: VALUE", value_node, value_node.value, value_node in self.vnode_callbacks
    if value_node in self.vnode_callbacks:
      funcs = self.vnode_callbacks[value_node]
      for func in funcs:
        if func not in self.event_queue:
          self.event_queue.appendleft(func)

  def generate(self, model=None):
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
      # TODO: make recursive
      self.generate( m )
      #self.infer_sensitivity_list( m )
    # TODO: debug_sensitivity_list
    #print "VALUE NODE CALLBACKS"
    #pprint.pprint( self.vnode_callbacks )


  def infer_sensitivity_list(self, model):

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
      if isinstance(value_ptr, rtler_vbase.VerilogSlice):
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
  # http://docs.python.org/library/ast.html#abstract-grammar
  def __init__(self, registry):
    self.current_fn = None
    self.registry   = registry

  def visit_FunctionDef(self, node):
    """ Only parse functions that have the @... decorator! """
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

