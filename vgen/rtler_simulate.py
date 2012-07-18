from collections import deque
import ast, _ast
import pprint

class LogicSim():

  def __init__(self):
    self.num_cycles     = 0
    self.port_callbacks = {}
    self.event_queue    = deque()

  def cycle(self):
    self.num_cycles += 1
    while self.event_queue:
      func = self.event_queue.pop()
      func()

  def add_callback(self, port, func):
    # TODO: doesnt' work in __init__ because ValueNodes are not
    #       created until elaborate!
    #node = port._value
    #print "ADDCALLBACK:", port.name, node
    ## TODO: might need to support multiple funcs?
    #self.port_callbacks[node] = func
    port.funcs.add( func )

  def add_event(self, port, connections):
    node = port._value
    for func in node.funcs:
      if func not in self.event_queue:
        #print "ADDEVENT:", port.parent, port.name, port.value, func
        self.event_queue.appendleft(func)

  def generate(self, model):
    #print "Model:", model
    #print "Submodules:"
    #pprint.pprint( model.submodules )

    self.infer_sensitivity_list( model )

    for m in model.submodules:
      # TODO: make recursive
      #self.generate( m )
      self.infer_sensitivity_list( m )


  def infer_sensitivity_list(self, model):

    # Create an AST Tree
    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    temp_registry = set()

    # Walk the tree to inspect a given modules combinational blocks and
    # build a sensitivity list from it
    SensitivityListVisitor( temp_registry ).visit( tree )

    # TODO: only gives us function names... still need function pointers
    print temp_registry
    for port_name, func_name in temp_registry:
      port_ptr = model.__getattribute__(port_name)
      func_ptr = model.__getattribute__(func_name)
      self.port_callbacks[port_ptr] = func_ptr
      #print port_ptr, func_ptr
    pprint.pprint( self.port_callbacks )



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
    if 'always_comb' in decorator_names:
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
  # normally a decorator returns a wrapped function,
  # but here we return func unmodified, after registering it
  return func

import inspect
def always_comb(fn):
  def wrapped(self):
    #for x,y in inspect.getmembers(fn, inspect.isdatadescriptor):
    #  print x,y
    return fn(self)
  return wrapped

