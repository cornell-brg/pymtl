from collections import deque
import ast, _ast
import pprint
# TODO: cyclic dependency...
import rtler_vbase

class LogicSim():

  def __init__(self):
    self.num_cycles     = 0
    self.port_callbacks = {}
    self.event_queue    = deque()
    self.TESTevent_queue= deque()

  def cycle(self):
    self.num_cycles += 1

    while self.TESTevent_queue:
      func = self.TESTevent_queue.pop()
      func()

    #while self.event_queue:
    #  func = self.event_queue.pop()
    #  func()

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
        #print "#ADDEVENT:", port.parent, port.name, port.value, func
        self.event_queue.appendleft(func)

  def TESTadd_event(self, value_node):
    # ALTERNATE
    print "    ADDEVENT: VALUE", value_node, value_node.value, value_node in self.port_callbacks
    if value_node in self.port_callbacks:
      funcs = self.port_callbacks[value_node]
      for func in funcs:
        if func not in self.TESTevent_queue:
          self.TESTevent_queue.appendleft(func)
      #if funcs not in self.TESTevent_queue:
      #  self.TESTevent_queue.appendleft(funcs)



  def generate(self, model):
    #print "Model:", model
    #print "Submodules:"
    #pprint.pprint( model.submodules )

    self.infer_sensitivity_list( model )

    for m in model.submodules:
      # TODO: make recursive
      #self.generate( m )
      self.infer_sensitivity_list( m )
    print "PORTCALLBACKS"
    pprint.pprint( self.port_callbacks )


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
    #print temp_registry
    for port_name, func_name in temp_registry:
      port_ptr = model.__getattribute__(port_name)
      func_ptr = model.__getattribute__(func_name)
      value_ptr = port_ptr._value
      if isinstance(value_ptr, rtler_vbase.VerilogSlice):
        value_ptr = value_ptr._value
      print value_ptr
      if value_ptr in self.port_callbacks:
        self.port_callbacks[value_ptr] += [func_ptr]
      else:
        self.port_callbacks[value_ptr] = [func_ptr]
      #for connected_port in port_ptr.connection:
      #  self.port_callbacks[connected_port] = func_ptr
      #print port_ptr, func_ptr


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

